#!/usr/bin/env python3
"""Builds Plainwrite-J from a Plainwrite release (../pw-src: index.html, sw.js, fonts, icons).

Two editions:
  dist/ja     Japanese (monolingual): Japanese menus only
  dist/en-ja  English-Japanese (bilingual): English and Japanese menus, picked from the system language
Both have the Japanese input method (ime.js), Pixel Gothic J as the default font and dict-ja.txt.
Plainwrite-J keeps its own storage keys, so it never touches a Plainwrite install's files.
"""
import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'pw-src4')
VER = '0.7.4'
BUILD = 2   # bump for a rebuild that keeps the version number

def jsstr(d):
    return '{' + ','.join(f'{k}:{json.dumps(v, ensure_ascii=False)}' for k, v in d.items()) + '}'

def load_strings():
    out = subprocess.check_output(['node', '-e', f"const m=require({json.dumps(os.path.join(HERE,'ja_strings.js'))});"
                                   "const en=m.en;delete m.en;process.stdout.write(JSON.stringify({ja:m,en}))"])
    return json.loads(out)

FAILS=[]
def widen_ja(d):
    # digits and % in the Japanese text itself become full-width too; {0} placeholders stay as they are
    return {k: re.sub(r'\{\d\}|[0-9%]', lambda m: m.group(0) if len(m.group(0)) > 1 else chr(ord(m.group(0)) + 0xfee0), v) for k, v in d.items()}

def build(edition):
    h = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
    def R(a, b, n=1):
        nonlocal h
        c = h.count(a)
        if c != n: FAILS.append((a[:150], c)); return
        h = h.replace(a, b)
    S = load_strings()
    mono = edition == 'ja'
    ed_name = '日本語版' if mono else 'English–Japanese'

    # ---- names, titles, storage ----
    R('<html lang="en">', f'<html lang="{"ja" if mono else "en"}">')
    R('<title>Plainwrite</title>', '<title>Plainwrite-J</title>')
    R('content="Plainwrite">', 'content="Plainwrite-J">', 2)
    R("const KEY='neo-sim-v1';", "const KEY='plainwrite-j-v1';")
    R("'plainwrite-cover-v3'", "'plainwrite-j-cover-v3'")
    R("'plainwrite-langs-v1'", "'plainwrite-j-langs-v1'")
    R("indexedDB.open('plainwrite-fonts',1)", "indexedDB.open('plainwrite-j-fonts',1)")
    R("indexedDB.open('plainwrite-sound',1)", "indexedDB.open('plainwrite-j-sound',1)")
    R('`Plainwrite File ${S.active+1}.txt`', '`Plainwrite-J File ${S.active+1}.txt`', 2)
    # wordmark: "plainwrite" plus a J (CSS, so the logo's text nodes stay as they were)
    R('.logo b{font-weight:600}', '.logo b{font-weight:600}\n@font-face{font-family:"Plainwrite J";src:url("logo-j.woff") format("woff");font-weight:700;font-display:block}\n'
      '.logo::after{content:"J";font-family:"Plainwrite J",Georgia,"Times New Roman",serif;font-weight:700;margin-left:.1em;letter-spacing:0}')
    # version: the Plainwrite release it's built on, then Plainwrite-J's own (half-width digits in both editions)
    main_ver = re.search(r"const APP_VER='Version ([0-9.]+) \(Multilingual\)';", h).group(1)
    h = re.sub(r"const APP_VER='Version [0-9.]+ \(Multilingual\)';", "const APP_VER='@@VER@@';", h, count=1)
    R("const APP_VER='@@VER@@';",
      f"const APP_VER={json.dumps(('ﾊﾞｰｼﾞｮﾝ'+main_ver+'／'+VER+'J（'+ed_name+'）') if mono else ('Version '+main_ver+'/'+VER+'J ('+ed_name+')'), ensure_ascii=False)};")
    R("const n=APP_VER.match(/\\d[\\d.]*/);v.textContent=n?'v'+n[0]:'dev';", "v.textContent=" + json.dumps('v' + VER + 'J') + ";")
    # the About screen: about-ja.txt (Japanese edition) and about-en-ja.txt (English–Japanese edition).
    # One line per screen line; ${APP_VER} becomes the version. Edit them freely and rebuild.
    about = open(os.path.join(HERE, 'about-ja.txt' if mono else 'about-en-ja.txt'), encoding='utf-8').read().rstrip('\n').replace('`', "'")
    i = h.index('const ABOUT_TEXT=`'); j = h.index('`;', i)
    h = h[:i] + '// Plainwrite-J: also in about-ja.txt / about-en-ja.txt in the source folder (rebuilding uses those).\nconst ABOUT_TEXT=`' + about + h[j:]

    # ---- menu languages ----
    h = re.sub(r"const LANGS=\[\{id:'en',name:'English \(US\)'\}.*?\];", "const LANGS=@@LANGS@@;", h, count=1, flags=re.S)
    R("const LANGS=@@LANGS@@;", "const LANGS=[{id:'ja',name:'日本語'}];" if mono else "const LANGS=[{id:'en',name:'English'},{id:'ja',name:'日本語'}];")
    R("function t(key,...a){const d=I18N[S.lang]||I18N.en;",
      "function t(key,...a){const d=I18N[S.lang]||I18N.en;"
      "if(S.lang==='ja'){if(/^tutor_(speed|line_done|live)$/.test(key)&&a[0]!=null)a[0]=Math.round(a[0]*5);   // 字/分: five characters to a word\n"
      "  a=a.map(x=>typeof x==='number'||/^\\d+([.,]\\d+)?%?$/.test(String(x))?String(x).replace(/[0-9%.,]/g,c=>String.fromCharCode(c.charCodeAt(0)+0xfee0)):x)}")
    R("// English variants: only the strings that differ from US English",
      "Object.assign(I18N.en," + jsstr(S['en']) + ");\nI18N.ja=" + jsstr(widen_ja(S['ja'])) + ";\n// English variants: only the strings that differ from US English")
    R("const BUNDLE='langs/all.json';", "const BUNDLE=null;")
    # default language: Japanese edition always Japanese; bilingual follows the system
    R("function pickLocale(){", "function pickLocale(){" + ("return'ja';" if mono else
      "{const p=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'en']).map(s=>String(s).toLowerCase());return p.some(x=>x.split('-')[0]==='ja')?'ja':'en'}"))
    if mono:
        R("    {id:'langs',label:t('cp_langs')},\n", "")
    # first start: no keyboard-layout question (Japanese input is set up in the Control Panel)
    R("autoOff:10,powerOn:'power',", "autoOff:10,powerOn:'power',setupDone:true,imeOn:true,imeMode:'hira',imeKana:'romaji',")
    if mono:
        welcome = ("Plainwrite-J へようこそ。静かな小さいワープロです。\n画面をタップして打ち始めてください。ローマ字で打って Space で変換、Enter で確定します。"
                   "変換の候補は一番下の行に出ます。\n上のバーの「あ」で入力モードを切り替え、applets キーで電卓やゲーム、Aa で書体を変えられます。")
    else:
        welcome = ("Welcome to Plainwrite-J, a quiet little word processor that writes Japanese too.\n"
                   "Type romaji, press Space to convert to kanji and Enter to take it; the choices show on the bottom line. "
                   "The あ badge at the top switches Japanese on and off.\n"
                   "Plainwrite-J へようこそ。ローマ字で打って Space で変換、Enter で確定。候補は一番下の行に出ます。")
    i = h.index('const WELCOME="'); j = h.index('";', i)
    h = h[:i] + 'const WELCOME=' + json.dumps(welcome, ensure_ascii=False) + h[j + 1:]

    # ---- fonts: Pixel Gothic J first and default; everything else borrows Japanese from it ----
    R('<link rel="preload" href="plain-sans.ttf" as="font" type="font/ttf" crossorigin>',
      '<link rel="preload" href="pixel-gothic.ttf" as="font" type="font/ttf" crossorigin>\n<link rel="preload" href="plain-sans.ttf" as="font" type="font/ttf" crossorigin>')
    R("""  {name:'Plain Sans',langs:'ru uk be bg sr kk ky mn tg el',css:'"Plain Sans"',pixel:10},
  {name:'Pixel Gothic',langs:'ru uk be bg sr kk ky mn tg',css:'"Pixel Gothic"',pixel:16,fb:'"Plain Sans",'},""",
      """  {name:'Pixel Gothic',langs:'ru uk be bg sr kk ky mn tg',css:'"Pixel Gothic"',pixel:16,fb:'"Plain Sans",'},
  {name:'Plain Sans',langs:'ru uk be bg sr kk ky mn tg el',css:'"Plain Sans"',pixel:10,fb:'"Pixel Gothic",'},""")
    for name, css in [('Home Computer', '"Home Computer"'), ('Home Computer Thin', '"Home Computer Thin"')]:
        R(f"{{name:'{name}',langs:'ru uk be bg sr kk ky mn tg el',css:'{css}',pixel:10}}",
          f"{{name:'{name}',langs:'ru uk be bg sr kk ky mn tg el',css:'{css}',pixel:10,fb:'\"Pixel Gothic\",'}}")
    R("""{name:'Modern Mono',langs:'ru uk be bg sr kk ky mn',css:'"IBM Plex Mono"'}""",
      """{name:'Modern Mono',langs:'ru uk be bg sr kk ky mn',css:'"IBM Plex Mono"',fb:'"Pixel Gothic",'}""")
    # every other font borrows Japanese letters from Pixel Gothic
    for a in ['"Plain Sans"', '"Home Computer"', '"IBM Plex Mono"']:
        h = h.replace("fb:'" + a + ",'}", "fb:'\"Pixel Gothic\"," + a + ",'}")
    R("face:0,faceName:'Plain Sans',", "face:0,faceName:'Pixel Gothic',")
    R("const FACE_FALLBACK=['Teletext','Modern Mono','Arcade','Tiny Pixel','Pixel Gothic','Teletext Narrow'];",
      "const FACE_FALLBACK=['Pixel Gothic','Teletext','Modern Mono','Arcade','Tiny Pixel','Teletext Narrow'];")
    R("let firstBoot=false;", "let firstBoot=false;")
    # monospace spacing: Japanese letters take two cells
    R("  if(spacingMode()==='mono')g={w:cellW,ti:(cellW-n)/2};",
      "  if(spacingMode()==='mono'){const c=isWide(ch)?2*cellW:cellW;g={w:c,ti:(c-n)/2}}")
    R("function G(ch){", "const isWide=ch=>/[\\u1100-\\u115f\\u2e80-\\u303e\\u3041-\\u33ff\\u3400-\\u4dbf\\u4e00-\\u9fff\\ua960-\\ua97f\\uac00-\\ud7a3\\uf900-\\ufaff\\ufe30-\\ufe4f\\uff00-\\uff60\\uffe0-\\uffe6]/.test(ch);\nfunction G(ch){")
    # ---- Wide letters (全角表示): the writer draws Latin, digits and signs as their full-width forms, and
    #      Russian Cyrillic with Pixel Gothic's wide JIS shapes (kept at U+E401–U+E451 by merge_font.py). Display only.
    R("function W(ch){return spacingMode()==='auto'?W0(ch):G(ch).w}",
      "function W(ch){return spacingMode()==='auto'?W0(ch):G(ch).w}\n"
      "function dispCh(ch){if(!S.wideDisp||mode!=='word')return ch;const c=ch.charCodeAt(0);if(c>0x20&&c<0x7f)return String.fromCharCode(c+0xfee0);"
      "if(c===0x20)return'\\u3000';if((c>=0x410&&c<=0x44f)||c===0x401||c===0x451)return String.fromCharCode(0xe000+c);return ch}\n"
      "const WT=ch=>W(dispCh(ch));")
    R("function posAtX(text,L,x){let w=0;for(let p=L.s;p<L.e;p++){const cw=W(text[p]);", "function posAtX(text,L,x){let w=0;for(let p=L.s;p<L.e;p++){const cw=WT(text[p]);")
    R("for(let p=L.s;p<end;p++){const cw=W(v[p]);", "for(let p=L.s;p<end;p++){const cw=WT(v[p]);")
    R("goalX=textW(ta.value.slice(lines[li].s,c))", "goalX=[...ta.value.slice(lines[li].s,c)].reduce((w,ch)=>w+WT(ch),0)")
    R("function wrap(text){const lines=[]", "function wrap(text){const wt=text===ta.value,lines=[]")
    R("    for(let p=L.s;p<L.e;p++){const ch=text[p];", "    for(let p=L.s;p<L.e;p++){const ch=dispCh(text[p]);")
    R("    case 'blink':S.blink=!S.blink;save();break;", "    case 'blink':S.blink=!S.blink;save();break;\n    case 'widedisp':S.wideDisp=!S.wideDisp;save();break;")
    # ---- wrapping: Japanese breaks between any two letters; 、。」 and small kana never start a line ----
    R("""    while(s<pend){let w=0,lastSp=-1,i=s;
      for(;i<pend;i++){const ch=text[i],cw=W(ch);
        if(ch===' '){lastSp=i;w+=cw;continue}           // spaces may hang past the edge, never force a break
        if(w+cw>maxW&&i>s)break;w+=cw}""",
      """    while(s<pend){let w=0,lastSp=-1,i=s;
      for(;i<pend;i++){const ch=text[i],cw=wt?WT(ch):W(ch);
        if(ch===' '||ch==='\\u3000'){lastSp=i;w+=cw;continue}           // spaces may hang past the edge, never force a break
        if(w+cw>maxW&&i>s){
          // Japanese: 、。」 and small kana never start a line, so the letter before them comes down too
          if(NOSTART.includes(ch)){if(i-1>s&&isWide(text[i-1])&&!NOSTART.includes(text[i-1]))lastSp=i-2}
          else if((isWide(ch)||isWide(text[i-1]))&&!NOEND.includes(text[i-1]))lastSp=i-1;
          break}
        if(i>s&&(isWide(ch)||isWide(text[i-1]))&&!NOSTART.includes(ch)&&!NOEND.includes(text[i-1]))lastSp=i-1;   // a Japanese line may break before any letter
        w+=cw}""")
    R("function wrap(text){", "const NOSTART='、。，．・：；？！ー」』）】〉》〕｝ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ…‥々゛゜',NOEND='「『（【〈《〔｛';\nfunction wrap(text){")
    # ---- drawing: the composition is underlined, the part being converted reversed; candidates on the bottom line ----
    R("""      if(p===c&&a===b&&li===i)h+=curSpan(ch);
      else if(p>=a&&p<b)h+='<span class="inv">'+esc(ch)+'</span>';
      else h+=esc(ch)}
    if(li===i&&a===b&&c>=L.e)h+=curSpan(' ');""",
      """      const ic=imeCls(p);
      if(p===c&&a===b&&li===i&&!imeBar())h+=curSpan(ch);
      else if(p>=a&&p<b)h+='<span class="inv">'+esc(ch)+'</span>';
      else if(ic)h+='<span class="'+ic+'">'+esc(ch)+'</span>';
      else h+=esc(ch)}
    if(li===i&&a===b&&c>=L.e&&!imeBar())h+=curSpan(' ');""")
    R("""      const ml=msg?wrap(msg,FONTS[S.font].cols).slice(0,Math.max(1,n-1)).map(L=>msg.slice(L.s,L.e).trim()):[];
      rows=wordRows(n-ml.length);for(const l of ml)rows.push(invRow(l));break}""",
      """      if(imeBar()&&n>1){rows=wordRows(n-1);rows.push(candRow());break}
      const ml=msg?wrap(msg,FONTS[S.font].cols).slice(0,Math.max(1,n-1)).map(L=>msg.slice(L.s,L.e).trim()):[];
      rows=wordRows(n-ml.length);for(const l of ml)rows.push(invRow(l));break}""")
    R(".cur{display:inline-block;min-width:.4em}",
      ".cur{display:inline-block;min-width:.4em}\n"
      ".pre{box-shadow:inset 0 calc(-1*max(1px,.07em)) var(--ink)}\n"
      ".pre.seg{background:var(--ink);color:var(--lcd);box-shadow:none}\n"
      ".inv .csel{background:var(--lcd);color:var(--ink)}\n"
      ".imebtn{min-width:22px;height:20px;border-radius:5px;border:1.5px solid var(--brand);background:transparent;color:var(--brandb);"
      "font:700 12px/1 \"M PLUS 1p J\",system-ui,sans-serif;padding:0 3px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;letter-spacing:0}\n"
      ".imebtn.off{opacity:.7}.imebtn:hover{border-color:#c2c8cf;color:#e3e6ea}")
    R('<span class="status"><button class="infobtn" id="helpBtn"',
      '<span class="status"><button class="imebtn" id="imeBtn" type="button" title="あ / カ / A">あ</button><button class="infobtn" id="helpBtn"')
    # ---- Control Panel: Japanese input, kana input; Keyboard settings: forget learned conversions ----
    R("  return[{id:'font',label:t('cp_font',FACES[S.face].name,FONTS[S.font].lines)},",
      "  return[{id:'font',label:t('cp_font',FACES[S.face].name,FONTS[S.font].lines)},\n"
      "    {id:'imemode',step:1,label:t('cp_imemode',t('imm_'+imeMode()))},{id:'imekana',step:1,label:t('cp_imekana',t('ik_'+imeKanaMode()))},"
      "{id:'widedisp',label:t('cp_wide',S.wideDisp?t('on'):t('off'))},")
    R("{id:'sndfile',label:t('cp_sndfile')}]},",
      "{id:'sndfile',label:t('cp_sndfile')},{id:'imekana',step:1,label:t('cp_imekana',t('ik_'+imeKanaMode()))},{id:'learn',label:t('cp_learn')}]},")
    R("    case 'sndfile':return pickSound();",
      "    case 'sndfile':return pickSound();\n"
      "    case 'learn':LEARN={};try{localStorage.removeItem(IME_LEARN_KEY)}catch(e){}subMsg=t('m_learn');break;")
    R("function controlStep(d,it=controlList()[ctrlSel]){if(!it||!it.step)return;\n  if(it.id==='screen')",
      "function controlStep(d,it=controlList()[ctrlSel]){if(!it||!it.step)return;\n  if(it.id==='imemode'||it.id==='imekana')imeStep(it.id,d);\n  else if(it.id==='screen')")
    # ---- finish the composition before anything else happens ----
    R("function setMode(m){\n", "function setMode(m){\n  if(m!=='word')imeFlush();\n")
    R("function switchFile(i){if(!on)return;", "function switchFile(i){if(!on)return;imeFlush();")
    R("function powerOff(auto){if(!on||splashing)return;", "function powerOff(auto){if(!on||splashing)return;imeFlush();")
    R("function pressKey(k){\n", "function pressKey(k){\n  if(on&&mode==='word'&&k!=='power'&&imePress(k))return;\n")
    R("lcd.addEventListener('click',e=>{\n  if(!on)return;", "lcd.addEventListener('click',e=>{\n  if(!on)return;if(mode==='word')imeFlush();")
    R("function setLang(d){", "function setLang(d){setTimeout(()=>imeBadge(),0);")
    # Plainwrite 0.83 has two posAtX functions and the tap handler called the one that got replaced: tapping the text threw an error
    R("setSel(Math.min(posAtX(ta.value,L[i],x),lineEnd(L,i)))", "setSel(Math.min(posAtX(L,i,x),lineEnd(L,i)))")
    # ---- Japanese on the screen: Pixel Gothic for everything by default. A font without Japanese gives way to
    #      Pixel Gothic whenever Japanese is in use (Japanese menus, or Japanese in the file), the way Plainwrite
    #      already swaps fonts for Cyrillic and Greek. Control Panel → Japanese in other fonts → Blend instead
    #      keeps the chosen font and borrows only the Japanese letters from Pixel Gothic (Kanji Talk style).
    R("const TEXT_GROUPS=[", "const TEXT_GROUPS=[['ja',/[\\u3040-\\u30ff\\u3400-\\u4dbf\\u4e00-\\u9fff\\uff66-\\uff9f]/,'あア漢字'],")
    R("  const have=[...g.keys()].join(' ');\n", "  if(lang().id==='ja')g.set('ja','あア漢字');\n  const have=[...g.keys()].join(' ');\n")
    R("  return g}\nfunction faceOK(", "  if(S.jaBlend)g.delete('ja');\n  return g}\nfunction faceOK(")
    # kana and kanji are full-width in every fallback font, so the width test can't tell whether a font has them:
    # for Japanese, go by the font table alone
    R("  try{for(const[grp,letters]of needGroups())for(const f of FACES){if(COVER[f.name]&&grp in COVER[f.name])continue;",
      "  try{for(const[grp,letters]of needGroups())for(const f of FACES){if(grp==='ja'||COVER[f.name]&&grp in COVER[f.name])continue;")
    R("function faceOK(f,groups=needGroups()){for(const grp of groups.keys()){const r=COVER[f.name]&&COVER[f.name][grp];",
      "function faceOK(f,groups=needGroups()){for(const grp of groups.keys()){const r=grp==='ja'?undefined:COVER[f.name]&&COVER[f.name][grp];")
    R("{name:'Pixel Gothic',langs:'ru uk be bg sr kk ky mn tg',", "{name:'Pixel Gothic',langs:'ru uk be bg sr kk ky mn tg ja',")
    # ---- device interface font: M PLUS 1p for Japanese (Jost stays for Latin), bundled so it works offline ----
    h = h.replace('"Jost",system-ui', '"Jost","M PLUS 1p J",system-ui')
    R('@font-face{font-family:"Plain Sans";', ''.join('@font-face{font-family:"M PLUS 1p J";src:url("ui-ja-%d.woff") format("woff");font-weight:%d;font-display:swap}\n' % (w, w) for w in (400, 500, 700)) + '@font-face{font-family:"Plain Sans";')
    # ---- key labels: with Japanese menus the top row and file keys are in Japanese, squeezed to fit their keys ----
    R(".k small{display:block;", ".kl{display:block;width:max-content;white-space:nowrap;position:relative;left:50%;transform:translateX(-50%) scaleX(var(--sq,1))}\n.k small{display:block;")
    R("function setLang(d){setTimeout(()=>imeBadge(),0);", "function setLang(d){setTimeout(()=>{imeBadge();labelKeys()},0);")
    # Control Panel: device labels in English or Japanese (until set, they follow the menu language)
    R("{id:'imekana',step:1,label:t('cp_imekana',t('ik_'+imeKanaMode()))},{id:'widedisp'",
      "{id:'imekana',step:1,label:t('cp_imekana',t('ik_'+imeKanaMode()))},{id:'devlang',step:1,label:t('cp_devlang',devLang()==='ja'?'日本語':'English')},{id:'widedisp'")
    R("  if(it.id==='imemode'||it.id==='imekana')imeStep(it.id,d);", "  if(it.id==='imemode'||it.id==='imekana')imeStep(it.id,d);\n  else if(it.id==='devlang'){S.devLang=devLang()==='ja'?'en':'ja';save();labelKeys()}")
    keyjs = open(os.path.join(HERE, 'keys.js'), encoding='utf-8').read()
    R("// ---------- boot ----------", keyjs + "\n// ---------- boot ----------")
    R("{id:'devlang',step:1,", "{id:'jablend',step:1,label:t('cp_jablend',t(S.jaBlend?'jb_blend':'jb_pixel'))},{id:'devlang',step:1,")
    R("  else if(it.id==='devlang')", "  else if(it.id==='jablend'){S.jaBlend=!S.jaBlend;save();resolveFace(true)}\n  else if(it.id==='devlang')")
    # ---- spell check: Japanese menus check the English words in the text; Japanese itself is skipped ----
    R("const dictId=()=>SPELL_DICT[S.lang||'en']||null;", "const dictId=()=>SPELL_DICT[S.lang==='ja'?'en':S.lang||'en']||null;")
    R("const WORD_RE=/[\\p{L}\\p{M}][\\p{L}\\p{M}'’\\-]*/gu;",
      "const WORD_RE=/(?:(?![\\p{sc=Han}\\p{sc=Hiragana}\\p{sc=Katakana}\\u30fc\\u3005])[\\p{L}\\p{M}])(?:(?![\\p{sc=Han}\\p{sc=Hiragana}\\p{sc=Katakana}\\u30fc\\u3005])[\\p{L}\\p{M}'’\\-])*/gu;")
    # ---- messages on the transfer and spell-check screens: wrap like everything else, so Japanese (no spaces) wraps too ----
    R("function wrapText(str){const words=str.split(' '),out=[];let cur='';\n  for(const w of words){const next=cur?cur+' '+w:w;if(cur&&textW(next)>maxW){out.push(cur);cur=w}else cur=next}if(cur)out.push(cur);return out}",
      "function wrapText(str){return wrap(str).map(L=>str.slice(L.s,L.e).trim()).filter(Boolean)}")
    # ---- Games → English Quiz: Same & Opposite plus five more English quizzes (quiz.js) ----
    R("const GAMES=['g_snake','g_dino','g_words','g_simon'],GAME_MODES=['snake','dino','words','simon'];",
      "const GAMES=['g_snake','g_dino','g_quiz','g_simon'],GAME_MODES=['snake','dino','quiz','simon'];")
    R("function stepDiff(i,d){const k=GAME_MODES[i];", "function stepDiff(i,d){const k=GAME_MODES[i];if(k==='quiz')return;")
    R("const gameLabel=(g,i)=>t(g)+'  ◂ '+t('d_'+diff(GAME_MODES[i]))+' ▸'", "const gameLabel=(g,i)=>GAME_MODES[i]==='quiz'?t(g)+'  ▸':t(g)+'  ◂ '+t('d_'+diff(GAME_MODES[i]))+' ▸'")
    R("function openGame(i){const m=GAME_MODES[i];", "function openGame(i){const m=GAME_MODES[i];if(m==='quiz')return setMode('quiz');")
    R("function wordsStart(quiet){", "function wordsStart(quiet){clearTimeout(wordsBusy);wordsBusy=0;if(quizKind!=='words')return quizStart(quiet);")   # a quiz left mid-answer doesn't skip a question in the next one
    R("hdr=t(q.ant?'w_ant':'w_syn',q.w.toUpperCase())", "hdr=(q.hdr||t(q.ant?'w_ant':'w_syn',q.w.toUpperCase()))")
    R("best('words')", "best(quizKind)")
    R("setBest('words',game.score)", "setBest(quizKind,game.score)")
    R("    case 'words':rows=wordsRows(n);break;", "    case 'quiz':rows=quizRows(n);break;\n    case 'words':rows=wordsRows(n);break;")
    R("    case 'words':wordsKey(k);break;", "    case 'quiz':quizKey(k);break;\n    case 'words':wordsKey(k);break;")
    R("  else if(mode==='snake'||mode==='dino'||mode==='words'||mode==='simon'){stopGame();setMode('games')}",
      "  else if(mode==='words'){stopGame();setMode('quiz')}\n  else if(mode==='quiz')setMode('games');\n  else if(mode==='snake'||mode==='dino'||mode==='simon'){stopGame();setMode('games')}")
    R("  if(mode==='words'&&item)return wordsPick(+item.dataset.i);",
      "  if(mode==='quiz'&&item){const i=+item.dataset.i,r=item.getBoundingClientRect();   // the right part (the ◂ ▸) changes difficulty\n"
      "    if(e.clientX>r.left+r.width*.6){quizSel=i;return quizStep(i,1)}return quizOpen(i)}\n  if(mode==='words'&&item)return wordsPick(+item.dataset.i);")
    R("// ---------- boot ----------", open(os.path.join(HERE, 'quiz.js'), encoding='utf-8').read() + "\n// ---------- boot ----------")
    # ---- phones: the same four lines, with the letters a little smaller inside them ----
    R("rowsN=rows;lh=r.height/rows;", "rowsN=rows;lh=r.height/rows;const shrink=matchMedia('(max-width:600px)').matches?.85:1;")
    R("fs=lh*fitK();maxW=r.width-1;", "fs=lh*fitK()*shrink;maxW=r.width-1;")
    R("const dpr=window.devicePixelRatio||1,raw=lh*dpr/(pxGrid+1);", "const dpr=window.devicePixelRatio||1,raw=lh*dpr/(pxGrid+1)*shrink;")
    # ---- the input method itself, just before boot ----
    ime = open(os.path.join(HERE, 'ime.js'), encoding='utf-8').read()
    R("// ---------- boot ----------", ime + "\n// ---------- boot ----------")
    # ---- help ----
    i = h.index('<div class="helpbody">') + len('<div class="helpbody">\n'); j = h.index('  </div>\n</section>\n<!-- ================= end of HELP TEXT')
    if mono:
        h = h[:i] + open(os.path.join(HERE, 'help-ja.html'), encoding='utf-8').read() + h[j:]
        R('<span>How to use Plainwrite</span><button id="helpClose" type="button">Close</button>', '<span>Plainwrite-J の使い方</span><button id="helpClose" type="button">閉じる</button>')
    else:
        body = h[i:j]
        body = body.replace('<h3>Eight files</h3>', open(os.path.join(HERE, 'help-ime-en.html'), encoding='utf-8').read() + '    <h3>Eight files</h3>', 1)
        # the bits of the Plainwrite help that are different here
        body = re.sub(r'\s*<li>The menus come in 15 forms of English.*?</li>', '\n      <li>Plainwrite-J speaks English and Japanese. On first start it picks Japanese if your system is set to Japanese, otherwise English. Change it in <b>Control Panel → Menu language</b>.</li>', body, count=1, flags=re.S)
        body = re.sub(r'\s*<li>Other languages come as language packs\..*?</li>', '\n      <li>Language packs from Plainwrite work here too. Plainwrite-J comes in two editions: <b>Japanese</b> (Japanese menus only) and <b>English–Japanese</b> (this one). Both have the same Japanese input.</li>', body, count=1, flags=re.S)
        body = re.sub(r'\s*<li>Latin script:.*?</li>', '', body, count=1, flags=re.S)
        body = body.replace('Snake, Dino Jump, Same &amp; Opposite and Simon Says.', 'Snake, Dino Jump, English Quiz and Simon Says.', 1)
        body = body.replace('<li><b>Same &amp; Opposite</b>: ten questions. Pick the word with the same or the opposite meaning, using the arrows and <kbd>↵</kbd>, keys <kbd>1</kbd> to <kbd>4</kbd>, or a tap. English words only.</li>',
          '<li><b>English Quiz</b>: six quizzes of ten questions each. Pick the answer with the arrows and <kbd>↵</kbd>, keys <kbd>1</kbd> to <kbd>4</kbd>, or a tap. '
          '<b>Same &amp; Opposite</b> (the word with the same or the opposite meaning), <b>Japanese → English</b>, <b>English → Japanese</b>, <b>Past tense</b> (irregular verbs), '
          '<b>Plurals</b> (irregular ones) and <b>Spelling</b>. Each has its own difficulty and best score: Easy has three choices, Normal four, Hard four look-alikes.</li>', 1)
        body = re.sub(r'\s*<li>Cyrillic: .*?</li>', '', body, count=1, flags=re.S)
        body = re.sub(r'<li>Key labels on the device stay in English\.</li>', '<li>Control Panel → Device labels switches the keys between English and Japanese.</li>', body, count=1)
        body = body.replace('It uses the dictionary for your menu language', 'It checks English words (Japanese text is skipped) with the dictionary for your menu language', 1)
        body += '    <h3>Licences</h3>\n    <p>Conversion dictionary: SKK-JISYO.L © SKK Development Team and contributors, GNU GPL v2 or later. Font: DotGothic16 © The DotGothic16 Project Authors, SIL Open Font License 1.1; Pixel Gothic J is a modified version. Interface font: M PLUS 1p © M+ FONTS PROJECT, SIL Open Font License 1.1. The J in the logo: Playfair Display © The Playfair Display Project Authors, cut down and renamed, SIL Open Font License 1.1.</p>\n'
        h = h[:i] + body + h[j:]
        R('<span>How to use Plainwrite</span>', '<span>How to use Plainwrite-J</span>')
    # the menu language in the HTML follows the language picked
    out = os.path.join(HERE, 'dist', edition)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(h)
    for f in ['plain-sans.ttf', 'home-computer.ttf', 'home-computer-thin.ttf', 'bedstead.otf', 'bedstead-condensed.otf', 'jost.ttf', 'vt323.ttf', 'press-start-2p.ttf', 'tiny5.ttf', 'ibm-plex-mono-medium.ttf', 'courier-prime-bold.ttf', 'share-tech-mono.ttf']:
        shutil.copy(os.path.join(SRC, f), out)
    shutil.copy(os.path.join(HERE, 'pixel-gothic.ttf'), out)   # merge_font.py
    for f in ['icon-192.png', 'icon-512.png']: shutil.copy(os.path.join(HERE, f), out)
    shutil.copy(os.path.join(HERE, 'logo-j.woff'), out)   # make_logo_font.py
    for w in (400, 500, 700): shutil.copy(os.path.join(HERE, 'uifont', 'ui-ja-%d.woff' % w), out)   # make_ui_font.py   # sakura pink (recolor_icon.py)
    shutil.copy(os.path.join(HERE, 'dict', 'dict-ja.txt'), out)
    # service worker
    sw = open(os.path.join(SRC, 'sw.js'), encoding='utf-8').read()
    def SR(a, b):
        nonlocal sw
        assert sw.count(a) == 1, a; sw = sw.replace(a, b)
    sw = re.sub(r"const CACHE = 'plainwrite-all-v\d+';", "const CACHE = 'plainwrite-all-vX';", sw)
    SR("const CACHE = 'plainwrite-all-vX';", f"const CACHE = 'plainwrite-j-{edition}-v{VER}-{BUILD}';")   # BUILD: a rebuild of the same version still reaches installed copies
    SR("// Plainwrite service worker", "// Plainwrite-J service worker")
    SR("const CORE = ['./', './index.html', './langs/all.json', './manifest.json', './icon-192.png', './icon-512.png'];",
       "const CORE = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './pixel-gothic.ttf', './ui-ja-400.woff', './ui-ja-500.woff', './ui-ja-700.woff', './logo-j.woff'];")
    SR("'./share-tech-mono.ttf']).catch(() => {});", "'./share-tech-mono.ttf', './dict-ja.txt']).catch(() => {});")
    open(os.path.join(out, 'sw.js'), 'w', encoding='utf-8').write(sw)
    man = json.load(open(os.path.join(SRC, 'manifest.json')))
    man['name'] = 'Plainwrite-J'; man['short_name'] = 'Plainwrite-J'
    man['description'] = 'レトロでミニマルなワープロ。日本語入力つき。' if mono else 'Retro minimalist word processing with Japanese input. Eight auto-saving files, works offline.'
    man['lang'] = 'ja' if mono else 'en'
    man['background_color'] = '#ffffff'   # the splash screen matches the icon's white page
    json.dump(man, open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    shutil.copy(os.path.join(HERE, 'README.md'), out)
    shutil.copy(os.path.join(HERE, '..', 'google', 'fonts', 'ofl', 'dotgothic16', 'OFL.txt'), out)
    shutil.copy(os.path.join(HERE, '..', 'google', 'fonts', 'ofl', 'mplus1p', 'OFL.txt'), os.path.join(out, 'OFL-MPLUS1p.txt'))
    shutil.copy(os.path.join(HERE, '..', 'google', 'fonts', 'ofl', 'playfairdisplay', 'OFL.txt'), os.path.join(out, 'OFL-Playfair.txt'))
    shutil.copy('/usr/share/common-licenses/GPL-2', os.path.join(out, 'COPYING-dictionary.txt'))
    print(edition, 'ok', len(h))

# the interface font holds just the letters the Japanese text uses, so cut it again from the current text
subprocess.run([sys.executable, os.path.join(HERE, 'make_ui_font.py'), os.path.join(HERE, '..', 'google', 'fonts', 'ofl', 'mplus1p'), os.path.join(HERE, 'uifont')]
               + [os.path.join(HERE, f) for f in ('ja_strings.js', 'help-ja.html', 'help-ime-en.html', 'keys.js', 'ime.js', 'quiz.js', 'build.py')], check=True, stdout=subprocess.DEVNULL)
for e in (sys.argv[1:] or ['ja', 'en-ja']):
    build(e)
for f in FAILS: print('MISSING', f)
if FAILS: sys.exit(1)
# keep the Android and desktop projects' copies of both editions up to date
for proj in ('plainwrite-j-android', 'plainwrite-j-desktop'):
    root = os.path.join(HERE, '..', 'platforms', proj)
    if os.path.isdir(root):
        subprocess.run(['sh', 'tools/update_www.sh', os.path.join(HERE, 'dist')], cwd=root, check=True, stdout=subprocess.DEVNULL)
        # the app icons follow icon-512.png
        from PIL import Image
        ic = Image.open(os.path.join(HERE, 'icon-512.png')).convert('RGBA')
        if proj.endswith('android'):
            for d, z in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)]:
                ic.resize((z, z), Image.LANCZOS).save(os.path.join(root, 'app/src/main/res/mipmap-%s/ic_launcher.png' % d))
        else:
            dd = os.path.join(root, 'src-tauri/icons/')
            for n, z in [('32x32.png', 32), ('128x128.png', 128), ('128x128@2x.png', 256), ('icon.png', 512)]: ic.resize((z, z), Image.LANCZOS).save(dd + n)
            ic.save(dd + 'icon.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]); ic.save(dd + 'icon.icns')
        print('refreshed', proj)
