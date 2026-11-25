// ================= HANGUL AND HANJA TUTORS (Plainwrite-K, edit freely) =================
// Two more applets that use the Typing Tutor's screens with their own lessons: the Hangul Tutor
// (자리 연습 by Dubeolsik rows, then words and short sentences) and the Hanja Tutor (8급 Hanja with
// their meaning and reading, typed with the Hanja key). Speed is counted in keystrokes a minute (타/분).
// Each lesson: key (menu text), words (picked at random to fill a line) or lines, and for Hanja:
// sep (what goes between words), max (longest line) and hint (the line shown above the one to type).
const KO_LESSONS=[
  {key:'les_k_home',ko:true,words:'아이 나라 오리 하나 머리 어머니 오이 나이 마리 허리 하마 미나리 머나먼 호랑이 놀이 엄마 언니 너머 노란 알람 아라리 어린이 할머니 아니오 나라말 아리랑 마라 미리'.split(' ')},
  {key:'les_k_top',ko:true,words:'바다 사자 가방 지도 고기 다리 개미 여자 교실 학교 세상 기자 사과 제비 비행기 도서관 자전거 신발 고양이 거리 소리 저녁 영어 가게 대학생 아버지 시장 가지 여기 저기 사랑 하얀 다섯 생각 기억 소녀 행복'.split(' ')},
  {key:'les_k_bottom',ko:true,words:'커피 치마 크다 우유 구름 휴지 컴퓨터 친구 축구 추석 피아노 트럭 기차 투표 포도 타자기 티셔츠 추위 크기 편지 창문 하늘 우주 노트 칠판 튼튼 부추 특별 그림 음악 운동장'.split(' ')},
  {key:'les_k_shift',ko:true,words:'빵 짜장면 딸기 꽃 씨앗 얘기 예쁘다 쓰레기 까치 뿌리 아빠 오빠 땅콩 찌개 떡볶이 꿈 싸움 쌀 똑똑 깜짝 빨래 짝꿍 예전 걔 쑥 뜰 꼬리 씨름 쪽지 계획'.split(' ')},
  {key:'les_k_words',ko:true,words:'한글 글쇠 문장 워드프로세서 파일 저장 화면 커서 맞춤법 원고지 공책 연필 지우개 책상 도서관 이야기 생각 시간 오늘 내일 어제 마음 사랑 친구 가족 바람 햇빛 바다 산책 기차역 여행 노래 그림 편지'.split(' ')},
  {key:'les_k_sent',ko:true,lines:['가는 말이 고와야 오는 말이 곱다','낮말은 새가 듣고 밤말은 쥐가 듣는다','세 살 버릇 여든까지 간다','백지장도 맞들면 낫다',
    '천 리 길도 한 걸음부터','원숭이도 나무에서 떨어진다','발 없는 말이 천 리 간다','티끌 모아 태산','고래 싸움에 새우 등 터진다',
    '오늘도 한 쪽씩 써 봅시다','쓴 글은 저절로 저장됩니다','먼저 쓰고 나중에 고치세요','손은 기본 자리에 두세요','작은 화면에 큰 이야기']}];
// 8급 한자: the fifty of the lowest grade of the Hanja proficiency test, with meaning and reading (훈음)
const HJ8='校학교 교|敎가르칠 교|九아홉 구|國나라 국|軍군사 군|金쇠 금|南남녘 남|女계집 녀|年해 년|大큰 대|東동녘 동|六여섯 륙|萬일만 만|母어미 모|木나무 목|門문 문|民백성 민|白흰 백|父아비 부|北북녘 북|四넉 사|山메 산|三석 삼|生날 생|西서녘 서|先먼저 선|小작을 소|水물 수|室집 실|十열 십|五다섯 오|王임금 왕|外바깥 외|月달 월|二두 이|人사람 인|一한 일|日날 일|長긴 장|弟아우 제|中가운데 중|靑푸를 청|寸마디 촌|七일곱 칠|土흙 토|八여덟 팔|學배울 학|韓한국 한|兄형 형|火불 화|百일백 백|千일천 천|男사내 남'.split('|');
const HUNEUM={};for(const x of HJ8)HUNEUM[x[0]]=x.slice(1);
// a line's hint: 배울 학 · 학교 교 (two-character words: 한국 한·나라 국)
const hjHint=s=>[...s.replace(/ /g,'')].map(c=>HUNEUM[c]||c).join(' · ');
const HJ_LESSONS=[
  {key:'les_h_8a',ko:true,exact:true,sep:'',max:4,hint:hjHint,words:[...'校敎九國軍金南女年大東六萬母木門民白父北四山三生西']},
  {key:'les_h_8b',ko:true,exact:true,sep:'',max:4,hint:hjHint,words:[...'先小水室十五王外月二人一日長弟中靑寸七土八學韓兄火']},
  {key:'les_h_num',ko:true,exact:true,sep:'',max:5,hint:hjHint,words:[...'一二三四五六七八九十百千萬']},
  {key:'les_h_words',ko:true,exact:true,sep:' ',max:8,hint:hjHint,words:'韓國 大學 學生 先生 父母 兄弟 東西 南北 山水 中國 人生 生日 校門 國民 女王 外國 火山 水門 長女 白金 大門 南山 敎室 軍人 土木 萬年 一生 王室 國土 中學 長男 東門 西山'.split(' ')}];
var TUTOR='en',LESSONS_EN=null;
function setTutor(k){if(!LESSONS_EN)LESSONS_EN=LESSONS.slice();TUTOR=k;LESSONS.splice(0,LESSONS.length,...(k==='ko'?KO_LESSONS:k==='hj'?HJ_LESSONS:LESSONS_EN));kwSel=0}
// keystrokes for one character on Dubeolsik: 한 = ㅎ ㅏ ㄴ = 3; a Hanja is its reading plus the Hanja key and a pick
function strokes(c){if(c>='가'&&c<='힣'){const n=c.charCodeAt(0)-0xac00,v=JUNG[Math.floor(n/28)%21],tt=JONG[n%28];
    return 1+('ㅘㅙㅚㅝㅞㅟㅢ'.includes(v)?2:1)+(!tt?0:TSPLIT[tt]?2:1)}
  if(isHanja(c)&&RDICT&&RDICT.get(c))return strokes(RDICT.get(c)[0])+2;return 1}
// the tutor line without the syllable still being typed, so a half-built syllable doesn't count as a mistake
function kwTyped(){const v=cmd.value;if(comp&&comp.el===cmd&&!comp.conv)return v.slice(0,comp.start)+v.slice(comp.start+comp.len);return v}
// =========================================================================================
