(()=>{
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const KEY='lockscreen-cat-web:v1';
const PET={cat:{name:'小猫',self:'本猫'},dog:{name:'小狗',self:'本汪'}};
const MOODS={happy:'开心得意',proud:'嘴上不说，尾巴翘起',disdain:'嫌弃',collapsed:'瘫倒',sleepy:'困',nightowl:'熬夜黑眼圈',nodata:'没读到数据'};
const SB=['<3000','3000-6000','6000-10000','>10000'];
const BB=['23点前','23-1点','1点后'];
// 与 iOS 版 ToneRule 的常量一致
const GOOD_STEPS=6000,BAD_STEPS=3000;

const def={pet:'cat',steps:4560,bed:300,dur:450,noSleep:false,phase:'auto',view:'lock',streak:false,roll:Math.random(),picks:{}};
let S=Object.assign({},def);
try{Object.assign(S,JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}};

const fmt=n=>n.toLocaleString('en-US');
const hhmm=m=>{m=((m%1440)+1440)%1440;return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')};
const bedClock=()=>(18*60+S.bed)%1440;
// 入睡时间距 18:00 的分钟数 → 桶
const bedBucket=m=>m<300?BB[0]:m<420?BB[1]:BB[2];
const stepBucket=n=>n<3000?SB[0]:n<6000?SB[1]:n<=10000?SB[2]:SB[3];
const realPhase=()=>{const h=new Date().getHours();return h>=5&&h<12?'morning':h>=12&&h<18?'daytime':'evening'};
const phase=()=>S.phase==='auto'?realPhase():S.phase;
const PH={morning:'早上',daytime:'白天',evening:'晚上'};

function mood(ph){
  const hasBed=!S.noSleep, st=S.steps;
  if(ph==='morning'){
    if(!hasBed) return st>0?'proud':'nodata';
    const b=bedBucket(S.bed);return b===BB[0]?'happy':b===BB[1]?'sleepy':'nightowl';
  }
  if(st<=0) return 'nodata';
  if(ph==='daytime') return st>=5000?'happy':st>=2500?'proud':st>=800?'disdain':'collapsed';
  return st>10000?'happy':st>=GOOD_STEPS?'proud':st>=BAD_STEPS?'disdain':'collapsed';
}
function caption(ph){
  if(ph==='morning'){
    if(!S.noSleep) return '昨晚 '+hhmm(bedClock())+' 入睡';
    return S.steps>0?'已走 '+fmt(S.steps)+' 步':'没读到数据';
  }
  return S.steps>0?'已走 '+fmt(S.steps)+' 步':'今天还一步没走';
}
// 基调：夸 / 吐槽
function tone(){
  const st=S.steps;
  const force=S.streak; // 连续吐槽满 3 天 → 今天强制夸
  if(S.noSleep){return force?'enc':(S.roll<0.5?'enc':'roast')}
  const b=bedBucket(S.bed);
  if(st>=GOOD_STEPS&&b===BB[0]) return 'enc';
  if(st<BAD_STEPS&&b===BB[2]) return force?'enc':'roast';
  if(force) return 'enc';
  return S.roll<0.5?'enc':'roast';
}
function pool(t,sb,bb){
  const L=LINES[S.pet];
  if(bb){const g=(t==='enc'?L.enc:L.roast)[sb];if(g&&g[bb]&&g[bb].length)return g[bb];}
  else{const r=(t==='enc'?L.encNo:L.roastNo)[sb];if(r&&r.length)return r;}
  return ['今天先记下了。'];
}
const render=s=>s.replace(/\{steps\}/g,fmt(S.steps)).replace(/\{bedtime\}/g,hhmm(bedClock()));
const NOSTEP=()=>PET[S.pet].name+'也懒得说你，今天你还一步没走。';
function current(force){
  if(S.steps<=0) return {text:'今天你还一步没走，'+PET[S.pet].name+'也懒得说你。',tone:'neutral'};
  const t=tone(), sb=stepBucket(S.steps), bb=S.noSleep?null:bedBucket(S.bed);
  const k=[S.pet,t,sb,bb||'-'].join('|');
  const p=pool(t,sb,bb);
  let rec=S.picks[k]||{cur:null,used:[]};
  if(force||!rec.cur||!p.includes(rec.cur)){
    let fresh=p.filter(x=>!rec.used.includes(x)&&x!==rec.cur);
    if(!fresh.length){rec.used=[];fresh=p.filter(x=>x!==rec.cur);}
    if(!fresh.length)fresh=p;
    rec.cur=fresh[Math.floor(Math.random()*fresh.length)];
    rec.used=[...rec.used,rec.cur].slice(-7);
    S.picks[k]=rec;save();
  }
  return {text:render(rec.cur),tone:t};
}

function why(ph,tn){
  const st=S.steps, sb=stepBucket(st), pn=PET[S.pet].name;
  const parts=[];
  if(st<=0){return `今天一步没走，${pn}没东西可评，只会固定说一句。表情看<em>${PH[ph]}</em>的规则：${ph==='morning'&&!S.noSleep?'早上看睡眠':'没数据就一脸问号'}。`;}
  parts.push(`步数 <em>${fmt(st)}</em> 落在「${sb}」`+(S.noSleep?'，没有睡眠，用“没读到睡眠”那一组句子。':`，入睡 <em>${hhmm(bedClock())}</em> 落在「${bedBucket(S.bed)}」。`));
  let r;
  if(!S.noSleep&&st>=GOOD_STEPS&&bedBucket(S.bed)===BB[0]) r='走得多、睡得早，一定夸。';
  else if(!S.noSleep&&st<BAD_STEPS&&bedBucket(S.bed)===BB[2]) r=S.streak?'本来必吐槽，但已经连着被吐槽三天，今天网开一面，改夸。':'走得少、睡得晚，一定吐槽。';
  else if(S.streak) r='已经连着被吐槽三天，今天强制夸一次。';
  else r='不在极端区间，夸还是吐槽一半一半。'+(S.roll<0.5?'今天抽到了夸。':'今天抽到了吐槽。');
  parts.push(r);
  parts.push(`表情按<em>${PH[ph]}</em>看${ph==='morning'?'睡眠':'步数'}：${MOODS[mood(ph)]}。`);
  return parts.join('');
}

const imgSrc=(m,mono)=>`img/${S.pet}-${m}${mono?'-mono':''}.png`;
function paint(){
  const ph=phase(), m=mood(ph), cur=current(false), cap=caption(ph);
  const pn=PET[S.pet].name;
  $$('#petSeg button').forEach(b=>b.classList.toggle('on',b.dataset.pet===S.pet));
  $$('#phaseSeg button').forEach(b=>b.classList.toggle('on',b.dataset.phase===S.phase));
  $$('#viewSeg button').forEach(b=>b.classList.toggle('on',b.dataset.view===S.view));
  $('#screen').className='screen '+S.view;
  $('#stepsNum').value=S.steps; $('#steps').value=Math.min(S.steps,25000);
  $('#bed').value=S.bed; $('#dur').value=S.dur;
  $('#noSleep').checked=S.noSleep; $('#streak').checked=S.streak;
  $('#sleepBlock').classList.toggle('off',S.noSleep);
  $('#bedLabel').textContent=hhmm(bedClock());
  $('#durLabel').textContent=Math.floor(S.dur/60)+' 小时 '+(S.dur%60?S.dur%60+' 分':'');
  const wake=bedClock()+S.dur;
  $('#wakeHint').textContent=`大约 ${hhmm(wake)} 醒。规则只看入睡时间，睡多久不影响吐槽。`;
  $('#phaseHint').textContent=S.phase==='auto'?`此刻是${PH[realPhase()]}。早上看睡眠，白天和晚上看步数。`:'早上看睡眠，白天和晚上看步数。';
  $$('input[type=range]').forEach(r=>r.style.setProperty('--p',((r.value-r.min)/(r.max-r.min)*100)+'%'));
  $('#why').innerHTML=why(ph,cur.tone);
  $('#moodName').textContent=`${pn}此刻的表情：${MOODS[m]}`;

  const line=cur.text;
  const now=new Date(), wk='日一二三四五六'[now.getDay()];
  $('#lockDate').textContent=`${now.getMonth()+1}月${now.getDate()}日 星期${wk}`;
  $('#lockClock').textContent=hhmm(now.getHours()*60+now.getMinutes()).replace(/^0/,'');
  $('#stTime').textContent=hhmm(now.getHours()*60+now.getMinutes()).replace(/^0/,'');
  $('#lwImg').src=imgSrc(m,true); $('#lwCap').textContent=cap; $('#lwLine').textContent=line;
  $('#mwImg').src=imgSrc(m,false); $('#mwCap').textContent=cap; $('#mwLine').textContent=line;
  $('#mwDay').textContent=`${now.getMonth()+1}月${now.getDate()}日 · ${pn}观察日记`;
  $('#mwBadge').textContent=cur.tone==='roast'?'今日吐槽':cur.tone==='enc'?'今日鼓励':'';
  $('#mwBadge').style.display=cur.tone==='neutral'?'none':'';
  $$('#petSeg img').forEach(i=>i.alt='');
  window.__state={m,line,cap,tone:cur.tone};
  save();
}

// 控件
$$('#petSeg button').forEach(b=>b.onclick=()=>{S.pet=b.dataset.pet;paint()});
$$('#phaseSeg button').forEach(b=>b.onclick=()=>{S.phase=b.dataset.phase;paint()});
$$('#viewSeg button').forEach(b=>b.onclick=()=>{S.view=b.dataset.view;paint()});
$('#steps').oninput=e=>{S.steps=+e.target.value;paint()};
$('#stepsNum').oninput=e=>{S.steps=Math.max(0,Math.min(99999,Math.round(+e.target.value||0)));paint()};
$('#bed').oninput=e=>{S.bed=+e.target.value;paint()};
$('#dur').oninput=e=>{S.dur=+e.target.value;paint()};
$('#noSleep').onchange=e=>{S.noSleep=e.target.checked;paint()};
$('#streak').onchange=e=>{S.streak=e.target.checked;paint()};
$('#shuffle').onclick=()=>{current(true);paint()};
$('#reroll').onclick=()=>{S.roll=Math.random();paint()};

// 桌面图标（装饰）
$('#apps').innerHTML=['锁屏萌宠','照片','天气','备忘录','日历','相机','音乐','设置'].map((n,i)=>
  i===0?`<div class="app"><img src="img/app-icon.png" alt=""><span>${n}</span></div>`:`<div class="app"><i style="opacity:${.55+((i*37)%40)/100}"></i><span>${n}</span></div>`).join('');

// 分享卡片
const cv=$('#card'), cx=cv.getContext('2d');
function loadImg(src){return new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.onerror=()=>r(null);i.src=src})}
function rr(x,y,w,h,r){cx.beginPath();cx.moveTo(x+r,y);cx.arcTo(x+w,y,x+w,y+h,r);cx.arcTo(x+w,y+h,x,y+h,r);cx.arcTo(x,y+h,x,y,r);cx.arcTo(x,y,x+w,y,r);cx.closePath()}
function wrap(t,max){const out=[];let l='';for(const ch of t){if(cx.measureText(l+ch).width>max&&l){out.push(l);l=ch}else l+=ch}if(l)out.push(l);return out}
const FONT='"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif';
async function drawCard(){
  const st=window.__state, W=1080,H=1560, pn=PET[S.pet].name, now=new Date();
  const img=await loadImg(imgSrc(st.m,false));
  cx.clearRect(0,0,W,H);
  rr(6,6,W-12,H-12,96);cx.fillStyle='#FFF8EE';cx.fill();cx.lineWidth=12;cx.strokeStyle='#F4A04B';cx.stroke();
  cx.fillStyle='#4A2C1D';cx.textBaseline='alphabetic';
  cx.font=`500 44px ${FONT}`;cx.textAlign='left';
  cx.fillText(`${now.getMonth()+1}月${now.getDate()}日 · ${pn}观察日记`,72,148);
  const badge=st.tone==='roast'?'今日吐槽':st.tone==='enc'?'今日鼓励':'';
  if(badge){cx.font=`700 38px ${FONT}`;const w=cx.measureText(badge).width+60;rr(W-72-w,100,w,64,32);cx.fillStyle='#f4a04b40';cx.fill();cx.fillStyle='#4A2C1D';cx.textAlign='center';cx.fillText(badge,W-72-w/2,145);}
  if(img)cx.drawImage(img,W/2-345,210,690,690);
  cx.textAlign='center';cx.font=`700 66px ${FONT}`;
  const ls=wrap(st.line,W-190);let y=1000;
  ls.slice(0,5).forEach(l=>{cx.fillText(l,W/2,y);y+=96});
  cx.font=`600 44px ${FONT}`;cx.fillStyle='#4A2C1Dbf';
  const a=`${fmt(S.steps)} 步`, b=S.noSleep?'没有睡眠记录':`${hhmm(bedClock())} 入睡`;
  cx.fillText(`${a}　·　${b}`,W/2,1380);
  cx.textAlign='right';cx.font=`400 34px ${FONT}`;cx.fillStyle='#4A2C1D80';
  cx.fillText('来自我的锁屏萌宠 · 网页版',W-84,1466);
}
$('#makeCard').onclick=async()=>{await drawCard();$('#modal').hidden=false};
$('#close').onclick=()=>$('#modal').hidden=true;
$('#modal').onclick=e=>{if(e.target.id==='modal')$('#modal').hidden=true};
$('#dl').onclick=()=>{cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=`锁屏萌宠-${PET[S.pet].name}-${new Date().toISOString().slice(0,10)}.png`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000)})};
document.addEventListener('keydown',e=>{if(e.key==='Escape')$('#modal').hidden=true});

setInterval(()=>{if(!document.hidden)paint()},30000);
paint();
})();
