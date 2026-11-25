// ---------- key labels (Plainwrite-K) ----------
// The top row and the file keys are labelled in Korean or English: Control Panel → Device labels,
// which until it's set follows the menu language. Labels are fitted again whenever the keys change size.
const KEY_KO={power:'전원',print:'인쇄',spell:'맞춤법<br>검사',find:'찾기',clear:'파일<br>지우기',home:'처음',end:'끝',applets:'애플릿',send:'보내기'};
const keyOrig=new Map();
function devLang(){return S.devLang==='ko'||S.devLang==='en'?S.devLang:(lang().id==='ko'?'ko':'en')}
function labelKeys(){const ko=devLang()==='ko';
  document.querySelectorAll('.keys.top .k').forEach(b=>{const k=b.dataset.k;if(!keyOrig.has(b))keyOrig.set(b,[b.innerHTML,b.classList.contains('two')]);
    const[html,two]=keyOrig.get(b);
    if(ko&&KEY_KO[k]&&KEY_KO[k].includes('<br>')){b.innerHTML='<span class="kl">'+KEY_KO[k]+'</span>';b.classList.add('two')}   // stacked, like spell/check
    else if(ko&&KEY_KO[k]){const sm=b.querySelector('small');b.innerHTML=(sm?sm.outerHTML:'<small>&nbsp;</small>')+'<span class="kl">'+KEY_KO[k]+'</span>';b.classList.remove('two')}
    else{b.innerHTML=html;b.classList.toggle('two',two)}});
  fk.querySelectorAll('.k').forEach((b,i)=>{b.innerHTML='<span class="kl">'+(ko?'파일 '+(i+1):'file '+(i+1))+'</span>'});
  fitKeys()}
// Any label wider than its key (the file row especially, on phones) is squeezed sideways to fit.
function fitKeys(){for(const s of document.querySelectorAll('.keys .kl')){const b=s.parentElement,cs=getComputedStyle(b);
    const room=b.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)-4;s.style.setProperty('--sq',1);
    const w=s.offsetWidth;if(w>room&&room>0)s.style.setProperty('--sq',(room/w).toFixed(3))}}
labelKeys();
if(window.ResizeObserver){const ro=new ResizeObserver(()=>fitKeys());ro.observe(fk);ro.observe(document.querySelector('.keys.top'))}
if(document.fonts){document.fonts.addEventListener('loadingdone',()=>fitKeys());document.fonts.ready.then(fitKeys)}

// ================= KOREAN INPUT (Plainwrite-K) =================
// A small Hangul input method for physical keyboards. The syllable being built is underlined in the
// text; it's finished as soon as the next one starts, the way Korean input has always worked.
// The Hanja key (한자, F9 or Right Ctrl on its own) turns the syllable before the cursor, or each
// syllable of a selection, into Hanja; the choices line up on the bottom line, like status messages.
//   Keyboard (Control Panel → Keyboard settings → Hangul keyboard):
//     2      – Dubeolsik 두벌식, the standard KS X 5002 layout
//     390    – Sebeolsik 390 세벌식
//     3f     – Sebeolsik Final 세벌식 최종
//     roma   – romanized: one Latin letter for one jamo (han'gug'eo → 한국어)
//   Layouts go by physical key, so they work whatever the computer's own layout is.
//   Hanja come from LibreOffice's Hangul–Hanja table (MPL 2.0), in dict-ko.txt, most-used first.
// Phone keyboards bring their own Korean input, and Plainwrite-K leaves them alone.
// Everything here uses var: render() can run before this block does, and must find empty state, not an error.
var IME_LEARN_KEY='plainwrite-k-learn-v1';
var comp=null;   // {start, len, s:{L,V,T}, hist, raw, conv}
var DICT=null,RDICT=null,dictP=null,dictFailed=false,LEARN={},wantHanja=false;
try{LEARN=JSON.parse(localStorage.getItem(IME_LEARN_KEY)||'{}')||{}}catch(e){LEARN={}}
const IME_MODES=['hang','wide','off'];
const imeMode=()=>S.imeOn===false?'off':(S.imeMode==='wide'?'wide':'hang');
const KBD_MODES=['2','390','3f','roma'];
const imeKbd=()=>KBD_MODES.includes(S.imeKbd)?S.imeKbd:'2';
// ---------- jamo ----------
const CHO='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ',JUNG='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ';
const JONG=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];
const VCOMB={'ㅗㅏ':'ㅘ','ㅗㅐ':'ㅙ','ㅗㅣ':'ㅚ','ㅜㅓ':'ㅝ','ㅜㅔ':'ㅞ','ㅜㅣ':'ㅟ','ㅡㅣ':'ㅢ'};
const TCOMB={'ㄱㅅ':'ㄳ','ㄴㅈ':'ㄵ','ㄴㅎ':'ㄶ','ㄹㄱ':'ㄺ','ㄹㅁ':'ㄻ','ㄹㅂ':'ㄼ','ㄹㅅ':'ㄽ','ㄹㅌ':'ㄾ','ㄹㅍ':'ㄿ','ㄹㅎ':'ㅀ','ㅂㅅ':'ㅄ'};
const TSPLIT={};for(const[k,v]of Object.entries(TCOMB))TSPLIT[v]=k;
const LDBL={'ㄱㄱ':'ㄲ','ㄷㄷ':'ㄸ','ㅂㅂ':'ㅃ','ㅅㅅ':'ㅆ','ㅈㅈ':'ㅉ'};            // 세벌식: the same first consonant twice
const TCOMB3=Object.assign({'ㄱㄱ':'ㄲ','ㅅㅅ':'ㅆ'},TCOMB);
const isHangul=c=>c>='가'&&c<='힣';
const isHanja=c=>/[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/.test(c);
function sylText(s){if(s.L&&s.V)return String.fromCharCode(0xac00+(CHO.indexOf(s.L)*21+JUNG.indexOf(s.V))*28+JONG.indexOf(s.T));return s.L+s.V+s.T}
const EMPTY=()=>({L:'',V:'',T:''});
// ---------- layouts, by physical key ----------
// Dubeolsik: [normal, shift]
const DUB={KeyQ:'ㅂㅃ',KeyW:'ㅈㅉ',KeyE:'ㄷㄸ',KeyR:'ㄱㄲ',KeyT:'ㅅㅆ',KeyY:'ㅛ',KeyU:'ㅕ',KeyI:'ㅑ',KeyO:'ㅐㅒ',KeyP:'ㅔㅖ',
  KeyA:'ㅁ',KeyS:'ㄴ',KeyD:'ㅇ',KeyF:'ㄹ',KeyG:'ㅎ',KeyH:'ㅗ',KeyJ:'ㅓ',KeyK:'ㅏ',KeyL:'ㅣ',KeyZ:'ㅋ',KeyX:'ㅌ',KeyC:'ㅊ',KeyV:'ㅍ',KeyB:'ㅠ',KeyN:'ㅜ',KeyM:'ㅡ'};
// the US key each physical key stands for: [normal, shift]
const US={Backquote:'`~',Digit1:'1!',Digit2:'2@',Digit3:'3#',Digit4:'4$',Digit5:'5%',Digit6:'6^',Digit7:'7&',Digit8:'8*',Digit9:'9(',Digit0:'0)',Minus:'-_',Equal:'=+',
  BracketLeft:'[{',BracketRight:']}',Backslash:'\\|',Semicolon:';:',Quote:'\'"',Comma:',<',Period:'.>',Slash:'/?'};
for(const c of'abcdefghijklmnopqrstuvwxyz')US['Key'+c.toUpperCase()]=c+c.toUpperCase();
// Sebeolsik 390 and Final, as in libhangul: the ASCII key each character comes from, 0x21–0x7E.
// Conjoining jamo say which part they are: U+1100… first consonants, U+1161… vowels, U+11A8… last consonants.
const SEB={
  '390':[0x11bd,0x22,0x23,0x24,0x25,0x26,0x1110,0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x2e,0x1169,0x110f,0x11c2,0x11bb,0x11b8,0x116d,0x1172,0x1163,0x1168,0x1174,0x116e,
    0x3a,0x1107,0x32,0x3d,0x33,0x3f,0x40,0x11ae,0x21,0x11b1,0x11b0,0x11bf,0x11a9,0x2f,0x27,0x38,0x34,0x35,0x36,0x31,0x30,0x39,0x3e,0x11c1,0x1164,0x11ad,0x3b,0x37,
    0x11b6,0x11c0,0x11b9,0x3c,0x11be,0x5b,0x5c,0x5d,0x5e,0x5f,0x60,0x11bc,0x116e,0x1166,0x1175,0x1167,0x1161,0x1173,0x1102,0x1106,0x110b,0x1100,0x110c,0x1112,
    0x1109,0x110e,0x1111,0x11ba,0x1162,0x11ab,0x1165,0x1103,0x1169,0x11af,0x11a8,0x1105,0x11b7,0x7b,0x7c,0x7d,0x7e],
  '3f':[0x11a9,0xb7,0x11bd,0x11b5,0x11b4,0x201c,0x1110,0x27,0x7e,0x201d,0x2b,0x2c,0x29,0x2e,0x1169,0x110f,0x11c2,0x11bb,0x11b8,0x116d,0x1172,0x1163,0x1168,0x1174,0x116e,
    0x34,0x1107,0x2c,0x3e,0x2e,0x21,0x11b0,0x11ae,0x3f,0x11bf,0x11b2,0x11ac,0x11b1,0x1164,0x30,0x37,0x31,0x32,0x33,0x22,0x2d,0x38,0x39,0x11c1,0x11b6,0x11ad,0x11b3,0x36,
    0x11aa,0x11c0,0x11b9,0x35,0x11be,0x28,0x3a,0x3c,0x3d,0x3b,0x2a,0x11bc,0x116e,0x1166,0x1175,0x1167,0x1161,0x1173,0x1102,0x1106,0x110b,0x1100,0x110c,0x1112,
    0x1109,0x110e,0x1111,0x11ba,0x1162,0x11ab,0x1165,0x1103,0x1169,0x11af,0x11a8,0x1105,0x11b7,0x25,0x5c,0x2f,0x203b]};
// a 세벌식 key: {r:'L'|'V'|'T', j: the letter} or {ch: a character to type}
function sebKey(code,shift){const u=US[code];if(!u)return null;const a=(shift?u[1]:u[0])||u[0],v=SEB[imeKbd()][a.charCodeAt(0)-0x21];if(v==null)return null;
  if(v>=0x1100&&v<=0x1112)return{r:'L',j:CHO[v-0x1100]};if(v>=0x1161&&v<=0x1175)return{r:'V',j:JUNG[v-0x1161]};
  if(v>=0x11a8&&v<=0x11c2)return{r:'T',j:JONG[v-0x11a7]};return{ch:String.fromCharCode(v)}}
// ---------- romanized input: one letter for one jamo ----------
const R_V=[['yae','ㅒ'],['yeo','ㅕ'],['wae','ㅙ'],['weo','ㅝ'],['ae','ㅐ'],['ya','ㅑ'],['eo','ㅓ'],['ye','ㅖ'],['wa','ㅘ'],['oe','ㅚ'],['yo','ㅛ'],['wo','ㅝ'],
  ['we','ㅞ'],['wi','ㅟ'],['yu','ㅠ'],['eu','ㅡ'],['ui','ㅢ'],['a','ㅏ'],['e','ㅔ'],['i','ㅣ'],['o','ㅗ'],['u','ㅜ']];
const R_C=[['kk','ㄲ'],['kh','ㅋ'],['ph','ㅍ'],['th','ㅌ'],['tt','ㄸ'],['pp','ㅃ'],['ss','ㅆ'],['jj','ㅉ'],['ch','ㅊ'],['ng','ㅇ'],['g','ㄱ'],['k','ㅋ'],['n','ㄴ'],['d','ㄷ'],['t','ㅌ'],['r','ㄹ'],['l','ㄹ'],
  ['m','ㅁ'],['b','ㅂ'],['p','ㅍ'],['s','ㅅ'],['j','ㅈ'],['h','ㅎ'],['c','ㅊ'],['f','ㅍ'],['v','ㅂ'],['z','ㅈ'],['x','ㅇ'],['q','ㄲ']];
// as a last consonant, k p t read the way Revised Romanization writes them: 학 hak, 밥 bap, 맛 mat (kh ph th give ㅋ ㅍ ㅌ)
const R_FIN={k:'ㄱ',p:'ㅂ',t:'ㅅ'};
// han'gug'eo → 한국어: a consonant between two vowels starts the next syllable; ' ends a syllable;
// ng before a vowel is n + g (hangang → 한강), anywhere else it's ㅇ; leftover letters stay as they are.
function romaToHangul(str){const tk=[];let i=0;
  while(i<str.length){if(str[i]==="'"){tk.push({b:1});i++;continue}
    let m=R_V.find(([r])=>str.startsWith(r,i));if(m){tk.push({v:m[1]});i+=m[0].length;continue}
    m=R_C.find(([r])=>str.startsWith(r,i));if(m){tk.push({c:m[1],r:m[0]});i+=m[0].length;continue}
    tk.push({x:str[i]});i++}
  let out='',cur=null,cl=[];   // cur: the syllable being built; cl: consonants typed since its vowel
  const jamo=()=>{const s=cl.map(x=>x.c).join('');cl=[];return s};
  // the consonants after a vowel become its last consonant (two may join: ㄹ+ㄱ = ㄺ); any more are left as letters
  const close=()=>{if(!cur)return jamo();let a=cl.map(x=>R_FIN[x.r]||x.c),t='';
    if(a.length>=2&&TCOMB[a[0]+a[1]]){t=TCOMB[a[0]+a[1]];a=a.slice(2)}else if(a.length&&JONG.includes(a[0])){t=a[0];a=a.slice(1)}
    cur.T=t;const s=sylText(cur)+a.join('');cur=null;cl=[];return s};
  for(const x of tk){
    if(x.b){out+=close();continue}
    if(x.x){out+=close()+x.x;continue}
    if(x.c){cl.push(x);continue}
    let onset='ㅇ';
    if(cl.length){const last=cl.pop();
      if(last.r==='ng'&&cur){cl.push({c:'ㄴ',r:'n'});onset='ㄱ'}else onset=last.c}
    out+=close();cur={L:onset,V:x.v,T:''}}
  return out+close()}
// ---------- dictionary ----------
function loadDict(){if(DICT||dictP)return dictP;
  dictP=fetch('dict-ko.txt').then(r=>{if(!r.ok)throw 0;return r.text()}).then(txt=>{const m=new Map(),rm=new Map();
    for(const line of txt.split('\n')){const tab=line.indexOf('\t');if(tab<1)continue;const k=line.slice(0,tab),v=[...line.slice(tab+1)];m.set(k,v);
      for(const h of v){const r=rm.get(h);if(r){if(!r.includes(k))r.push(k)}else rm.set(h,[k])}}
    DICT=m;RDICT=rm;if(wantHanja){wantHanja=false;hanjaKey()}else render()}).catch(()=>{dictFailed=true;dictP=null;if(wantHanja){wantHanja=false;flash(t('hj_nodict'))}});
  return dictP}
// the choices for one character: Hanja for a Hangul syllable, the readings (and other Hanja) for a Hanja
function hanjaFor(c){if(!DICT)return null;
  if(isHangul(c)){const v=DICT.get(c);if(!v)return null;const out=[c];for(const h of LEARN[c]||[])if(v.includes(h)&&!out.includes(h))out.push(h);for(const h of v)if(!out.includes(h))out.push(h);return out}
  if(isHanja(c)){const r=RDICT.get(c);if(!r)return null;return[c,...r]}
  return null}
function learn(r,c){if(!r||!c||r===c||!isHangul(r))return;const L=(LEARN[r]||[]).filter(x=>x!==c);L.unshift(c);LEARN[r]=L.slice(0,4);
  const keys=Object.keys(LEARN);if(keys.length>3000)delete LEARN[keys[0]];
  try{localStorage.setItem(IME_LEARN_KEY,JSON.stringify(LEARN))}catch(e){}}
// the text the input method types into: the document, or the line in the Hangul and Hanja tutors
function imeTarget(){return mode==='word'?ta:(mode==='keywords'&&kw&&!kw.summary&&TUTOR!=='en')?cmd:null}
const E=()=>comp&&comp.el||imeTarget()||ta;
function after(el=E()){if(el===ta){syncFile();scanTextGroups()}else el.dispatchEvent(new Event('input',{bubbles:true}));render()}
// ---------- the syllable being typed ----------
function compText(){if(!comp)return'';if(comp.conv)return comp.conv.segs.map(s=>s.cands[s.i]).join('');
  if(comp.raw!=null)return romaToHangul(comp.raw);return sylText(comp.s)}
function compShow(){const v=compText();E().setRangeText(v,comp.start,comp.start+comp.len,'end');comp.len=v.length;
  let c=comp.start+v.length;
  if(comp.conv){let p=comp.start;for(let k=0;k<=comp.conv.cur;k++)p+=comp.conv.segs[k].cands[comp.conv.segs[k].i].length;c=p}
  E().setSelectionRange(c,c);if(!comp.len&&!comp.conv)comp=null;after()}
function compStart(){if(comp)return;const a=E().selectionStart,b=E().selectionEnd;if(a!==b)E().setRangeText('',a,b,'start');
  comp={el:imeTarget(),start:E().selectionStart,len:0,s:EMPTY(),hist:[],raw:null,conv:null};if(!DICT)setTimeout(loadDict,0)}
// class for a text position inside the composition (wordRows draws it)
function imeCls(p){if(!comp||p<comp.start||p>=comp.start+comp.len)return'';if(!comp.conv)return'pre';
  let q=comp.start;for(let k=0;k<comp.conv.segs.length;k++){const s=comp.conv.segs[k],l=s.cands[s.i].length;if(p<q+l)return k===comp.conv.cur?'pre seg':'pre';q+=l}return'pre'}
const push=()=>comp.hist.push(Object.assign({},comp.s));
// finish the current syllable: it stays in the text, and a new one starts after it
function nextSyl(){const v=sylText(comp.s);E().setRangeText(v,comp.start,comp.start+comp.len,'end');comp.start+=v.length;comp.len=0;comp.s=EMPTY();comp.hist=[]}
// 두벌식: one key for each letter; a last consonant moves on to the next syllable when a vowel follows
function dubJamo(j){compStart();const s=comp.s;
  if(!JUNG.includes(j)){
    if(s.L&&s.V&&!s.T&&JONG.includes(j)){push();s.T=j}
    else if(s.T&&TCOMB[s.T+j]){push();s.T=TCOMB[s.T+j]}
    else if(!s.L&&!s.V){push();s.L=j}
    else{nextSyl();push();comp.s.L=j}}
  else{
    if(s.V&&!s.T&&VCOMB[s.V+j]){push();s.V=VCOMB[s.V+j]}
    else if(s.L&&!s.V){push();s.V=j}
    else if(s.L&&s.V&&s.T){const sp=TSPLIT[s.T];let keep='',mv=s.T;if(sp){keep=sp[0];mv=sp[1]}
      s.T=keep;nextSyl();comp.s.L=mv;comp.hist=[EMPTY()];push();comp.s.V=j}
    else if(!s.L&&!s.V){push();s.V=j}
    else{nextSyl();push();comp.s.V=j}}
  compShow()}
// 세벌식: every key says which part of the syllable it is
function sebJamo(r,j){compStart();const s=comp.s;
  if(r==='L'){if(!s.L&&!s.V&&!s.T){push();s.L=j}else if(s.L&&!s.V&&!s.T&&LDBL[s.L+j]){push();s.L=LDBL[s.L+j]}else{nextSyl();push();comp.s.L=j}}
  else if(r==='V'){if(!s.V&&!s.T){push();s.V=j}else if(s.V&&!s.T&&VCOMB[s.V+j]){push();s.V=VCOMB[s.V+j]}else{nextSyl();push();comp.s.V=j}}
  else{if(s.V&&!s.T){push();s.T=j}else if(s.T&&TCOMB3[s.T+j]){push();s.T=TCOMB3[s.T+j]}else{nextSyl();push();comp.s.T=j}}
  compShow()}
function romaLetter(ch){compStart();if(comp.raw==null)comp.raw='';comp.raw+=ch;compShow()}
function imeCommit(){if(!comp)return false;
  if(comp.conv)for(const s of comp.conv.segs)if(s.i>0&&s.learn)learn(s.cands[0],s.cands[s.i]);
  const v=compText();E().setRangeText(v,comp.start,comp.start+comp.len,'end');const end=comp.start+v.length,el=E();comp=null;
  el.setSelectionRange(end,end);after(el);return true}
function imeCancel(){if(!comp)return;
  const el=E();
  if(comp.conv){const v=comp.conv.segs.map(s=>s.cands[0]).join('');el.setRangeText(v,comp.start,comp.start+comp.len,'end');const e=comp.start+v.length;comp=null;el.setSelectionRange(e,e)}
  else{el.setRangeText('',comp.start,comp.start+comp.len,'end');comp=null}
  after(el)}
// ---------- Hanja ----------
// The Hanja key converts the syllable being typed, or else each character of the selection, or else the
// character before the cursor. Hanja go back to Hangul the same way.
function hanjaKey(){
  if(comp&&comp.conv){convStep(1);return}
  if(!DICT&&!dictFailed){wantHanja=true;loadDict();if(dictP){flash(t('ime_loading'));return}wantHanja=false}
  if(!DICT){flash(t('hj_nodict'));return}
  let start,text;
  const el=imeTarget();if(!el)return;
  if(comp&&comp.raw!=null){const v=compText();start=comp.start;text=v;comp=null}
  else if(comp){start=comp.start;text=sylText(comp.s);comp=null}
  else{const a=E().selectionStart,b=E().selectionEnd;
    if(a!==b){start=a;text=E().value.slice(a,b)}
    else{const c=E().value[a-1];if(!c){flash(t('hj_none'));return}start=a-1;text=c}}
  const segs=[...text].map(c=>{const h=hanjaFor(c);return{cands:h||[c],i:0,learn:false,ok:!!h}});
  const first=segs.findIndex(s=>s.ok);
  if(first<0){if(comp)comp=null;flash(t('hj_none'));E().setSelectionRange(start+text.length,start+text.length);render();return}
  segs[first].i=1;   // the first Hanja shows straight away; Esc puts the Hangul back
  comp={el,start,len:text.length,s:EMPTY(),hist:[],raw:null,conv:{segs,cur:first}};compShow()}
function convStep(d){const C=comp.conv,s=C.segs[C.cur];s.i=(s.i+d+s.cands.length)%s.cands.length;s.learn=true;compShow()}
function convMove(d){const C=comp.conv;let k=C.cur;do{k+=d}while(k>=0&&k<C.segs.length&&!C.segs[k].ok);
  if(k<0||k>=C.segs.length)return false;C.cur=k;compShow();return true}
// pick a numbered choice, then move on to the next character, or finish after the last
function imePick(j){const C=comp.conv,s=C.segs[C.cur],p=candPages(s).find(([a,b])=>s.i>=a&&s.i<b)||candPages(s)[0];
  if(!p||p[0]+j>=p[1])return;s.i=p[0]+j;s.learn=true;if(!convMove(1))imeCommit()}
// ---------- choices on the bottom line ----------
// "한: 1 韓 2 漢 3 寒 …  2/31": the Hangul first, then the Hanja, nine to a page
function candPages(s){const pages=[];let i=1;const room=maxW-textW(s.cands[0]+': ')-textW(' 99/99 ');
  while(i<s.cands.length){let w=0,j=i;while(j<s.cands.length&&j-i<9){const cw=textW(`${j-i+1} ${s.cands[j]}  `);if(j>i&&w+cw>room)break;w+=cw;j++}pages.push([i,j]);i=j}
  if(!pages.length)pages.push([0,1]);return pages}
function candRow(){const s=comp.conv.segs[comp.conv.cur],pages=candPages(s),p=pages.find(([a,b])=>s.i>=a&&s.i<b)||pages[0];
  let h=plain(s.cands[0]+': ');for(let j=p[0];j<p[1];j++){const lab=`${j-p[0]+1} ${s.cands[j]}`;h+=(j===s.i?`<span class="csel">${plain(lab)}</span>`:plain(lab))+(j+1<p[1]?'  ':'')}
  return`<span class="inv blk split"><span>${h}</span><span>${s.i}/${s.cands.length-1}</span></span>`}
function imeBar(){return!!(comp&&comp.conv&&mode==='word'&&comp.el===ta)}
// ---------- keys ----------
const TOGGLE_KEYS=['HangulMode','Lang1','KanaMode','Alphanumeric','Eisu','Zenkaku','Hankaku','ZenkakuHankaku'];
const HANJA_KEYS=['HanjaMode','Lang2','KanjiMode'];
function setImeMode(m){imeCommit();if(m==='off')S.imeOn=false;else{S.imeOn=true;S.imeMode=m}save();imeBadge()}
var lone={code:null,other:false};   // Right Alt / Right Ctrl pressed on their own: 한/영 and 한자 on 101-key keyboards
function imeToggleKey(e){const k=e.key,c=e.code;
  if(TOGGLE_KEYS.includes(k)||c==='Lang1'||(c==='Space'&&(e.shiftKey||e.ctrlKey)&&!e.altKey&&!e.metaKey&&!(e.shiftKey&&e.ctrlKey)))
    return setImeMode(imeMode()==='off'?(S.imeMode==='wide'?'wide':'hang'):'off'),true;
  return false}
function quiet(e){e.preventDefault();e.stopImmediatePropagation();lastActive=Date.now();if(autoOffPending&&S.wake)cancelAutoOff()}
function imeKey(e){
  const el=imeTarget();if(!on||!el||e.isComposing||e.keyCode===229)return;
  if(e.target!==el){if(e.target!==document.body||e.type!=='keydown')return;el.focus({preventScroll:true})}
  if(e.type==='keyup'){
    if(lone.code===e.code&&!lone.other){lone.code=null;
      if(e.code==='AltRight'){e.preventDefault();setImeMode(imeMode()==='off'?(S.imeMode==='wide'?'wide':'hang'):'off');flash(t('ime_now',t('imm_'+imeMode())));playKey('key')}
      else if(e.code==='ControlRight'){e.preventDefault();hanjaKey()}}
    return}
  if(e.code==='AltRight'||e.code==='ControlRight'){if(!e.repeat)lone={code:e.code,other:false};return}
  lone.other=true;
  if(imeToggleKey(e)){quiet(e);playKey('key');flash(t('ime_now',t('imm_'+imeMode())));return}
  if(HANJA_KEYS.includes(e.key)||e.code==='Lang2'||(e.key==='F9'&&!e.ctrlKey&&!e.altKey&&!e.metaKey)){quiet(e);playKey('key');hanjaKey();return}
  if(comp&&comp.conv)return convKey(e);
  if(S.imeOn===false){if(comp)imeCommit();return}
  if(imeMode()==='wide'){if(comp)imeCommit();if(!e.metaKey&&!(e.ctrlKey&&!e.altKey))wideKey(e);return}
  // shortcuts and file keys: finish the syllable first, then let them through
  if(e.metaKey||(e.ctrlKey&&!e.altKey)){imeCommit();return}
  if(e.key==='Backspace'&&comp&&!e.altKey){quiet(e);playKey('key');
    if(comp.raw!=null){comp.raw=comp.raw.slice(0,-1);if(!comp.raw){comp.raw=null;comp.s=EMPTY()}}
    else comp.s=comp.hist.length?comp.hist.pop():EMPTY();
    compShow();return}
  if(e.key==='Escape'&&comp){quiet(e);imeCommit();return}
  if(e.altKey){imeCommit();return}
  typeKey(e)}
// keys while choosing Hanja
function convKey(e){const k=e.key,C=comp.conv;
  const done=f=>{quiet(e);playKey(k==='Enter'?'enter':'key');f()};
  if(k==='Enter')return done(imeCommit);
  if(k==='Escape'||k==='Backspace')return done(imeCancel);
  if((k===' '&&!e.shiftKey)||k==='ArrowDown')return done(()=>convStep(1));
  if((k===' '&&e.shiftKey)||k==='ArrowUp')return done(()=>convStep(-1));
  if(k==='PageDown'||k==='PageUp')return done(()=>{const s=C.segs[C.cur],pg=candPages(s),i=pg.findIndex(([a,b])=>s.i>=a&&s.i<b),n=pg[(Math.max(0,i)+(k==='PageDown'?1:-1)+pg.length)%pg.length];s.i=n[0];s.learn=true;compShow()});
  if(k==='ArrowLeft'||k==='ArrowRight')return done(()=>convMove(k==='ArrowLeft'?-1:1));
  if(/^[1-9]$/.test(k)&&!e.altKey&&!e.ctrlKey&&!e.metaKey)return done(()=>imePick(+k-1));
  if(k==='Home'||k==='End'||k==='Tab'||k==='Delete'){quiet(e);return}
  if(/^(Shift|Control|Alt|Meta|CapsLock)$/.test(k))return;
  // anything else: take the Hanja, then carry on with this key
  imeCommit();if(S.imeOn!==false&&imeMode()==='hang'&&!e.metaKey&&!e.ctrlKey&&!e.altKey)typeKey(e)}
// a key that types something
function typeKey(e){const code=e.code,km=imeKbd();
  if(km==='2'){const v=DUB[code];if(v){quiet(e);playKey('key');dubJamo(e.shiftKey&&v[1]?v[1]:v[0]);return}}
  else if(km==='roma'){const L=kbd();let ch=e.key;if(!L.pass&&L.map[code]){const m=L.map[code];ch=e.shiftKey?m.s:m.n}
    if(ch&&ch.length===1&&(/[a-z]/.test(ch)||(ch==="'"&&comp&&comp.raw))){quiet(e);playKey('key');romaLetter(ch);return}}
  else{const x=sebKey(code,e.shiftKey);
    if(x&&x.r){quiet(e);playKey('key');sebJamo(x.r,x.j);return}
    if(x&&x.ch){quiet(e);playKey('key');imeCommit();kbdInsert(x.ch);return}}
  // not a Hangul key: the syllable is finished, and the key does what it always does
  imeCommit()}
// 전각: letters, digits and signs type as their full-width forms (ＡＢＣ１２３), a space as a full-width space.
const toWide=s=>s.replace(/[!-~]/g,c=>String.fromCharCode(c.charCodeAt(0)+0xfee0)).replace(/ /g,'\u3000');
function wideKey(e){const k=e.key;if(e.altKey||k.length!==1)return;
  let ch=k;const L=kbd();if(!L.pass&&L.map[e.code]){const m=L.map[e.code];ch=e.shiftKey?m.s:m.n}
  quiet(e);playKey('key');kbdInsert(ch===' '?(e.shiftKey?' ':'\u3000'):toWide(ch))}
// on-screen keys and taps: finish the syllable before anything else happens
function imeFlush(){if(comp)imeCommit()}
function imePress(k){if(!comp)return false;
  if(comp.conv){if(k==='Enter'){imeCommit();return true}
    if(k==='ArrowLeft'||k==='ArrowRight'){convMove(k==='ArrowLeft'?-1:1);return true}
    if(k==='ArrowDown'||k==='ArrowUp'){convStep(k==='ArrowDown'?1:-1);return true}
    if(k==='Escape'){imeCancel();return true}}
  imeCommit();return false}
window.addEventListener('keydown',imeKey,true);window.addEventListener('keyup',imeKey,true);
// ---------- the mode badge in the top bar: tap to cycle 한 → Ａ → A ----------
const imeBtn=document.getElementById('imeBtn');
function imeBadge(){if(!imeBtn)return;const m=imeMode();imeBtn.textContent={hang:'한',wide:'Ａ',off:'A'}[m];
  imeBtn.setAttribute('aria-label',t('ime_badge',t('imm_'+m)));imeBtn.classList.toggle('off',m==='off')}
if(imeBtn){imeBtn.addEventListener('mousedown',e=>e.preventDefault());
  imeBtn.addEventListener('click',()=>{const m=imeMode();setImeMode(IME_MODES[(IME_MODES.indexOf(m)+1)%IME_MODES.length]);flash(t('ime_now',t('imm_'+imeMode())));focusMode()})}
function imeStep(id,d){if(id==='imekbd'){imeCommit();S.imeKbd=KBD_MODES[(KBD_MODES.indexOf(imeKbd())+d+KBD_MODES.length)%KBD_MODES.length];save()}
  else{const n=IME_MODES.length,m=IME_MODES[(IME_MODES.indexOf(imeMode())+d+n)%n];setImeMode(m)}}
imeBadge();setTimeout(loadDict,2500);
// =================================================================
