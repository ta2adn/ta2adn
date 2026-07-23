
const C=window.DASHBOARD_CONFIG,$=s=>document.querySelector(s);

function fit(){
  const scale=Math.min(innerWidth/1366,innerHeight/768);
  $('#stage').style.transform=`translateX(-50%) scale(${scale})`;
}
addEventListener('resize',fit);fit();

function tick(){
  const now=new Date();
  $('#clock').textContent=new Intl.DateTimeFormat('tr-TR',{timeZone:C.timezone,hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(now);
  $('#date').textContent=new Intl.DateTimeFormat('tr-TR',{timeZone:C.timezone,weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(now);
}
setInterval(tick,1000);tick();

const radarFrames=[];
let radarIndex=0;
let radarTimer=null;

function radarUrl(frame){
  return `https://www.mgm.gov.tr/FTPDATA/uzal/radar/ist/istppi${frame}.jpg?t=${Date.now()}`;
}

async function loadRadarFrames(){
  radarFrames.length=0;
  const stamp=Date.now();
  for(let i=1;i<=15;i++){
    const img=new Image();
    img.src=`https://www.mgm.gov.tr/FTPDATA/uzal/radar/ist/istppi${i}.jpg?t=${stamp}`;
    radarFrames.push(img);
  }
  radarIndex=0;
  showRadarFrame();
  if(radarTimer)clearInterval(radarTimer);
  radarTimer=setInterval(showRadarFrame,700);
  $('#radarTime').textContent=new Intl.DateTimeFormat('tr-TR',{hour:'2-digit',minute:'2-digit'}).format(new Date());
}

function showRadarFrame(){
  if(!radarFrames.length)return;
  const img=radarFrames[radarIndex];
  if(img.complete && img.naturalWidth>0){
    $('#radarImage').src=img.src;
    radarIndex=(radarIndex+1)%radarFrames.length;
  }else{
    radarIndex=(radarIndex+1)%radarFrames.length;
  }
}

loadRadarFrames();
setInterval(loadRadarFrames,5*60000);

const icons={0:'☀️',1:'🌤️',2:'⛅',3:'☁️',45:'🌫️',48:'🌫️',51:'🌦️',53:'🌦️',55:'🌧️',61:'🌧️',63:'🌧️',65:'🌧️',71:'🌨️',73:'🌨️',75:'🌨️',80:'🌦️',81:'🌧️',82:'⛈️',95:'⛈️',96:'⛈️',99:'⛈️'};

function renderWeather(w){
  if(!w)return;
  $('#temp').textContent=Math.round(w.current.temperature)+'°C';
  $('#condition').textContent=w.current.condition;
  $('#weatherIcon').textContent=icons[w.current.code]||'🌤️';
  $('#feels').textContent=Math.round(w.current.feels_like)+'°C';
  $('#humidity').textContent=w.current.humidity+'%';
  $('#wind').textContent=Math.round(w.current.wind_speed)+' km/sa';
  $('#sunrise').textContent=w.sun.sunrise;
  $('#sunset').textContent=w.sun.sunset;
  $('#moonPhase').textContent=w.moon.phase;
  $('#moonPct').textContent=w.moon.illumination+'%';
  const moon=$('#moonIcon');
  const illumination=Math.max(0,Math.min(100,Number(w.moon.illumination)||0));
  moon.style.setProperty('--illumination',illumination);
  moon.classList.remove('new','full','waxing','waning');
  if(illumination<=2) moon.classList.add('new');
  else if(illumination>=98) moon.classList.add('full');
  else moon.classList.add(w.moon.waxing===false?'waning':'waxing');
  $('#forecast').innerHTML=w.daily.map(d=>`<div class="day"><b>${d.day}</b><span class="ico">${icons[d.code]||'🌤️'}</span><span>${Math.round(d.max)}° / ${Math.round(d.min)}°</span></div>`).join('');
}

function startOfWeek(d=new Date()){
  const x=new Date(d);const day=(x.getDay()+6)%7;x.setHours(0,0,0,0);x.setDate(x.getDate()-day);return x;
}
function sameDate(a,b){return a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate()}
function renderCalendar(events){
  const monday=startOfWeek(), sunday=new Date(monday);sunday.setDate(monday.getDate()+6);
  $('#weekRange').textContent=new Intl.DateTimeFormat('tr-TR',{day:'numeric',month:'long'}).format(monday)+' – '+new Intl.DateTimeFormat('tr-TR',{day:'numeric',month:'long',year:'numeric'}).format(sunday);
  const names=['PZT','SAL','ÇAR','PER','CUM','CMT','PAZ'],now=new Date();
  $('#calendarGrid').innerHTML=Array.from({length:7},(_,i)=>{
    const date=new Date(monday);date.setDate(monday.getDate()+i);
    const dayStart=new Date(date);dayStart.setHours(0,0,0,0);
    const dayEnd=new Date(dayStart);dayEnd.setDate(dayEnd.getDate()+1);
    const dayEvents=(events||[]).filter(e=>{
      const start=new Date(e.start), end=new Date(e.end||e.start);
      return start<dayEnd && end>dayStart;
    }).sort((a,b)=>{
      if(a.all_day!==b.all_day)return a.all_day?-1:1;
      return new Date(a.start)-new Date(b.start);
    });
    const visible=dayEvents.slice(0,12);
    const cards=visible.map(e=>{
      const startsToday=sameDate(new Date(e.start),date);
      const label=e.all_day?'Tüm gün':(startsToday?e.time:'Devam ediyor');
      return `<div class="event ${e.all_day?'all-day':''} ${!startsToday?'continues':''}">
        <span class="event-time">${label}</span>
        <span class="event-title">${escapeHtml(e.title||'Etkinlik')}</span>
      </div>`;
    }).join('');
    const more=dayEvents.length>12?`<div class="more-events">+${dayEvents.length-12} etkinlik daha</div>`:'';
    return `<div class="cal-day ${sameDate(date,now)?'today':''}">
      <div class="cal-head"><span class="cal-name">${names[i]}</span><span class="cal-date">${date.getDate()}</span></div>
      ${dayEvents.length?cards+more:'<div class="empty">Etkinlik yok</div>'}
    </div>`;
  }).join('');
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}

let news=[],newsIndex=0;
function renderNews(){
  if(!news.length)return;const n=news[newsIndex%news.length],card=$('#newsCard');
  card.style.animation='none';void card.offsetWidth;card.style.animation='';
  $('#newsTime').textContent=n.time||'SON';
  $('#newsTitle').textContent=n.title||'';
  $('#newsDescription').textContent=n.description||'';
}
setInterval(()=>{if(news.length){newsIndex=(newsIndex+1)%news.length;renderNews()}},C.newsRotationSeconds*1000);

async function loadData(){
  const bust='?t='+Date.now();
  try{renderWeather(await fetch('data/weather.json'+bust).then(r=>r.json()))}catch(e){console.warn('weather',e)}
  try{renderCalendar(await fetch('data/calendar.json'+bust).then(r=>r.json()))}catch(e){console.warn('calendar',e);renderCalendar([])}
  try{
    const q=await fetch('data/earthquakes.json'+bust).then(r=>r.json());
    $('#quakeList').innerHTML=q.slice(0,5).map(x=>`<div class="quake-row">
      <span>${x.time}</span><span class="mag ${x.magnitude>=4.5?'high':''}">${Number(x.magnitude).toFixed(1)}</span>
      <span>${escapeHtml(x.location)}</span><span>${Number(x.depth).toFixed(1)} km</span><span>${x.ago}</span></div>`).join('');
    $('#quakeUpdated').textContent='Son güncelleme: '+new Intl.DateTimeFormat('tr-TR',{hour:'2-digit',minute:'2-digit'}).format(new Date());
  }catch(e){console.warn('quake',e)}
  try{news=await fetch('data/news.json'+bust).then(r=>r.json());renderNews()}catch(e){console.warn('news',e)}
}
loadData();setInterval(loadData,C.dataRefreshMinutes*60000);
