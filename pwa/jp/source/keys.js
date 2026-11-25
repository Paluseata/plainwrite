// ---------- key labels (Plainwrite-J) ----------
// The top row and the file keys are labelled in Japanese or English: Control Panel → Device labels,
// which until it's set follows the menu language. Labels are fitted again whenever the keys change size.
const KEY_JA={power:'電源',print:'印刷',spell:'スペル<br>チェック',find:'検索',clear:'ファイル<br>削除',home:'ホーム',end:'エンド',applets:'アプレット',send:'送る'};
const keyOrig=new Map();
function devLang(){return S.devLang==='ja'||S.devLang==='en'?S.devLang:(lang().id==='ja'?'ja':'en')}
function labelKeys(){const ja=devLang()==='ja';
  document.querySelectorAll('.keys.top .k').forEach(b=>{const k=b.dataset.k;if(!keyOrig.has(b))keyOrig.set(b,[b.innerHTML,b.classList.contains('two')]);
    const[html,two]=keyOrig.get(b);
    if(ja&&KEY_JA[k]&&KEY_JA[k].includes('<br>')){b.innerHTML='<span class="kl">'+KEY_JA[k]+'</span>';b.classList.add('two')}   // stacked, like spell/check
    else if(ja&&KEY_JA[k]){const sm=b.querySelector('small');b.innerHTML=(sm?sm.outerHTML:'<small>&nbsp;</small>')+'<span class="kl">'+KEY_JA[k]+'</span>';b.classList.remove('two')}
    else{b.innerHTML=html;b.classList.toggle('two',two)}});
  fk.querySelectorAll('.k').forEach((b,i)=>{b.innerHTML='<span class="kl">'+(ja?'ファイル'+String.fromCharCode(0xff11+i):'file '+(i+1))+'</span>'});
  fitKeys()}
// Any label wider than its key (the file row especially, on phones) is squeezed sideways to fit.
function fitKeys(){for(const s of document.querySelectorAll('.keys .kl')){const b=s.parentElement,cs=getComputedStyle(b);
    const room=b.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)-4;s.style.setProperty('--sq',1);
    const w=s.offsetWidth;if(w>room&&room>0)s.style.setProperty('--sq',(room/w).toFixed(3))}}
labelKeys();
if(window.ResizeObserver){const ro=new ResizeObserver(()=>fitKeys());ro.observe(fk);ro.observe(document.querySelector('.keys.top'))}
if(document.fonts){document.fonts.addEventListener('loadingdone',()=>fitKeys());document.fonts.ready.then(fitKeys)}
