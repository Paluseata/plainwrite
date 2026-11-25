// ----- Plainwrite-J: English Quiz (Games → English Quiz). Same & Opposite is one of its quizzes; the others are below. -----
// Each quiz has its own difficulty (◂ ▸ on it) and its own best score. They all play on the Same & Opposite screen.
// Easy: three choices. Normal: four. Hard: four, all of them look-alikes.
var QUIZZES=[{k:'words',l:'g_words'},{k:'q_ja2en',l:'q_ja2en'},{k:'q_en2ja',l:'q_en2ja'},{k:'q_past',l:'q_past'},{k:'q_plural',l:'q_plural'},{k:'q_spell',l:'q_spell'}];
var quizSel=0,quizKind='words';
// Japanese and English, by subject (Hard picks the wrong answers from the same subject)
var QZ_VOCAB=[
  [['犬','dog'],['猫','cat'],['鳥','bird'],['魚','fish'],['馬','horse'],['牛','cow'],['豚','pig'],['羊','sheep'],['うさぎ','rabbit'],['くま','bear']],
  [['水','water'],['米','rice'],['パン','bread'],['卵','egg'],['肉','meat'],['牛乳','milk'],['お茶','tea'],['塩','salt'],['砂糖','sugar'],['りんご','apple']],
  [['目','eye'],['耳','ear'],['口','mouth'],['手','hand'],['足','foot'],['頭','head'],['鼻','nose'],['歯','tooth'],['髪','hair'],['顔','face']],
  [['山','mountain'],['川','river'],['海','sea'],['空','sky'],['雨','rain'],['雪','snow'],['風','wind'],['花','flower'],['木','tree'],['星','star']],
  [['家','house'],['学校','school'],['駅','station'],['本','book'],['机','desk'],['窓','window'],['車','car'],['電車','train'],['傘','umbrella'],['時計','clock']],
  [['朝','morning'],['夜','night'],['今日','today'],['明日','tomorrow'],['昨日','yesterday'],['春','spring'],['夏','summer'],['秋','autumn'],['冬','winter'],['週','week']],
  [['赤','red'],['青','blue'],['白','white'],['黒','black'],['緑','green'],['黄色','yellow'],['大きい','big'],['小さい','small'],['新しい','new'],['古い','old']]];
// [word, right answer, look-alikes...]: the first look-alike is the trickiest
var QZ_PAST=[['go','went','gone','goed','wented'],['eat','ate','eaten','eated','ated'],['see','saw','seen','seed','sawed'],['take','took','taken','taked','tooked'],
  ['write','wrote','written','writed','wroted'],['buy','bought','brought','buyed','boughted'],['think','thought','taught','thinked','thoughted'],
  ['catch','caught','cought','catched','caughted'],['bring','brought','bought','bringed','broughted'],['teach','taught','thought','teached','taughted'],
  ['run','ran','run','runned','ranned'],['swim','swam','swum','swimmed','swammed'],['sing','sang','sung','singed','sanged'],['drink','drank','drunk','drinked','dranked'],
  ['begin','began','begun','beginned','begined'],['sleep','slept','sleeped','slepted','sleept'],['keep','kept','keeped','kepted','keept'],
  ['make','made','maked','maded','mayed'],['speak','spoke','spoken','speaked','speeked'],['choose','chose','chosen','choosed','chosed'],
  ['forget','forgot','forgotten','forgetted','forgotted'],['give','gave','given','gived','gaved'],['know','knew','known','knowed','knewed'],
  ['grow','grew','grown','growed','grewed'],['throw','threw','thrown','throwed','threwed'],['break','broke','broken','breaked','broked'],
  ['stand','stood','standed','stooded','stend'],['sit','sat','sitted','satted','sot'],['win','won','winned','wonned','wan'],['lose','lost','losed','lossed','losted'],
  ['find','found','finded','fand','founded'],['tell','told','telled','tolled','tald'],['feel','felt','feeled','fealt','feld'],['fall','fell','fallen','falled','felled']];
var QZ_PLURAL=[['child','children','childs','childrens','childes'],['mouse','mice','mouses','mices','mousen'],['man','men','mans','mens','manes'],
  ['woman','women','womans','womens','womanes'],['foot','feet','foots','feets','footes'],['tooth','teeth','tooths','teeths','toothes'],
  ['goose','geese','gooses','geeses','goosen'],['sheep','sheep','sheeps','sheepes','shoop'],['deer','deer','deers','dear','deeres'],
  ['box','boxes','boxs','boxies','boxen'],['city','cities','citys','cityes','cits'],['baby','babies','babys','babyes','babis'],
  ['knife','knives','knifes','knive','knifs'],['leaf','leaves','leafs','leafes','leavs'],['wife','wives','wifes','wivs','wifs'],
  ['potato','potatoes','potatos','potatoe','potatoies'],['tomato','tomatoes','tomatos','tomatoe','tomatoies'],['ox','oxen','oxes','oxs','oxxen'],
  ['dish','dishes','dishs','dishies','dishen'],['church','churches','churchs','churchies','churchen'],['story','stories','storys','storyes','storis'],
  ['day','days','daies','dayes','dais'],['toy','toys','toies','toyes','tois'],['photo','photos','photoes','photoies','photo'],
  ['piano','pianos','pianoes','pianies','piani'],['life','lives','lifes','livs','lifies'],['wolf','wolves','wolfs','wolfes','wolven'],['loaf','loaves','loafs','loafes','loavs']];
var QZ_SPELL=[['necessary','neccessary','necesary','neccesary'],['separate','seperate','separete','seperete'],['definitely','definately','definitly','defenitely'],
  ['receive','recieve','receeve','resieve'],['believe','beleive','belive','beleve'],['beginning','begining','beginnig','beggining'],
  ['tomorrow','tommorow','tomorow','tommorrow'],['friend','freind','frend','friennd'],['because','becuase','becouse','beacuse'],
  ['library','libary','librery','liberary'],['February','Febuary','Februry','Feburary'],['Wednesday','Wensday','Wednsday','Wedensday'],
  ['government','goverment','govermant','governmant'],['environment','enviroment','enviorment','envirnoment'],['restaurant','restaraunt','resturant','restaurent'],
  ['address','adress','addres','adddress'],['calendar','calender','calandar','calander'],['embarrass','embarass','embaress','embarras'],
  ['occurred','occured','ocurred','occurrd'],['accommodate','accomodate','acommodate','acomodate'],['which','wich','whitch','wihch'],
  ['different','diffrent','diferent','differant'],['interesting','intresting','interessting','intersting'],['probably','probly','probaly','probabley'],
  ['question','questoin','qestion','quetion'],['business','buisness','bussiness','busines'],['weird','wierd','weerd','wiered'],['until','untill','untile','untl']];
var qzShuffle=a=>a.map(x=>[Math.random(),x]).sort((p,q)=>p[0]-q[0]).map(p=>p[1]);
function quizLabel(q){return t(q.l)+'  ◂ '+t('d_'+diff(q.k))+' ▸'}
function quizStep(i,d){const k=QUIZZES[i].k;S.diff=S.diff||{};S.diff[k]=DIFFS[(DIFFS.indexOf(diff(k))+d+3)%3];save();render()}
function quizOpen(i){quizSel=i;quizKind=QUIZZES[i].k;stopGame();game={state:'ready',kind:'words'};wordsStart(true);setMode('words')}
function quizRows(n){return listRows(n,t('q_hdr'),QUIZZES.map(quizLabel),quizSel)}
function quizKey(k){const n=QUIZZES.length;
  if(k==='ArrowUp')quizSel=(quizSel+n-1)%n;else if(k==='ArrowDown')quizSel=(quizSel+1)%n;
  else if(k==='ArrowLeft'||k==='ArrowRight')return quizStep(quizSel,k==='ArrowLeft'?-1:1);
  else if(k==='Enter')return quizOpen(quizSel);render()}
// one question: the right answer plus wrong ones, by difficulty
function qzPick(right,tricky,other){const D=diff(quizKind);let wrong;
  if(D==='hard')wrong=tricky.slice(0,3);
  else if(D==='normal')wrong=[...tricky.slice(0,2),other()];
  else wrong=[tricky[1]||tricky[0],other()];
  wrong=[...new Set(wrong.filter(w=>w&&w!==right))];while(wrong.length<(D==='easy'?2:3)){const o=other();if(o!==right&&!wrong.includes(o))wrong.push(o)}
  return qzShuffle([right,...wrong])}
function quizStart(quiet){const k=quizKind,ja=S.lang==='ja';let qs;
  const vocab=QZ_VOCAB.flatMap((g,gi)=>g.map(p=>[...p,gi]));
  if(k==='q_ja2en'||k==='q_en2ja'){const to=k==='q_ja2en'?1:0,from=1-to;
    qs=qzShuffle(vocab).slice(0,10).map(p=>{const same=qzShuffle(QZ_VOCAB[p[2]].filter(x=>x[to]!==p[to])).map(x=>x[to]);
      const other=()=>vocab[Math.floor(Math.random()*vocab.length)][to];
      // Easy and Normal: wrong answers from any subject; Hard: from the same one (a cat among the animals)
      const tricky=diff(k)==='hard'?same:qzShuffle(vocab.filter(x=>x[to]!==p[to])).slice(0,3).map(x=>x[to]);
      return{hdr:t(k==='q_ja2en'?'qq_ja2en':'qq_en2ja',p[from]),answer:p[to],choices:qzPick(p[to],tricky,other)}})}
  else{const list=k==='q_past'?QZ_PAST:k==='q_plural'?QZ_PLURAL:QZ_SPELL,spell=k==='q_spell';
    qs=qzShuffle(list).slice(0,10).map(r=>{const right=spell?r[0]:r[1],tricky=spell?qzShuffle(r.slice(1)):r.slice(2);
      const other=()=>{const o=list[Math.floor(Math.random()*list.length)];return spell?o[1+Math.floor(Math.random()*(o.length-1))]:o[1]};   // in Spelling, always a misspelling (from Plainwrite-K)
      return{hdr:spell?t('qq_spell'):t(k==='q_past'?'qq_past':'qq_plural',r[0]),answer:right,choices:qzPick(right,tricky,other)}})}
  game={state:'play',kind:'words',score:0,i:0,qs,msg:''};wordSel=0;if(!quiet)render()}
