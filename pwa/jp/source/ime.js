// ================= JAPANESE INPUT (Plainwrite-J) =================
// A small input method in the spirit of the 1980s word processors: kana go into an underlined
// "preedit" in the text, Space converts it to kanji, and the choices for the highlighted part
// cycle along the bottom line, the same way status messages show there.
//   Kana input (Control Panel → Keyboard settings → Kana input):
//     romaji  – type Hepburn or kunrei romaji (ka, shi, tsu, kya, nn…)
//     jis     – JIS kana layout, たていすかんな (by physical key, like a Japanese keyboard)
//     nicola  – NICOLA thumb shift (親指シフト): thumb keys are Muhenkan / Option / Alt (left) and Henkan / Space (right)
//   Conversion uses SKK-JISYO.L (GPL v2 or later, SKK Development Team), in dict-ja.txt.
// Physical keyboards only: phone keyboards bring their own Japanese input, and Plainwrite-J leaves them alone.
// Everything here uses var: render() can run before this block does, and must find empty state, not an error.
var IME_LEARN_KEY='plainwrite-j-learn-v1';
var comp=null;        // composition: {start, len, kana, raw, pos, conv}
var DICT=null,dictP=null,dictFailed=false,LEARN={};
try{LEARN=JSON.parse(localStorage.getItem(IME_LEARN_KEY)||'{}')||{}}catch(e){LEARN={}}
const imeOn=()=>S.imeOn!==false&&on;
const imeKanaMode=()=>['romaji','jis','nicola'].includes(S.imeKana)?S.imeKana:'romaji';
const IME_MODES=['hira','kata','wide','off'];
const imeMode=()=>S.imeOn===false?'off':(['kata','wide'].includes(S.imeMode)?S.imeMode:'hira');
const KANA_MODES=['romaji','jis','nicola'];
// ---------- kana tables ----------
const toKata=s=>s.replace(/[ぁ-ゖゝゞ]/g,c=>String.fromCharCode(c.charCodeAt(0)+0x60));
const toHira=s=>s.replace(/[ァ-ヶヽヾ]/g,c=>String.fromCharCode(c.charCodeAt(0)-0x60));
const HALF_KATA={'。':'｡','「':'｢','」':'｣','、':'､','・':'･','ー':'ｰ','゛':'ﾞ','゜':'ﾟ'};
'ヲァィゥェォャュョッ'.split('').forEach((c,i)=>HALF_KATA[c]=String.fromCharCode(0xff66+i));
'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン'.split('').forEach((c,i)=>HALF_KATA[c]=String.fromCharCode(0xff71+i));
function toHalfKata(s){return[...toKata(s)].map(c=>{if(HALF_KATA[c])return HALF_KATA[c];
  const d=c.normalize('NFD');if(d.length===2&&HALF_KATA[d[0]])return HALF_KATA[d[0]]+(d[1]==='゙'?'ﾞ':'ﾟ');
  if(c==='ヴ')return'ｳﾞ';return c}).join('')}
const toWide=s=>s.replace(/[!-~]/g,c=>String.fromCharCode(c.charCodeAt(0)+0xfee0)).replace(/ /g,'　');
const toNarrow=s=>s.replace(/[！-～]/g,c=>String.fromCharCode(c.charCodeAt(0)-0xfee0)).replace(/　/g,' ');
// romaji → kana
const ROMA={};
(function(){const V='aiueo';
  const row=(c,ks)=>{ks.split(' ').forEach((k,i)=>{if(k!=='-')ROMA[c+V[i]]=k})};
  row('','あ い う え お');row('k','か き く け こ');row('g','が ぎ ぐ げ ご');row('s','さ し す せ そ');row('z','ざ じ ず ぜ ぞ');
  row('t','た ち つ て と');row('d','だ ぢ づ で ど');row('n','な に ぬ ね の');row('h','は ひ ふ へ ほ');row('b','ば び ぶ べ ぼ');
  row('p','ぱ ぴ ぷ ぺ ぽ');row('m','ま み む め も');row('y','や い ゆ いぇ よ');row('r','ら り る れ ろ');row('l','ぁ ぃ ぅ ぇ ぉ');
  row('x','ぁ ぃ ぅ ぇ ぉ');row('w','わ うぃ う うぇ を');row('f','ふぁ ふぃ ふ ふぇ ふぉ');row('v','ゔぁ ゔぃ ゔ ゔぇ ゔぉ');
  row('j','じゃ じ じゅ じぇ じょ');row('q','くぁ くぃ く くぇ くぉ');row('c','か し く せ こ');
  const yo=(c,base)=>{ROMA[c+'ya']=base+'ゃ';ROMA[c+'yi']=base+'ぃ';ROMA[c+'yu']=base+'ゅ';ROMA[c+'ye']=base+'ぇ';ROMA[c+'yo']=base+'ょ'};
  yo('k','き');yo('g','ぎ');yo('s','し');yo('z','じ');yo('t','ち');yo('c','ち');yo('d','ぢ');yo('n','に');yo('h','ひ');yo('b','び');
  yo('p','ぴ');yo('m','み');yo('r','り');yo('j','じ');yo('f','ふ');yo('v','ゔ');yo('x','');yo('l','');
  Object.assign(ROMA,{shi:'し',sha:'しゃ',shu:'しゅ',she:'しぇ',sho:'しょ',chi:'ち',cha:'ちゃ',chu:'ちゅ',che:'ちぇ',cho:'ちょ',tsu:'つ',
    tsa:'つぁ',tsi:'つぃ',tse:'つぇ',tso:'つぉ',fu:'ふ',ji:'じ',ja:'じゃ',ju:'じゅ',jo:'じょ',je:'じぇ',
    thi:'てぃ',thu:'てゅ',tha:'てゃ',the:'てぇ',tho:'てょ',dhi:'でぃ',dhu:'でゅ',dha:'でゃ',dhe:'でぇ',dho:'でょ',
    twu:'とぅ',dwu:'どぅ',whu:'う',wha:'うぁ',whi:'うぃ',whe:'うぇ',who:'うぉ',wyi:'ゐ',wye:'ゑ',
    xtu:'っ',ltu:'っ',xtsu:'っ',ltsu:'っ',xka:'ゕ',xke:'ゖ',lka:'ゕ',lke:'ゖ',xwa:'ゎ',lwa:'ゎ',xn:'ん',nn:'ん',"n'":'ん',
    kwa:'くゎ',gwa:'ぐゎ',qwa:'くぁ',
    '-':'ー',',':'、','.':'。','[':'「',']':'」','/':'・','~':'〜','!':'！','?':'？',
    'zh':'←','zj':'↓','zk':'↑','zl':'→','z.':'…','z,':'‥','z-':'〜','z[':'『','z]':'』','z/':'・','z ':'　'})})();
const ROMA_PREFIX=new Set();for(const k of Object.keys(ROMA))for(let i=1;i<k.length;i++)ROMA_PREFIX.add(k.slice(0,i));
// kana → romaji (for F9/F10), longest first
const KANA_ROMA=(()=>{const m={};for(const[r,k]of Object.entries(ROMA)){if(!/^[a-z']+$/.test(r)||r[0]==='l'||r[0]==='x'&&k.length>1)continue;
    if(!(k in m)||r.length<m[k].length||(r.length===m[k].length&&/^(sh|ch|ts|f|j)/.test(r)))m[k]=r}
  m['ん']='nn';m['っ']='xtu';m['ー']='-';return m})();
function kanaToRoma(s){let o='',i=0;s=toHira(s);
  while(i<s.length){if(s[i]==='っ'&&i+1<s.length){const n=kanaToRoma(s.slice(i+1,i+3)).replace(/^[^a-z]*/,'');if(n&&!/^[aiueon]/.test(n)){o+=n[0];i++;continue}}
    const two=s.slice(i,i+2);if(two.length===2&&KANA_ROMA[two]){o+=KANA_ROMA[two];i+=2;continue}
    o+=KANA_ROMA[s[i]]!=null?KANA_ROMA[s[i]]:s[i];i++}
  return o}
// JIS kana layout (たていすかんな), by physical key. [normal, shift]
const JIS_KANA={Digit1:'ぬ',Digit2:'ふ',Digit3:'あぁ',Digit4:'うぅ',Digit5:'えぇ',Digit6:'おぉ',Digit7:'やゃ',Digit8:'ゆゅ',Digit9:'よょ',Digit0:'わを',
  Minus:'ほ',Equal:'へ',IntlYen:'ー',KeyQ:'た',KeyW:'て',KeyE:'いぃ',KeyR:'す',KeyT:'か',KeyY:'ん',KeyU:'な',KeyI:'に',KeyO:'ら',KeyP:'せ',
  BracketLeft:'゛',BracketRight:'゜「',KeyA:'ち',KeyS:'と',KeyD:'し',KeyF:'は',KeyG:'き',KeyH:'く',KeyJ:'ま',KeyK:'の',KeyL:'り',
  Semicolon:'れ',Quote:'け',Backslash:'む」',KeyZ:'つっ',KeyX:'さ',KeyC:'そ',KeyV:'ひ',KeyB:'こ',KeyN:'み',KeyM:'も',
  Comma:'ね、',Period:'る。',Slash:'め・',IntlRo:'ろ',Backquote:'ろー'};   // Backquote: ろ and ー on keyboards without the JIS ろ and ¥ keys
// NICOLA thumb shift: [alone, left thumb, right thumb]
const NICOLA={};
(function(){const rows=[
  ['KeyQ KeyW KeyE KeyR KeyT KeyY KeyU KeyI KeyO KeyP BracketLeft','。かたこさらちくつ，、','ぁえりゃれぱぢぐづぴ゛','　がだござよにるまぇ゜'],
  ['KeyA KeyS KeyD KeyF KeyG KeyH KeyJ KeyK KeyL Semicolon','うしてけせはときいん','をあなゅもばどぎぽ　','ゔじでげぜみおのょっ'],
  ['KeyZ KeyX KeyC KeyV KeyB KeyN KeyM Comma Period Slash','．ひすふへめそねほ・','ぅーろやぃぷぞぺぼ゜','　びずぶべぬゆむわぉ']];
  for(const[codes,a,l,r]of rows)codes.split(' ').forEach((c,i)=>{NICOLA[c]=[a[i],l[i]==='　'?a[i]:l[i],r[i]==='　'?a[i]:r[i]]});
  '1234567890'.split('').forEach((d,i)=>NICOLA['Digit'+d]=[d,'？／〜「」［］（）『'[i],'！＿＠＃＄％＾＆＊』'[i]]);
  NICOLA.Minus=['ー','―','ー'];})();
const NICOLA_LEFT=['NonConvert','Lang2','AltLeft'],NICOLA_RIGHT=['Convert','Lang1','Space'];
const DAKU={};
(function(){const a='かきくけこさしすせそたちつてとはひふへほう',b='がぎぐげござじずぜぞだぢづでどばびぶべぼゔ';
  for(let i=0;i<a.length;i++){DAKU[a[i]+'゛']=b[i];DAKU[toKata(a[i])+'゛']=toKata(b[i])}
  const h='はひふへほ',p='ぱぴぷぺぽ';for(let i=0;i<5;i++){DAKU[h[i]+'゜']=p[i];DAKU[toKata(h[i])+'゜']=toKata(p[i])}})();
// ---------- dictionary ----------
function loadDict(){if(DICT||dictP)return dictP;
  dictP=fetch('dict-ja.txt').then(r=>{if(!r.ok)throw 0;return r.text()}).then(txt=>{const m=new Map();let i=0;
    while(i<txt.length){let e=txt.indexOf('\n',i);if(e<0)e=txt.length;const tab=txt.indexOf('\t',i);
      if(tab>i&&tab<e)m.set(txt.slice(i,tab),txt.slice(tab+1,e));i=e+1}
    DICT=m;if(comp&&comp.wantConv){comp.wantConv=false;imeConvert()}else render()}).catch(()=>{dictFailed=true;dictP=null});
  return dictP}
// a dictionary entry: {common: in the medium dictionary, cands}
function dentry(k){const v=DICT&&DICT.get(k);if(!v)return null;const common=v[0]==='*';return{common,cands:(common?v.slice(1):v).split('/')}}
// readings to keep in kana by default: words that are normally written without kanji
const KEEP=new Set('これ それ あれ どれ この その あの どの ここ そこ あそこ どこ こちら そちら あちら どちら こんな そんな あんな どんな する した して します しない ある あり あります ない なく なかった いる います いた いない です でした だ だった でしょう ます ました ません こと もの とき ため よう ところ など ほど まで ので のに けど から ね よ よね な か ありがとう すみません こんにちは こんばんは おはよう さようなら はい いいえ ええ うん まだ もう また すぐ とても ちょっと たくさん いつ だれ なに なん いくつ いくら もし でも しかし そして それから だから ただ ちゃんと きっと やはり やっぱり くらい ぐらい ばかり だけ しか いい よい ございます ください くださる いただく いただきます よろしく ほしい ほら ほんとう みんな あまり'.split(' '));
const PARTS=['は','が','を','に','へ','と','で','や','の','も','か','ね','よ','な','から','まで','より','など','って','だけ','しか','ので','のに','けど','けれど','ながら','ほど','くらい','ぐらい','ばかり','には','では','とは','へは','からは','までは','にも','でも','とも','へも','からも','のは','のが','のを','のも','かも','だ','です','でした','だった','でしょう','である','じゃ','さん','ちゃん','くん','たち','ら','ですね','ですか','でしたね','だね','だよ','ね','よね'];
const PARTSET=new Set(PARTS);
const AUX=['','ます','ました','ません','ませんでした','ましょう','ない','なかった','なければ','なくて','た','たい','たかった','たら','たり','て','ては','ても','てい','ている','ています','ていた','ていました','ていない','てある','てあります','てしまう','てしまった','てください','てくれ','てくれる','てもらう','だ','だら','で','でいる','でいます','でいた','でいました','でしまう','でください','ば','る','れる','られる','れた','られた','れて','られて','せる','させる','う','よう','く','くて','くない','かった','ければ','さ','そう','そうだ','し','ず','ぬ','い','き','け','こう','たく','ちゃう','ちゃった','す','すぎる','れます','られます','れている','られている','れています','られています'];
// 一段 verbs (見ます = みm): SKK files them under the first kana of the helper verb
const ICHI=['ます','ました','ません','ませんでした','ましょう','ない','なかった','なければ','なくて','た','たい','たかった','たら','たり','て','ては','ても','ている','ています','ていた','ていました','ていない','てある','てしまう','てください','る','れる','られる','れば','よう','ず','ろ','させる','させます','られます'];
const ichiOK=s=>ICHI.some(a=>s.startsWith(a)&&particleTail(s.slice(a.length)));
const SURU=['する','します','しました','しません','している','しています','していた','していました','した','して','しない','しよう','しましょう','させる','される','できる','できます','できない','した'];
const PSTART='はがをにへとでもやのかね';
// a loanword ends at most two kana after its last ー or small vowel, and those don't start with a particle
const loanEnd=h=>{const m=h.search(/[ーぁぃぅぇぉゔ][^ーぁぃぅぇぉゔ]*$/),after=h.slice(m+1);return after.length<=2&&!PSTART.includes(after[0]||'x')};
const LOAN=/^[\u3041-\u3096]*ー[\u3041-\u3096ー]*$|[ぁぃぅぇぉ]|ゔ/;   // a long-vowel mark or a small vowel: likely a foreign word
// a hiragana tail made of okurigana (+ helper verbs) and up to two particles
function tailOK(s){if(s==='')return true;for(const a of AUX){if(!s.startsWith(a))continue;const r=s.slice(a.length);
    if(r==='')return true;if(a.length===1&&!'いくさ'.includes(a))continue;   // a lone okurigana kana takes no particles after it
    if(PARTSET.has(r))return true;for(const p of PARTS)if(r.startsWith(p)&&PARTSET.has(r.slice(p.length)))return true}return false}
const particleTail=s=>s===''||PARTSET.has(s)||PARTS.some(p=>s.startsWith(p)&&PARTSET.has(s.slice(p.length)));
// what may follow a noun: particles, or する and its forms (勉強します)
const nounTail=s=>particleTail(s)||SURU.some(x=>s.startsWith(x)&&particleTail(s.slice(x.length)));
// consonant letter SKK uses for an okurigana kana (書く = かk)
function okuriLetter(k){if(k==='っ')return't';if(k==='ん')return'n';const r=kanaToRoma(k);if(!r||!/^[a-z]/.test(r))return null;
  if(/^[aiueo]/.test(r))return r[0];if(r.startsWith('sh'))return's';if(r.startsWith('ch'))return't';if(r.startsWith('ts'))return't';if(r.startsWith('j'))return'z';if(r.startsWith('f'))return'h';return r[0]}
// cost of one segment (文節); lower is better. Longer dictionary words, common words (SKK-JISYO.M) and a
// segment that ends in a particle or helper verb are preferred, like the 2-segment longest-match rule of old word processors.
const segCost=(len,common,tail,r)=>10-.5*Math.min(len,8)-(common?1.5:0)-(tail?1.5:0)+(!common&&PSTART.includes(r[0])?2:0)+(len<2?2:0);
// every way to read a stretch of kana as one segment
function segOptions(r){const o=[];   // {cost, cands}
  if(!DICT)return[{cost:20,cands:[]}];
  if(KEEP.has(r))o.push({cost:segCost(r.length,true,false,r),cands:[r]});
  const ex=dentry(r);if(ex)o.push({cost:segCost(r.length,ex.common,false,r),cands:ex.cands});
  for(let k=r.length-1;k>=1;k--){const t=r.slice(k);if(!nounTail(t))continue;const head=r.slice(0,k);
    if(KEEP.has(head))o.push({cost:segCost(k,true,true,r),cands:[r]});
    const e=dentry(head);if(e)o.push({cost:segCost(k,e.common,true,r),cands:e.cands.map(c=>c+t)})}
  for(let k=1;k<r.length&&k<=8;k++){const L=r[k]==='は'?null:okuriLetter(r[k]);if(!L)continue;const e=dentry(r.slice(0,k)+L);if(!e)continue;
    const tail=r.slice(k);if(tail.length===2&&'いくきけさしすうずぬるば'.includes(tail[1])&&!/[しじ]/.test(tail[0]))continue;   // 新しい, 美しく; not 干らく
    if(tail.length>10||!((tail.length>1||/[うくぐすつぬぶむるいきしちにびみりぎじ]/.test(tail))&&tailOK(tail.slice(1))||ichiOK(tail)))continue;
    o.push({cost:segCost(k+1,e.common,tail.length>1,r),cands:e.cands.map(c=>c+tail)})}
  if(PARTSET.has(r)||(r.length>1&&tailOK(r)))o.push({cost:11,cands:[r]});
  // loanwords not in the dictionary (こんぴゅーたー): katakana, with any particles after them left as they are
  for(let k=r.length;k>=2;k--){const t=r.slice(k),head=r.slice(0,k);if(!LOAN.test(head)||!nounTail(t)||!loanEnd(head))continue;
    o.push({cost:segCost(k,false,!!t,head)+2,cands:[toKata(head)+t]})}
  if(!o.length)o.push({cost:r.length===1?12:20+2*r.length,cands:[]});
  return o}
// split a reading into segments (文節): fewest and best-matching pieces
function segment(r){const n=r.length,best=Array(n+1).fill(Infinity),from=Array(n+1).fill(-1);best[0]=0;
  for(let i=0;i<n;i++){if(best[i]===Infinity)continue;
    for(let j=i+1;j<=n&&j-i<=16;j++){const c=Math.min(...segOptions(r.slice(i,j)).map(x=>x.cost));if(best[i]+c<best[j]){best[j]=best[i]+c;from[j]=i}}}
  const cuts=[];for(let j=n;j>0;j=from[j])cuts.unshift(from[j]);cuts.push(n);
  const segs=[];for(let k=0;k+1<cuts.length;k++)segs.push(r.slice(cuts[k],cuts[k+1]));return segs}
function candsFor(r){const out=[],add=c=>{if(c&&!out.includes(c))out.push(c)};
  for(const c of LEARN[r]||[])add(c);
  if(S.imeMode==='kata')add(toKata(r));
  const opts=segOptions(r).sort((a,b)=>a.cost-b.cost);for(const o of opts)for(const c of o.cands)add(c);
  add(r);add(toKata(r));
  if(/[a-z0-9]/i.test(r)){add(toWide(r));add(toNarrow(r))}
  return out}
function learn(r,c){if(!r||!c)return;const L=(LEARN[r]||[]).filter(x=>x!==c);L.unshift(c);LEARN[r]=L.slice(0,4);
  const keys=Object.keys(LEARN);if(keys.length>3000)delete LEARN[keys[0]];
  try{localStorage.setItem(IME_LEARN_KEY,JSON.stringify(LEARN))}catch(e){}}
// ---------- the composition in the text ----------
function compText(){if(!comp)return'';if(comp.conv)return comp.conv.segs.map(s=>s.cands[s.i]).join('');
  const k=S.imeMode==='kata'?toKata(comp.kana):comp.kana;return k.slice(0,comp.pos)+comp.raw+k.slice(comp.pos)}
function compShow(){const v=compText();ta.setRangeText(v,comp.start,comp.start+comp.len,'end');comp.len=v.length;
  let c=comp.start+v.length;
  if(!comp.conv)c=comp.start+comp.pos+comp.raw.length;
  else{let p=comp.start;for(let k=0;k<=comp.conv.cur;k++)p+=comp.conv.segs[k].cands[comp.conv.segs[k].i].length;c=p}
  ta.setSelectionRange(c,c);if(!comp.len&&!comp.raw)comp=null;syncFile();scanTextGroups();render()}
function compStart(){if(comp)return;const a=ta.selectionStart,b=ta.selectionEnd;if(a!==b)ta.setRangeText('',a,b,'start');
  comp={start:ta.selectionStart,len:0,kana:'',raw:'',pos:0,conv:null};if(!DICT)loadDict()}
// class for a text position inside the composition (wordRows draws it)
function imeCls(p){if(!comp||p<comp.start||p>=comp.start+comp.len)return'';if(!comp.conv)return'pre';
  let q=comp.start;for(let k=0;k<comp.conv.segs.length;k++){const s=comp.conv.segs[k],l=s.cands[s.i].length;if(p<q+l)return k===comp.conv.cur?'pre seg':'pre';q+=l}return'pre'}
function addKana(s){compStart();if(comp.conv)return;
  if(s==='゛'||s==='゜'){const prev=comp.kana[comp.pos-1],d=prev&&DAKU[prev+s];if(d){comp.kana=comp.kana.slice(0,comp.pos-1)+d+comp.kana.slice(comp.pos);return compShow()}}
  comp.kana=comp.kana.slice(0,comp.pos)+s+comp.kana.slice(comp.pos);comp.pos+=s.length;compShow()}
// romaji: letters wait in comp.raw until they make a kana
function addRoma(ch){compStart();if(comp.conv)return;comp.raw+=ch;
  for(let guard=0;comp.raw&&guard<8;guard++){const r=comp.raw;
    if(ROMA[r]!=null&&!(r==='n'||ROMA_PREFIX.has(r)&&r!=='nn')){put(ROMA[r]);comp.raw='';break}
    if(ROMA_PREFIX.has(r))break;
    if(r.length>=2&&r[0]===r[1]&&/[bcdfghjklmpqrstvwxyz]/.test(r[0])){put('っ');comp.raw=r.slice(1);continue}
    if(r[0]==='n'&&r.length>=2&&!/[aiueoy']/.test(r[1])){put('ん');comp.raw=r.slice(1);continue}
    if(ROMA[r]!=null){put(ROMA[r]);comp.raw='';break}
    put(r[0]);comp.raw=r.slice(1)}
  compShow()
  function put(k){comp.kana=comp.kana.slice(0,comp.pos)+k+comp.kana.slice(comp.pos);comp.pos+=k.length}}
function flushRaw(){if(!comp||!comp.raw)return;let r=comp.raw;comp.raw='';
  if(r==='n')r='ん';comp.kana=comp.kana.slice(0,comp.pos)+r+comp.kana.slice(comp.pos);comp.pos+=r.length}
function imeCommit(){if(!comp)return false;flushRaw();
  if(comp.conv)for(const s of comp.conv.segs)if(s.i>0||s.learn)learn(s.r,s.cands[s.i]);
  const v=compText();ta.setRangeText(v,comp.start,comp.start+comp.len,'end');const end=comp.start+v.length;comp=null;
  ta.setSelectionRange(end,end);syncFile();setTimeout(scanTextGroups,0);render();return true}
function imeCancel(){if(!comp)return;ta.setRangeText('',comp.start,comp.start+comp.len,'end');comp=null;syncFile();render()}
function imeConvert(){if(!comp)return;flushRaw();if(!comp.kana){compShow();return}
  if(!DICT&&!dictFailed){comp.wantConv=true;loadDict();if(dictP){flash(t('ime_loading'));return}}
  const r=toHira(comp.kana),segs=segment(r);
  comp.conv={segs:segs.map(x=>({r:x,cands:candsFor(x),i:0})),cur:0};compShow()}
function imeLiteral(text){if(!comp)return;flushRaw();comp.conv={segs:[{r:toHira(comp.kana),cands:[text],i:0,learn:false}],cur:0};compShow()}
// re-split from the current segment, with its length changed by d
function imeResize(d){const C=comp.conv,s=C.segs[C.cur],rest=C.segs.slice(C.cur).map(x=>x.r).join(''),len=s.r.length+d;
  if(len<1||len>rest.length)return;
  const head={r:rest.slice(0,len),cands:candsFor(rest.slice(0,len)),i:0},tail=rest.slice(len)?segment(rest.slice(len)).map(x=>({r:x,cands:candsFor(x),i:0})):[];
  C.segs=C.segs.slice(0,C.cur).concat([head],tail);compShow()}
// F6–F10: hiragana, katakana, half-width katakana, wide romaji, narrow romaji
function imeFkey(k){if(!comp)return false;flushRaw();
  const C=comp.conv,r=C?C.segs[C.cur].r:toHira(comp.kana);
  const out={F6:r,F7:toKata(r),F8:toHalfKata(r),F9:toWide(kanaToRoma(r)),F10:kanaToRoma(r)}[k];if(out==null)return false;
  if(!C)return imeLiteral(out),true;const s=C.segs[C.cur];if(!s.cands.includes(out))s.cands.push(out);s.i=s.cands.indexOf(out);s.learn=false;compShow();return true}
// ---------- candidates on the bottom line ----------
var candPage=[];   // [start, end) of each page of the current segment's candidates
function candPages(s){const pages=[];let i=0;const room=maxW-textW(' 99/99 ');
  while(i<s.cands.length){let w=0,j=i;while(j<s.cands.length&&j-i<9){const cw=textW(`${j-i+1} ${s.cands[j]}  `);if(j>i&&w+cw>room)break;w+=cw;j++}pages.push([i,j]);i=j}
  return pages}
function candRow(){const s=comp.conv.segs[comp.conv.cur],pages=candPages(s),p=pages.find(([a,b])=>s.i>=a&&s.i<b)||pages[0];
  let h='';for(let j=p[0];j<p[1];j++){const lab=`${j-p[0]+1} ${s.cands[j]}`;h+=(j===s.i?`<span class="csel">${plain(lab)}</span>`:plain(lab))+(j+1<p[1]?'  ':'')}
  return`<span class="inv blk split"><span>${h}</span><span>${s.i+1}/${s.cands.length}</span></span>`}
function imeBar(){return!!(comp&&comp.conv&&mode==='word')}
function imePick(j){const C=comp.conv,s=C.segs[C.cur],p=candPages(s).find(([a,b])=>s.i>=a&&s.i<b);if(!p||p[0]+j>=p[1])return;
  s.i=p[0]+j;s.learn=true;if(C.cur<C.segs.length-1)C.cur++;compShow()}
// ---------- keys ----------
var thumb={L:0,R:0,used:false,last:null};   // NICOLA: when each thumb went down, and the last letter typed
const TOGGLE_KEYS=['Zenkaku','Hankaku','ZenkakuHankaku','KanjiMode','Alphanumeric','Eisu','Lang1','Lang2','Hiragana','Katakana','HiraganaKatakana','KanaMode','Romaji'];
function setImeMode(m){imeCommit();if(m==='off')S.imeOn=false;else{S.imeOn=true;S.imeMode=m}save();imeBadge();
  if(m!=='off')loadDict()}
function imeToggleKey(e){const k=e.key,c=e.code;
  if(c==='Lang1'||k==='Hiragana'||k==='KanaMode'&&!e.shiftKey)return setImeMode('hira'),true;
  if(c==='Lang2'||k==='Eisu'||k==='Alphanumeric')return setImeMode('off'),true;
  if(k==='Katakana')return setImeMode('kata'),true;
  if(k==='HiraganaKatakana')return setImeMode(imeMode()==='kata'?'hira':'kata'),true;
  if(TOGGLE_KEYS.includes(k)||(c==='Backquote'&&e.altKey&&!e.ctrlKey&&!e.metaKey)||(c==='Space'&&e.ctrlKey&&!e.altKey&&!e.metaKey))
    return setImeMode(imeMode()==='off'?(['kata','wide'].includes(S.imeMode)?S.imeMode:'hira'):'off'),true;
  return false}
function quiet(e){e.preventDefault();e.stopImmediatePropagation();lastActive=Date.now();if(autoOffPending&&S.wake)cancelAutoOff()}
function imeKey(e){
  if(!on||mode!=='word'||e.isComposing||e.keyCode===229)return;
  if(e.target!==ta){if(e.target!==document.body||e.type!=='keydown')return;ta.focus({preventScroll:true})}
  if(e.type==='keyup'){if(imeKanaMode()==='nicola'&&S.imeOn!==false)nicolaUp(e);return}
  if(imeToggleKey(e)){quiet(e);playKey('key');return}
  if(S.imeOn===false){if(comp){imeCommit()}return}
  if(imeMode()==='wide'){if(comp)imeCommit();if(!e.metaKey&&!(e.ctrlKey&&!e.altKey))wideKey(e);return}
  const k=e.key;
  // shortcuts and file keys: finish the composition first, then let them through
  if(e.metaKey||(e.ctrlKey&&!e.altKey)){imeCommit();return}
  if(comp&&/^F([6-9]|10)$/.test(k)){quiet(e);imeFkey(k);return}
  if(/^F\d+$/.test(k)){imeCommit();return}
  if(comp&&comp.conv)return convKey(e);
  if(comp)if(preKey(e))return;
  typeKey(e)}
// keys while the kana are underlined (before conversion)
function preKey(e){const k=e.key,K=comp.kana;
  const done=f=>{quiet(e);f();return true};
  if(k==='Enter')return done(()=>{playKey('enter');imeCommit()});
  if(k==='Escape')return done(imeCancel);
  if(k==='Backspace')return done(()=>{if(comp.raw)comp.raw=comp.raw.slice(0,-1);else if(comp.pos>0){comp.kana=K.slice(0,comp.pos-1)+K.slice(comp.pos);comp.pos--}compShow()});
  if(k==='Delete')return done(()=>{flushRaw();comp.kana=comp.kana.slice(0,comp.pos)+comp.kana.slice(comp.pos+1);compShow()});
  if(k==='ArrowLeft')return done(()=>{flushRaw();comp.pos=Math.max(0,comp.pos-1);compShow()});
  if(k==='ArrowRight')return done(()=>{flushRaw();comp.pos=Math.min(comp.kana.length,comp.pos+1);compShow()});
  if(k==='Home')return done(()=>{flushRaw();comp.pos=0;compShow()});
  if(k==='End')return done(()=>{flushRaw();comp.pos=comp.kana.length;compShow()});
  if(k==='ArrowUp'||k==='ArrowDown'||k==='Tab'||k==='PageUp'||k==='PageDown'){imeCommit();return false}
  if((k===' '||k==='Convert')&&imeKanaMode()!=='nicola')return done(()=>{playKey('key');imeConvert()});
  return false}
// keys while converting
function convKey(e){const k=e.key,C=comp.conv,s=C.segs[C.cur];
  const done=f=>{quiet(e);playKey(k==='Enter'?'enter':'key');f()};
  const step=d=>{s.i=(s.i+d+s.cands.length)%s.cands.length;s.learn=true;compShow()};
  if(k==='Enter')return done(imeCommit);
  if(k==='Escape'||k==='Backspace')return done(()=>{comp.kana=C.segs.map(x=>x.r).join('');comp.pos=comp.kana.length;comp.conv=null;compShow()});
  if((k===' '&&!e.shiftKey)||k==='Convert'||k==='ArrowDown')return imeKanaMode()==='nicola'&&k===' '?nicolaSpaceDown(e):done(()=>step(1));
  if((k===' '&&e.shiftKey)||k==='ArrowUp')return done(()=>step(-1));
  if(k==='PageDown'||k==='PageUp')return done(()=>{const pg=candPages(s),i=pg.findIndex(([a,b])=>s.i>=a&&s.i<b),n=pg[(i+(k==='PageDown'?1:-1)+pg.length)%pg.length];s.i=n[0];compShow()});
  if(k==='ArrowLeft'||k==='ArrowRight'){if(e.shiftKey)return done(()=>imeResize(k==='ArrowLeft'?-1:1));
    return done(()=>{C.cur=Math.max(0,Math.min(C.segs.length-1,C.cur+(k==='ArrowLeft'?-1:1)));compShow()})}
  if(/^[1-9]$/.test(k)&&!e.altKey&&(imeKanaMode()!=='jis'||e.code.startsWith('Numpad')))return done(()=>imePick(+k-1));
  if(k==='Home'||k==='End')return done(()=>{C.cur=k==='Home'?0:C.segs.length-1;compShow()});
  if(k==='Tab'||k==='Delete'){quiet(e);return}
  if(imeKanaMode()==='nicola'&&(NICOLA_LEFT.includes(e.code)||NICOLA_RIGHT.includes(e.code)))return nicolaThumbDown(e);
  // anything that types: take the conversion, then start again with this key
  if(k.length===1||NICOLA[e.code]&&imeKanaMode()==='nicola'){imeCommit();typeKey(e)}}
// a key that types something
function typeKey(e){const k=e.key,km=imeKanaMode(),code=e.code;
  if(km==='nicola'){if(NICOLA_LEFT.includes(code)||NICOLA_RIGHT.includes(code))return nicolaThumbDown(e);
    if(NICOLA[code]&&!e.shiftKey&&(!e.altKey||thumb.L)){quiet(e);playKey('key');return nicolaChar(code)}}
  if(e.altKey)return;
  if(km==='jis'&&JIS_KANA[code]&&!e.altKey){const v=JIS_KANA[code];quiet(e);playKey('key');addKana(e.shiftKey&&v[1]?v[1]:v[0]);return}
  if(k===' '){quiet(e);playKey('key');if(comp)return imeConvert();kbdInsert(e.shiftKey?' ':'　');return}
  if(k.length!==1)return;
  // romaji (and the punctuation and digits around it): with a Plainwrite layout on, its letters count
  let ch=k;const L=kbd();if(!L.pass&&L.map[code]){const m=L.map[code];ch=e.shiftKey?m.s:m.n}
  quiet(e);playKey('key');
  if(km!=='romaji'){addKana(/[a-z]/i.test(ch)?ch:(ROMA[ch]||ch));return}
  if(/[A-Z]/.test(ch)){compStart();flushRaw();addKana(ch);return}
  if(/[a-z'\-.,\[\]\/~!?]/.test(ch)||(comp&&comp.raw==='z'))return addRoma(ch);
  addKana(ch)}
// 全角英数: letters, digits and signs type as their full-width forms (ＡＢＣ１２３), a space as a full-width space.
// Cyrillic has no full-width forms in Unicode, so it types as it is (Control Panel → Wide letters can draw it wide).
function wideKey(e){const k=e.key;if(e.altKey||k.length!==1)return;
  let ch=k;const L=kbd();if(!L.pass&&L.map[e.code]){const m=L.map[e.code];ch=e.shiftKey?m.s:m.n}
  quiet(e);playKey('key');kbdInsert(ch===' '?(e.shiftKey?' ':'\u3000'):toWide(ch))}
// ---------- NICOLA thumb shift ----------
const NICOLA_WINDOW=100;   // ms: a letter and a thumb pressed this close together count as one chord
function nicolaChar(code){const now=performance.now(),Lh=thumb.L,Rh=thumb.R;
  let side=0;if(Lh&&(!Rh||Lh>Rh))side=1;else if(Rh)side=2;
  // the thumb was already given to the letter before this one: whichever letter is closer in time keeps it
  const rs=thumb.reshift;thumb.reshift=null;
  if(side&&rs&&comp&&!comp.conv&&now-rs.thumbAt<rs.thumbAt-rs.time&&comp.kana.slice(comp.pos-rs.len,comp.pos)===rs.now){
    comp.kana=comp.kana.slice(0,comp.pos-rs.len)+rs.was+comp.kana.slice(comp.pos);comp.pos+=rs.was.length-rs.len}
  else if(side&&rs)side=0;   // the earlier letter keeps the thumb
  if(side)thumb.used=true;
  const v=NICOLA[code][side];thumb.last={code,time:now,side,len:v.length};
  if(v==='゛'||v==='゜')return addKana(v);
  addKana(v)}
function nicolaThumbDown(e){quiet(e);if(e.repeat)return;const now=performance.now(),side=NICOLA_LEFT.includes(e.code)?'L':'R';
  thumb[side]=now;thumb.used=false;
  // the letter came first: if it was very recent and unshifted, shift it now
  const l=thumb.last;if(l&&!l.side&&now-l.time<NICOLA_WINDOW&&comp&&!comp.conv){
    const v=NICOLA[l.code][side==='L'?1:2],was=comp.kana.slice(comp.pos-l.len,comp.pos);comp.kana=comp.kana.slice(0,comp.pos-l.len)+comp.kana.slice(comp.pos);comp.pos-=l.len;
    thumb.last=null;thumb.used=true;addKana(v);thumb.reshift={time:l.time,thumbAt:now,len:v.length,now:v,was}}}
function nicolaUp(e){const side=NICOLA_LEFT.includes(e.code)?'L':NICOLA_RIGHT.includes(e.code)?'R':null;if(!side)return;
  e.preventDefault();e.stopImmediatePropagation();const used=thumb.used;thumb[side]=0;thumb.reshift=null;
  if(side==='R'&&!used&&(e.code==='Space'||e.code==='Convert')){   // right thumb on its own: space, or convert
    if(comp&&comp.conv){const s=comp.conv.segs[comp.conv.cur];s.i=(s.i+1)%s.cands.length;s.learn=true;compShow()}
    else if(comp)imeConvert();else kbdInsert('　')}
  thumb.used=false}
function nicolaSpaceDown(e){quiet(e);if(!e.repeat){thumb.R=performance.now();thumb.used=false}}
// on-screen keys and taps: finish the composition before anything else happens
function imeFlush(){if(comp)imeCommit()}
function imePress(k){if(!comp)return false;if(k==='Enter'){imeCommit();return true}
  if(comp.conv&&(k==='ArrowLeft'||k==='ArrowRight')){comp.conv.cur=Math.max(0,Math.min(comp.conv.segs.length-1,comp.conv.cur+(k==='ArrowLeft'?-1:1)));compShow();return true}
  if(comp.conv&&(k==='ArrowDown'||k==='ArrowUp')){const s=comp.conv.segs[comp.conv.cur];s.i=(s.i+(k==='ArrowDown'?1:-1)+s.cands.length)%s.cands.length;s.learn=true;compShow();return true}
  if(k==='Escape'){imeCancel();return true}
  imeCommit();return false}
window.addEventListener('keydown',imeKey,true);window.addEventListener('keyup',imeKey,true);
// ---------- the mode badge in the top bar: tap to cycle あ → カ → Ａ → A ----------
const imeBtn=document.getElementById('imeBtn');
function imeBadge(){if(!imeBtn)return;const m=imeMode();imeBtn.textContent={hira:'あ',kata:'カ',wide:'Ａ',off:'A'}[m];
  imeBtn.setAttribute('aria-label',t('ime_badge',t('imm_'+m)));imeBtn.classList.toggle('off',m==='off')}
if(imeBtn){imeBtn.addEventListener('mousedown',e=>e.preventDefault());
  imeBtn.addEventListener('click',()=>{const m=imeMode();setImeMode(IME_MODES[(IME_MODES.indexOf(m)+1)%IME_MODES.length]);flash(t('ime_now',t('imm_'+imeMode())));focusMode()})}
function imeStep(id,d){if(id==='imekana'){S.imeKana=KANA_MODES[(KANA_MODES.indexOf(imeKanaMode())+d+3)%3];save()}
  else{const n=IME_MODES.length,m=IME_MODES[(IME_MODES.indexOf(imeMode())+d+n)%n];setImeMode(m)}}
imeBadge();if(S.imeOn!==false)setTimeout(loadDict,2500);
// =================================================================
