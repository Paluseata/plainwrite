plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "app.plainwrite"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.plainwrite"
        // Android 5.0 (2014) and newer. The web engine is what really limits old devices: Plainwrite needs a
        // Chromium 60+ WebView, built into Android 8+ and reachable on 5.0–7.x with one Play Store update.
        minSdk = 21
        targetSdk = 34
        versionCode = 108
        versionName = "1.08"
    }

    // Two editions, like the web download: Build Variants panel → englishDebug / multilingualDebug
    flavorDimensions += "edition"
    productFlavors {
        create("english") {
            dimension = "edition"
            resValue("string", "app_name", "Plainwrite")
        }
        create("multilingual") {
            dimension = "edition"
            applicationIdSuffix = ".multilingual"          // can be installed next to the English one
            versionNameSuffix = "-multilingual"
            resValue("string", "app_name", "Plainwrite")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-ktx:1.9.2")
    implementation("androidx.webkit:webkit:1.11.0")
}
