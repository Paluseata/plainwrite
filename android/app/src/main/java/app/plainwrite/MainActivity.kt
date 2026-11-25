package app.plainwrite

import android.annotation.SuppressLint
import android.app.ActivityManager
import android.app.AlertDialog
import android.content.Intent
import android.content.IntentFilter
import android.net.Uri
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.view.WindowManager
import android.webkit.WebView
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewClientCompat
import androidx.webkit.WebViewCompat
import org.json.JSONObject

/**
 * Plainwrite as an Android app: a full-window WebView showing the web app bundled in assets/www.
 *
 * The page is served from https://appassets.androidplatform.net/assets/www/ (WebViewAssetLoader), a real
 * https origin, so localStorage and IndexedDB (your files, settings, fonts, language packs) work and persist.
 * window.PlainwriteAndroid gives the page what a WebView lacks on its own: saving .txt files,
 * immersive full screen, focus mode (app pinning) and the battery level. The Back key works like Esc.
 */
class MainActivity : ComponentActivity() {
    private lateinit var web: WebView
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var pendingSave: Pair<String, String>? = null   // file name, text

    // <input type=file> (import font, language pack, key sound)
    private val pickFiles = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val cb = fileCallback
        fileCallback = null
        cb?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(r.resultCode, r.data))
    }

    // Send → Save as text file: the system "save as" screen (Downloads, Drive, …)
    private val createDoc = registerForActivityResult(ActivityResultContracts.CreateDocument("text/plain")) { uri ->
        val p = pendingSave
        pendingSave = null
        var ok = false
        if (uri != null && p != null) {
            ok = runCatching {
                contentResolver.openOutputStream(uri)?.use { it.write(p.second.toByteArray(Charsets.UTF_8)) }
            }.isSuccess
        }
        web.evaluateJavascript("window.plainwriteSaved&&plainwriteSaved($ok,${JSONObject.quote(p?.first ?: "")})", null)
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)   // chrome://inspect while testing

        web = WebView(this)
        web.setBackgroundColor(0xFF121417.toInt())
        setContentView(web)

        val assets = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        with(web.settings) {
            javaScriptEnabled = true
            domStorageEnabled = true                  // localStorage: your files and settings
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false  // key sounds
            allowFileAccess = false
            allowContentAccess = false
            textZoom = 100                            // ignore the system font-size setting; the LCD sizes itself
        }

        web.webViewClient = object : WebViewClientCompat() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? =
                assets.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                if (request.url.host == "appassets.androidplatform.net") return false
                runCatching { startActivity(Intent(Intent.ACTION_VIEW, request.url)) }   // other links open in the browser
                return true
            }
        }

        web.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(view: WebView, callback: ValueCallback<Array<Uri>>, params: FileChooserParams): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = callback
                return try {
                    pickFiles.launch(params.createIntent()); true
                } catch (e: Exception) {
                    fileCallback = null; false
                }
            }
        }

        web.addJavascriptInterface(Bridge(), "PlainwriteAndroid")

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                web.evaluateJavascript("window.plainwriteBack?plainwriteBack():'exit'") { r ->
                    if (r == "\"exit\"") moveTaskToBack(true)
                }
            }
        })

        if (savedInstanceState == null) web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")
        else web.restoreState(savedInstanceState)

        if (savedInstanceState == null) checkWebViewVersion()
    }

    /**
     * Plainwrite needs a Chromium 60+ WebView. Android 8 and 9 have one built in; on Android 5.0–7.x the
     * factory WebView is older (37–52), but one update from the Play Store fixes it (to Chromium 95 on
     * Android 5, 106 on 6, 119 on 7). This offers the update instead of showing a broken page.
     */
    private fun checkWebViewVersion() {
        val pkg = runCatching { WebViewCompat.getCurrentWebViewPackage(this) }.getOrNull() ?: return
        val major = pkg.versionName?.substringBefore('.')?.toIntOrNull() ?: return
        if (major >= MIN_CHROMIUM) return
        val app = if (pkg.packageName.contains("chrome")) "Chrome" else "Android System WebView"
        AlertDialog.Builder(this)
            .setTitle("Update needed")
            .setMessage("Plainwrite runs on $app, which is version $major here. It needs version $MIN_CHROMIUM or newer. Update $app, then open Plainwrite again.")
            .setPositiveButton("Update") { _, _ ->
                val market = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=${pkg.packageName}"))
                val site = Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=${pkg.packageName}"))
                runCatching { startActivity(market) }.onFailure { runCatching { startActivity(site) } }
            }
            .setNegativeButton("Not now", null)
            .show()
    }

    companion object { const val MIN_CHROMIUM = 60 }

    /** Focus mode: Android's app pinning, with the system bars hidden and the screen kept on. */
    @Suppress("DEPRECATION")
    private fun focusOn(): Boolean {
        val am = getSystemService(ACTIVITY_SERVICE) as ActivityManager
        return if (Build.VERSION.SDK_INT >= 23) am.lockTaskModeState != ActivityManager.LOCK_TASK_MODE_NONE
        else am.isInLockTaskMode
    }

    private fun setFocus(on: Boolean) {
        val c = WindowCompat.getInsetsController(window, web)
        if (on) {
            runCatching { startLockTask() }          // Android asks once whether to pin the app
            c.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            c.hide(WindowInsetsCompat.Type.systemBars())
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        } else {
            runCatching { stopLockTask() }
            window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }
    }

    // unpinned with Android's own gesture: keep the screen-on flag and the page's Control Panel in step
    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (!hasFocus) return
        val on = focusOn()
        if (!on) window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        web.evaluateJavascript("window.plainwriteFocus&&plainwriteFocus($on)", null)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    /** Called from the page as window.PlainwriteAndroid.* (always on a background thread). */
    inner class Bridge {
        @JavascriptInterface
        fun saveText(name: String, text: String) = runOnUiThread {
            pendingSave = name to text
            createDoc.launch(name)
        }

        @JavascriptInterface
        fun setFullscreen(on: Boolean) = runOnUiThread {
            val c = WindowCompat.getInsetsController(window, web)
            if (on) {
                c.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                c.hide(WindowInsetsCompat.Type.systemBars())
            } else {
                c.show(WindowInsetsCompat.Type.systemBars())
            }
        }

        @JavascriptInterface
        fun setFocus(on: Boolean) = runOnUiThread { this@MainActivity.setFocus(on) }

        @JavascriptInterface
        fun focusOn(): Boolean = this@MainActivity.focusOn()

        @JavascriptInterface
        fun battery(): String {
            val i = registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            val level = i?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = i?.getIntExtra(BatteryManager.EXTRA_SCALE, 100) ?: 100
            val status = i?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
            val charging = status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL
            return JSONObject()
                .put("level", if (level >= 0 && scale > 0) level.toDouble() / scale else -1.0)
                .put("charging", charging)
                .toString()
        }
    }
}
