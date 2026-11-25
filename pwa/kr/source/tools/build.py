#!/usr/bin/env python3
"""Builds Plainwrite-K from a Plainwrite release (index.html of the Multilingual edition, currently 1.07).

    python3 build.py <plainwrite index.html> <out dir> [--fonts <dir with Galmuri11.ttf / neodgm.ttf>]

Makes two editions in <out dir>/ko (Korean menus only) and <out dir>/en-ko (English and Korean menus).
Every change to Plainwrite is a find-and-replace below; each must match exactly once, so a new
Plainwrite release that moves things around stops the build instead of quietly breaking it.
The editable text lives next to this script: ime-ko.js, i18n-ko.js, help-ko.html, help-en-ko.html,
about-ko.txt, about-en-ko.txt, welcome-ko.txt, welcome-en-ko.txt, sheets-ko.json.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = '0.2.3'   # Plainwrite-K's own version; the About screen shows it after Plainwrite's (1.07/0.2.3K)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()


def build(src, edition, korean_faces):
    s = src
    ko_only = edition == 'ko'

    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count:
            raise SystemExit(f'[{edition}] expected {count} match(es), found {n}: {old[:90]!r}')
        s = s.replace(old, new)

    def rep_re(pat, new, flags=0):
        nonlocal s
        s2, n = re.subn(pat, lambda m: new, s, count=1, flags=flags)
        if n != 1:
            raise SystemExit(f'[{edition}] no match for /{pat[:80]}/')
        s = s2

    # ---------- head ----------
    if ko_only:
        rep('<html lang="en">', '<html lang="ko">')
    rep('<title>Plainwrite</title>', '<title>Plainwrite-K</title>')
    rep('<meta name="apple-mobile-web-app-title" content="Plainwrite">', '<meta name="apple-mobile-web-app-title" content="Plainwrite-K">')
    rep('<meta name="application-name" content="Plainwrite">', '<meta name="application-name" content="Plainwrite-K">')

    # ---------- styles ----------
    UI = '"Noto Sans KR K"'
    rep('html,body{margin:0;background:var(--page);color:#c9cdd2;font-family:"Jost",system-ui',
        f'html,body{{margin:0;background:var(--page);color:#c9cdd2;font-family:"Jost",{UI},system-ui')
    rep('.logo{font-family:"Jost",system-ui,sans-serif;', f'.logo{{font-family:"Jost",{UI},system-ui,sans-serif;')
    rep('font:500 12px/1.15 "Jost",system-ui,-apple-system,sans-serif;color:var(--kt);',
        f'font:500 12px/1.15 "Jost",{UI},system-ui,-apple-system,sans-serif;color:var(--kt);')
    # the K in the logo, the composition underline, the Hanja choices and the mode badge
    css = ('@font-face{font-family:"Plainwrite K";src:url("logo-k.woff") format("woff");font-weight:700;font-display:block}\n'
           '.logo::after{content:"K";font-family:"Plainwrite K",Georgia,"Times New Roman",serif;font-weight:700;margin-left:.1em;letter-spacing:0}\n'
           '.pre{box-shadow:inset 0 calc(-1*max(1px,.07em)) var(--ink)}\n'
           '.pre.seg{background:var(--ink);color:var(--lcd);box-shadow:none}\n'
           '.inv .csel{background:var(--lcd);color:var(--ink)}\n'
           f'.imebtn{{min-width:22px;height:20px;border-radius:5px;border:1.5px solid var(--brand);background:transparent;color:var(--brandb);font:700 12px/1 {UI},system-ui,sans-serif;padding:0 3px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;letter-spacing:0}}\n'
           '.imebtn.off{opacity:.7}.imebtn:hover{border-color:#c2c8cf;color:#e3e6ea}\n'
           '.helpbody{word-break:keep-all;overflow-wrap:break-word}\n'
           '.kl{display:block;width:max-content;white-space:nowrap;position:relative;left:50%;transform:translateX(-50%) scaleX(var(--sq,1))}\n')
    rep('</style>', css + '</style>')
    faces = ''.join(f'@font-face{{font-family:"{UI[1:-1]}";src:url("ui-ko-{w}.woff") format("woff");font-weight:{w};font-display:swap}}\n' for w in (400, 500, 700))
    for f in korean_faces:
        faces += f'@font-face{{font-family:"{f["family"]}";src:url("{f["file"]}") format("{f["format"]}");font-display:swap}}\n'
    faces += '@font-face{font-family:"Hanja Fallback";src:url("hanja-fallback.woff") format("woff");font-display:swap}\n'
    rep('@font-face{font-family:"Share Tech Mono"', faces + '@font-face{font-family:"Share Tech Mono"')

    # ---------- markup ----------
    rep('<span class="status"><button class="infobtn" id="helpBtn"',
        '<span class="status"><button class="imebtn" id="imeBtn" type="button" title="한 / Ａ / A">한</button><button class="infobtn" id="helpBtn"')
    # help sheet: the Korean edition gets it all in Korean; English–Korean gets a Korean input section
    a = s.index('<section class="sheet help" id="help"')
    b = s.index('</section>', a) + len('</section>')
    if ko_only:
        s = s[:a] + rd('help-ko.html').strip() + s[b:]
    else:
        help_html = s[a:b]
        help_html = help_html.replace('How to use Plainwrite<', 'How to use Plainwrite-K<', 1)
        i = help_html.index('    <h3>Eight files</h3>')
        help_html = help_html[:i] + rd('help-en-ko.html').rstrip() + '\n\n' + help_html[i:]
        help_html = help_html.replace(
            '<li>Key labels on the device stay in English.</li>',
            '<li>Plainwrite-K speaks English and Korean. On first start it picks Korean if your system is set to Korean, otherwise English. '
            'Plainwrite-K comes in two editions: <b>Korean</b> (Korean menus only) and <b>English–Korean</b> (this one). Both have the same Korean input.</li>\n'
            '      <li><b>Control Panel → Device labels</b> switches the keys between English and Korean.</li>')
        help_html = help_html.replace(
            'It uses the dictionary for your menu language,',
            'It checks words in Latin letters (Hangul and Hanja are skipped) with the dictionary for your menu language (English with Korean menus),')
        help_html = help_html.replace('Snake, Dino Jump, Same &amp; Opposite and Simon Says.', 'Snake, Dino Jump, English Quiz and Simon Says.')
        a = help_html.index('          <li><b>Same &amp; Opposite</b>:'); b = help_html.index('</li>', a) + 5
        help_html = help_html[:a] + ('          <li><b>English Quiz</b>: six quizzes of ten questions each. Pick the answer with the arrows and <kbd>↵</kbd>, keys <kbd>1</kbd> to <kbd>4</kbd>, or a tap. '
            '<b>Same &amp; Opposite</b> (the word with the same or the opposite meaning), <b>Korean → English</b>, <b>English → Korean</b>, <b>Past tense</b> (irregular verbs), '
            '<b>Plurals</b> (irregular ones) and <b>Spelling</b>. Each has its own difficulty and best score: Easy has three choices, Normal four, Hard four look-alikes.</li>') + help_html[b:]
        help_html = help_html.replace('</div>\n</section>', '    <h3>Licences</h3>\n    <p>' + rd('licences-en.txt').strip() + '</p>\n  </div>\n</section>')
        s = s[:a] + help_html + s[b:]
    if ko_only:
        # the other sheets' titles, labels and buttons
        for old, new in json.load(open(os.path.join(HERE, 'sheets-ko.json'), encoding='utf-8')):
            rep(old, new)

    # ---------- texts ----------
    base = re.search(r"const APP_VER='Version ([0-9.]+)", src).group(1)
    ver = f'버전 {base}/{VERSION}K (한국어판)' if ko_only else f'Version {base}/{VERSION}K (English–Korean)'
    rep_re(r"const APP_VER='[^']*';", 'const APP_VER=' + json.dumps(ver, ensure_ascii=False) + ';')
    about = rd('about-ko.txt' if ko_only else 'about-en-ko.txt').strip()
    about = about.replace('{FONTS_KO}', ', '.join(f['credit_ko'] for f in korean_faces if not f.get('extra'))).replace('{FONTS_EN}', ', '.join(f['credit_en'] for f in korean_faces if not f.get('extra')))
    a = s.index('const ABOUT_TEXT=`')
    b = s.index('`;', a)
    s = s[:a] + '// Plainwrite-K: also in about-ko.txt / about-en-ko.txt in the source folder (rebuilding uses those).\nconst ABOUT_TEXT=`' + about.replace('`', '\\`') + s[b:]
    welcome = rd('welcome-ko.txt' if ko_only else 'welcome-en-ko.txt').strip()
    rep_re(r'const WELCOME="[^"\n]*";', 'const WELCOME=' + json.dumps(welcome, ensure_ascii=False) + ';')

    # ---------- menu languages ----------
    if ko_only:
        rep_re(r"const LANGS=\[\{id:'en',name:'English \(US\)'\}.*?\];\n", "const LANGS=[{id:'ko',name:'한국어'}];\n", re.S)
    else:
        rep("{id:'en-JM',name:'English (Jamaica)'}];", "{id:'en-JM',name:'English (Jamaica)'},{id:'ko',name:'한국어'}];")
    rep('// English variants: only the strings that differ from US English', rd('i18n-ko.js').strip() + '\n// English variants: only the strings that differ from US English')
    # Korean typing speed is counted in keystrokes a minute (타/분): five to a word
    rep("function t(key,...a){const d=I18N[S.lang]||I18N.en;",
        "function t(key,...a){const d=I18N[S.lang]||I18N.en;if(S.lang==='ko'&&/^tutor_(speed|line_done|live)$/.test(key)&&a[0]!=null)a[0]=Math.round(a[0]*5);")
    rep("function setLang(d){const i=LANGS.indexOf(lang());",
        "function setLang(d){setTimeout(()=>{imeBadge();labelKeys()},0);const i=LANGS.indexOf(lang());")
    rep("const KEY='neo-sim-v1';", "const KEY='plainwrite-k-v1';")

    # ---------- fonts ----------
    first = korean_faces[0]
    KFB = f'"{first["family"]}","Pixel Gothic","Hanja Fallback",'
    entries = ''.join(
        f"  {{name:'{f['name']}',langs:'ko{(' ' + f['langs']) if f.get('langs') else ''}',css:'\"{f['family']}\"',{('pixel:' + str(f['pixel']) + ',') if f.get('pixel') else ''}fb:'{f.get('fb','')}\"Pixel Gothic\",\"Hanja Fallback\",\"Plain Sans\",'}},\n"
        for f in korean_faces)
    a = s.index('const FACES=[\n')
    b = s.index('];', a)
    body = s[a + len('const FACES=[\n'):b]
    lines = []
    for ln in body.split('\n'):
        if not ln.strip():
            continue
        if "fb:'" in ln:
            ln = ln.replace("fb:'", "fb:'" + KFB)
        else:
            ln = re.sub(r"(css:'[^']*')", r"\1,fb:'" + KFB + "'", ln)
        lines.append(ln)
    s = s[:a] + 'const FACES=[\n' + entries + '\n'.join(lines) + s[b:]
    # the Korean font the others borrow Hangul from is the Korean font chosen last (Galmuri to start with)
    rep("const faceCss=()=>FACES[S.face].css+', '+(FACES[S.face].fb||'')+'ui-monospace, monospace';",
        "const KO_FACES=FACES.filter(f=>(f.langs||'').split(' ').includes('ko')).map(f=>f.name);\n"
        "const koFace=()=>FACES.find(f=>f.name===(KO_FACES.includes(S.koFace)?S.koFace:KO_FACES[0]));\n"
        "const faceCss=()=>{const f=FACES[S.face],k=koFace();return f.css+', '+(f===k?'':k.css+', ')+(f.fb||'')+'ui-monospace, monospace'};")
    rep("function setFace(i){i=(i+FACES.length)%FACES.length;S.faceName=FACES[i].name;",
        "function setFace(i){i=(i+FACES.length)%FACES.length;S.faceName=FACES[i].name;if(KO_FACES.includes(FACES[i].name))S.koFace=FACES[i].name;")
    rep_re(r"face:0,faceName:'Plain Sans',font:0,blink:true,lastFind:'',palette:0,dark:'off',lang:null,kbd:'device',autoOff:10,powerOn:'power',",
           f"face:0,faceName:'{first['name']}',font:0,blink:true,lastFind:'',palette:0,dark:'off',lang:{json.dumps('ko') if ko_only else 'null'},kbd:'device',autoOff:10,powerOn:'power',setupDone:true,imeOn:true,imeMode:'hang',imeKbd:'2',")
    # Hangul and Hanja are as wide as two letters in monospace; Wide letters draws Latin letters full-width on screen
    rep("function G(ch){let g=gcache.get(ch);if(g)return g;const n=W0(ch);\n  if(spacingMode()==='mono')g={w:cellW,ti:(cellW-n)/2};",
        "const isWide=ch=>/[\\u1100-\\u115f\\u2e80-\\u303e\\u3041-\\u33ff\\u3400-\\u4dbf\\u4e00-\\u9fff\\ua960-\\ua97f\\uac00-\\ud7a3\\uf900-\\ufaff\\ufe30-\\ufe4f\\uff00-\\uff60\\uffe0-\\uffe6]/.test(ch);\n"
        "function G(ch){let g=gcache.get(ch);if(g)return g;const n=W0(ch);\n  if(spacingMode()==='mono'){const c=isWide(ch)?2*cellW:cellW;g={w:c,ti:(c-n)/2}}")
    rep("function W(ch){return spacingMode()==='auto'?W0(ch):G(ch).w}",
        "function W(ch){return spacingMode()==='auto'?W0(ch):G(ch).w}\n"
        "function dispCh(ch){if(!S.wideDisp||mode!=='word')return ch;const c=ch.charCodeAt(0);if(c>0x20&&c<0x7f)return String.fromCharCode(c+0xfee0);if(c===0x20)return'\\u3000';return ch}\n"
        "const WT=ch=>W(dispCh(ch));")
    rep("const COVER_KEY='plainwrite-cover-v3';", "const COVER_KEY='plainwrite-k-cover-v1';")
    rep("const FACE_FALLBACK=['Teletext','Modern Mono','Arcade','Tiny Pixel','Pixel Gothic','Teletext Narrow'];",
        "const FACE_FALLBACK=['Teletext','Modern Mono','Arcade','Tiny Pixel','Pixel Gothic','Teletext Narrow'];   // Korean in use: the Korean font comes first (resolveFace)")
    rep("const TEXT_GROUPS=[['ru',", "const TEXT_GROUPS=[['ko',/[\\u1100-\\u11ff\\u3130-\\u318f\\uac00-\\ud7a3]/,'가나다한글'],['ru',")
    rep("function needGroups(){const g=new Map(),p=lang().pack,k=kbd();",
        "function needGroups(){const g=new Map(),p=lang().pack,k=kbd();\n  if(lang().id==='ko')g.set('ko','가나다한글');")
    rep("  return g}\nfunction faceOK(", "  if(S.koBlend)g.delete('ko');\n  return g}\nfunction faceOK(")
    rep("function faceOK(f,groups=needGroups()){for(const grp of groups.keys()){const r=COVER[f.name]&&COVER[f.name][grp];",
        "function faceOK(f,groups=needGroups()){for(const grp of groups.keys()){const r=grp==='ko'?undefined:COVER[f.name]&&COVER[f.name][grp];")
    rep("  for(const n of FACE_FALLBACK){if(i>=0)break;",
        "  for(const n of(g.has('ko')?[koFace().name]:[]).concat(FACE_FALLBACK)){if(i>=0)break;")
    rep("try{for(const[grp,letters]of needGroups())for(const f of FACES){if(COVER[f.name]&&grp in COVER[f.name])continue;",
        "try{for(const[grp,letters]of needGroups())for(const f of FACES){if(grp==='ko'||COVER[f.name]&&grp in COVER[f.name])continue;")

    # ---------- wrapping and drawing ----------
    rep("function wrap(text){const lines=[],n=text.length;let start=0;",
        "// Korean wraps at spaces like English; Hanja, kana and full-width signs may break anywhere, but never before 、。」 and the like\n"
        "const NOSTART='、。，．・：；？！」』）】〉》〕｝…‥',NOEND='「『（【〈《〔｛';\n"
        "const anyBreak=ch=>isWide(ch)&&!/[\\uac00-\\ud7a3\\u1100-\\u11ff\\u3130-\\u318f]/.test(ch);\n"
        "function wrap(text){const wt=text===ta.value,lines=[],n=text.length;let start=0;")
    rep("""      for(;i<pend;i++){const ch=text[i],cw=W(ch);
        if(ch===' '){lastSp=i;w+=cw;continue}           // spaces may hang past the edge, never force a break
        if(w+cw>maxW&&i>s)break;w+=cw}""",
        """      for(;i<pend;i++){const ch=text[i],cw=wt?WT(ch):W(ch);
        if(ch===' '||ch==='\\u3000'){lastSp=i;w+=cw;continue}           // spaces may hang past the edge, never force a break
        if(w+cw>maxW&&i>s){
          if(NOSTART.includes(ch)){if(i-1>s&&anyBreak(text[i-1])&&!NOSTART.includes(text[i-1]))lastSp=i-2}
          else if((anyBreak(ch)||anyBreak(text[i-1]))&&!NOEND.includes(text[i-1]))lastSp=i-1;
          break}
        if(i>s&&(anyBreak(ch)||anyBreak(text[i-1]))&&!NOSTART.includes(ch)&&!NOEND.includes(text[i-1]))lastSp=i-1;
        w+=cw}""")
    rep("function posAtX(text,L,x){let w=0;for(let p=L.s;p<L.e;p++){const cw=W(text[p]);",
        "function posAtX(text,L,x){let w=0;for(let p=L.s;p<L.e;p++){const cw=WT(text[p]);")
    rep("""    for(let p=L.s;p<L.e;p++){const ch=text[p];
      if(p===c&&a===b&&li===i)h+=curSpan(ch);""",
        """    for(let p=L.s;p<L.e;p++){const ch=dispCh(text[p]);
      const ic=imeCls(p);
      if(p===c&&a===b&&li===i&&!imeBar())h+=curSpan(ch);
      else if(ic)h+='<span class="'+ic+'">'+esc(ch)+'</span>';""")
    rep("    if(li===i&&a===b&&c>=L.e)h+=curSpan(' ');", "    if(li===i&&a===b&&c>=L.e&&!imeBar())h+=curSpan(' ');")
    rep("      rows=wordRows(n-ml.length);for(const l of ml)rows.push(invRow(l));break}",
        "      if(imeBar()&&n>1){rows=wordRows(n-1);rows.push(candRow());break}\n      rows=wordRows(n-ml.length);for(const l of ml)rows.push(invRow(l));break}")
    # Plainwrite 1.07 has two functions called posAtX; the later one wins, so tapping the text called it the wrong way
    rep("else setSel(Math.min(posAtX(ta.value,L[i],x),lineEnd(L,i)));", "else setSel(Math.min(posAtX(L,i,x),lineEnd(L,i)));")
    rep("  for(let p=L.s;p<end;p++){const cw=W(v[p]);if(w+cw/2>x)return p;w+=cw}return end}",
        "  for(let p=L.s;p<end;p++){const cw=WT(v[p]);if(w+cw/2>x)return p;w+=cw}return end}")
    rep("  if(c!==vertCaret||goalX==null)goalX=textW(ta.value.slice(lines[li].s,c));",
        "  if(c!==vertCaret||goalX==null)goalX=[...ta.value.slice(lines[li].s,c)].reduce((w,ch)=>w+WT(ch),0);")

    # ---------- phones: the Korean fonts fill more of their pixel grid than Plainwrite's own fonts, so on narrow
    # screens they're drawn one pixel step smaller (still whole screen pixels), and Jeongeum by the same amount ----------
    rep("    const unit=raw>=2?Math.floor(raw):Math.max(1,raw);fs=unit*pxGrid/dpr;",
        "    const kr=raw*koScale(),unit=kr>=2?Math.floor(kr):Math.max(1,kr);fs=unit*pxGrid/dpr;")
    rep("  else if(lineSp()){rowsN=Math.max(1,Math.floor(r.height/(lh+lineSp()*fs/10)));lh=r.height/rowsN}",
        "  else{fs*=koScale();if(lineSp()){rowsN=Math.max(1,Math.floor(r.height/(lh+lineSp()*fs/10)));lh=r.height/rowsN}}")
    rep("function layout(){sizeLcd();",
        "function koScale(){return matchMedia('(max-width:600px)').matches&&(FACES[S.face].langs||'').split(' ').includes('ko')?.8:1}\nfunction layout(){sizeLcd();")

    # ---------- Control Panel ----------
    rep("    {id:'dark',step:1,label:t('cp_dark',t('dark_'+S.dark))},",
        "    {id:'imemode',step:1,label:t('cp_imemode',t('imm_'+imeMode()))},{id:'imekbd',step:1,label:t('cp_imekbd',t('ik_'+imeKbd()))},"
        "{id:'koblend',step:1,label:t('cp_koblend',S.koBlend?t('kb_blend'):t('kb_font',koFace().name))},"
        "{id:'devlang',step:1,label:t('cp_devlang',devLang()==='ko'?'한국어':'English')},{id:'widedisp',label:t('cp_wide',S.wideDisp?t('on'):t('off'))},\n"
        "    {id:'dark',step:1,label:t('cp_dark',t('dark_'+S.dark))},")
    if ko_only:
        rep("    {id:'langs',label:t('cp_langs')},\n", "")
    rep("{id:'sound',step:1,label:t('cp_sound',soundName())},{id:'sndfile',label:t('cp_sndfile')}]},",
        "{id:'sound',step:1,label:t('cp_sound',soundName())},{id:'sndfile',label:t('cp_sndfile')},{id:'imekbd',step:1,label:t('cp_imekbd',t('ik_'+imeKbd()))},{id:'learn',label:t('cp_learn')}]},")
    rep("    case 'wake':S.wake=!S.wake;save();break;",
        "    case 'wake':S.wake=!S.wake;save();break;\n"
        "    case 'learn':LEARN={};try{localStorage.removeItem(IME_LEARN_KEY)}catch(e){}subMsg=t('m_learn');break;\n"
        "    case 'widedisp':S.wideDisp=!S.wideDisp;save();break;")
    rep("  if(it.id==='screen')setPalette(S.palette+d);",
        "  if(it.id==='imemode'||it.id==='imekbd')imeStep(it.id,d);\n"
        "  else if(it.id==='koblend'){S.koBlend=!S.koBlend;save();resolveFace(true)}\n"
        "  else if(it.id==='devlang'){S.devLang=devLang()==='ko'?'en':'ko';save();labelKeys()}\n"
        "  else if(it.id==='screen')setPalette(S.palette+d);")

    # ---------- finishing the syllable before anything else ----------
    rep("  mode=m;cmd.value='';confirmErase=false;", "  if(m!=='word')imeFlush();\n  mode=m;cmd.value='';confirmErase=false;")
    rep("function switchFile(i){if(!on)return;syncFile();", "function switchFile(i){if(!on)return;imeFlush();syncFile();")
    rep("function powerOff(auto){if(!on||splashing)return;", "function powerOff(auto){if(!on||splashing)return;imeFlush();")
    rep("function pressKey(k){\n", "function pressKey(k){\n  if(on&&mode==='word'&&k!=='power'&&imePress(k))return;\n")
    rep("lcd.addEventListener('click',e=>{\n  if(!on)return;", "lcd.addEventListener('click',e=>{\n  if(!on)return;if(mode==='word')imeFlush();")

    # ---------- storage, files, language packs, spelling ----------
    for db in ('sound', 'fonts', 'wall'):
        s = s.replace(f"'plainwrite-{db}'", f"'plainwrite-k-{db}'")
    rep("try{localStorage.removeItem(KEY);", "try{localStorage.removeItem('plainwrite-k-learn-v1');localStorage.removeItem(KEY);")
    s = s.replace('`Plainwrite File ${S.active+1}.txt`', '`Plainwrite-K File ${S.active+1}.txt`')
    rep("const BUNDLE='langs/all.json';", "const BUNDLE=null;")
    rep("const PACK_KEY='plainwrite-langs-v1';", "const PACK_KEY='plainwrite-k-langs-v1';")
    if ko_only:
        rep("function pickLocale(){", "function pickLocale(){return'ko';")
    else:
        rep("function pickLocale(){", "function pickLocale(){{const p=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'en']).map(s=>String(s).toLowerCase());if(p[0]&&p[0].split('-')[0]==='ko')return'ko'}")
    rep("const dictId=()=>SPELL_DICT[S.lang||'en']||null;", "const dictId=()=>SPELL_DICT[S.lang==='ko'?'en':S.lang||'en']||null;")
    rep("const WORD_RE=/[\\p{L}\\p{M}][\\p{L}\\p{M}'’\\-]*/gu;",
        "const WORD_RE=/(?:(?![\\p{sc=Han}\\p{sc=Hangul}])[\\p{L}\\p{M}])(?:(?![\\p{sc=Han}\\p{sc=Hangul}])[\\p{L}\\p{M}'’\\-])*/gu;")

    # ---------- Hangul and Hanja tutors ----------
    rep('["app_tutor","kwmenu"],', '["app_tutor","kwmenu"],["app_htutor","kwmenu-ko"],["app_hjtutor","kwmenu-hj"],')
    rep("function openApplet(i){const m=APPLETS[i][1];",
        "function openApplet(i){const m=APPLETS[i][1];if(m.startsWith('kwmenu')){menuSel=i;setTutor(m==='kwmenu-ko'?'ko':m==='kwmenu-hj'?'hj':'en');return setMode('kwmenu')}")
    rep("const kwMenuRows=n=>listRows(n,t('tutor_hdr'),",
        "const kwMenuRows=n=>listRows(n,t(TUTOR==='ko'?'ko_tutor_hdr':TUTOR==='hj'?'hj_tutor_hdr':'tutor_hdr'),")
    rep("function makeLine(lesson){const L=LESSONS[lesson],max=Math.min(cols()-2,34),",
        "function makeLine(lesson){const L=LESSONS[lesson],max=Math.min(cols()-2,L.max||34),")
    rep("const next=s?s+' '+w:w;", "const next=s?s+(L.sep!=null?L.sep:' ')+w:w;")
    rep("function startLesson(i){", "function startLesson(i){if(TUTOR!=='en'&&imeMode()!=='hang')setImeMode('hang');")
    rep("""function kwStats(){const t=kw.target,typed=cmd.value;let ok=0;for(let i=0;i<typed.length;i++)if(typed[i]===t[i])ok++;
  const mins=kw.start?((kw.end||performance.now())-kw.start)/60000:0;
  return{ok,typed:typed.length,mins,wpm:mins>0?Math.round(ok/5/mins):0,acc:typed.length?Math.round(ok/typed.length*100):100,done:typed.length>=t.length}}
function kwTotals(){const r=kw.results,ok=r.reduce((a,x)=>a+x.ok,0),ty=r.reduce((a,x)=>a+x.typed,0),m=r.reduce((a,x)=>a+x.mins,0);
  return{wpm:m>0?Math.round(ok/5/m):0,acc:ty?Math.round(ok/ty*100):100}}""",
"""// Korean lessons count keystrokes (한 = 3), so speed comes out in 타/분 like Korean typing tutors
function kwStats(){const t=kw.target,typed=kwTyped(),L=LESSONS[kw.lesson]||{};let ok=0,ks=0;for(let i=0;i<typed.length;i++)if(typed[i]===t[i]){ok++;ks+=L.ko?strokes(typed[i]):1}
  const mins=kw.start?((kw.end||performance.now())-kw.start)/60000:0;
  return{ok,ks,typed:typed.length,mins,wpm:mins>0?Math.round(ks/5/mins):0,acc:typed.length?Math.round(ok/typed.length*100):100,done:typed.length>=t.length&&(!L.exact||typed===t)}}
function kwTotals(){const r=kw.results,ok=r.reduce((a,x)=>a+x.ok,0),ks=r.reduce((a,x)=>a+x.ks,0),ty=r.reduce((a,x)=>a+x.typed,0),m=r.reduce((a,x)=>a+x.mins,0);
  return{wpm:m>0?Math.round(ks/5/m):0,acc:ty?Math.round(ok/ty*100):100}}""")
    rep("""  const t=kw.target,typed=cmd.value;
  if(n>4)rows.push(invRow(`${tr(LESSONS[kw.lesson].key)}  ${kw.line+1}/${KW_LINES}`));
  rows.push(plain(t));
  let h='';for(let i=0;i<typed.length;i++){h+=typed[i]===t[i]?esc(typed[i]):'<span class="inv">'+esc(typed[i])+'</span>'}""",
"""  const t=kw.target,typed=cmd.value,LL=LESSONS[kw.lesson];
  if(n>4)rows.push(invRow(`${tr(LL.key)}  ${kw.line+1}/${KW_LINES}`));
  if(LL.hint)rows.push(plain(LL.hint(t)));
  rows.push(plain(t));
  let h='';for(let i=0;i<typed.length;i++){const ic=comp&&comp.el===cmd?imeCls(i):'';
    h+=ic?'<span class="'+ic+'">'+esc(typed[i])+'</span>':typed[i]===t[i]?esc(typed[i]):'<span class="inv">'+esc(typed[i])+'</span>'}""")
    rep("    case 'keywords':rows=kwRows(n);break;", "    case 'keywords':rows=kwRows(n);if(comp&&comp.conv&&comp.el===cmd)rows[n-1]=candRow();break;")

    # ---------- English Quiz (Games), as in Plainwrite-J ----------
    rep("const GAMES=['g_snake','g_dino','g_words','g_simon'],GAME_MODES=['snake','dino','words','simon'];",
        "const GAMES=['g_snake','g_dino','g_quiz','g_simon'],GAME_MODES=['snake','dino','quiz','simon'];")
    rep("function stepDiff(i,d){const k=GAME_MODES[i];S.diff", "function stepDiff(i,d){const k=GAME_MODES[i];if(k==='quiz')return;S.diff")
    rep("const gameLabel=(g,i)=>t(g)+'  ◂ '+t('d_'+diff(GAME_MODES[i]))+' ▸'",
        "const gameLabel=(g,i)=>GAME_MODES[i]==='quiz'?t(g)+'  ▸':t(g)+'  ◂ '+t('d_'+diff(GAME_MODES[i]))+' ▸'")
    rep("function openGame(i){const m=GAME_MODES[i];stopGame();", "function openGame(i){const m=GAME_MODES[i];if(m==='quiz')return setMode('quiz');stopGame();")
    rep("function wordsStart(quiet){const order=", "function wordsStart(quiet){clearTimeout(wordsBusy);wordsBusy=0;if(quizKind!=='words')return quizStart(quiet);const order=")
    rep("function wordsRows(n){if(game.state==='over')return[invRow(t('w_done',game.score,game.qs.length,best('words'))),",
        "function wordsRows(n){if(game.state==='over')return[invRow(t('w_done',game.score,game.qs.length,best(quizKind))),")
    rep("const q=game.qs[game.i],hdr=t(q.ant?'w_ant':'w_syn',q.w.toUpperCase())+", "const q=game.qs[game.i],hdr=(q.hdr||t(q.ant?'w_ant':'w_syn',q.w.toUpperCase()))+")
    rep("if(game.i>=game.qs.length){game.state='over';setBest('words',game.score)}", "if(game.i>=game.qs.length){game.state='over';setBest(quizKind,game.score)}")
    rep("  else if(mode==='snake'||mode==='dino'||mode==='words'||mode==='simon'){stopGame();setMode('games')}",
        "  else if(mode==='words'){stopGame();setMode('quiz')}\n  else if(mode==='quiz')setMode('games');\n  else if(mode==='snake'||mode==='dino'||mode==='simon'){stopGame();setMode('games')}")
    rep("    case 'words':wordsKey(k);break;", "    case 'quiz':quizKey(k);break;\n    case 'words':wordsKey(k);break;")
    rep("    case 'words':rows=wordsRows(n);break;", "    case 'quiz':rows=quizRows(n);break;\n    case 'words':rows=wordsRows(n);break;")
    rep("  if(mode==='words'&&item)return wordsPick(+item.dataset.i);",
        "  if(mode==='quiz'&&item){const i=+item.dataset.i,r=item.getBoundingClientRect();   // the right part (the ◂ ▸) changes difficulty\n"
        "    if(e.clientX>r.left+r.width*.6){quizSel=i;return quizStep(i,1)}return quizOpen(i)}\n  if(mode==='words'&&item)return wordsPick(+item.dataset.i);")

    # ---------- the input method ----------
    rep('// ---------- boot ----------', rd('ime-ko.js').strip() + '\n\n' + rd('tutor-ko.js').strip() + '\n\n' + rd('quiz-ko.js').strip() + '\n\n// ---------- boot ----------')
    return s


def main():
    src = open(sys.argv[1], encoding='utf-8').read()
    out = sys.argv[2]
    fonts = json.load(open(os.path.join(out, 'faces.json'), encoding='utf-8'))
    for ed in ('ko', 'en-ko'):
        d = os.path.join(out, ed)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(build(src, ed, fonts))
        print('built', ed)


if __name__ == '__main__':
    main()
