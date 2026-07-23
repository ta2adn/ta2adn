from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re, os

from icalendar import Calendar
import recurring_ical_events

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data";DATA.mkdir(exist_ok=True)
TZ=ZoneInfo("Europe/Istanbul")
CALENDAR_ID="c8463dde93b33102037c24945343919c98dedf8bad37573838101bf3d3660c32@group.calendar.google.com"
# Takvim herkese açık değilse Google Calendar > Ayarlar ve paylaşım >
# "Gizli iCal biçimindeki adres" bağlantısını aşağıya yapıştırın.
CALENDAR_ICS_URL=os.environ.get("CALENDAR_ICS_URL","").strip()

def get(url, data=None, headers=None):
    default_headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149 Safari/537.36",
        "Accept":"application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language":"tr-TR,tr;q=0.9,en;q=0.7"
    }
    if headers:
        default_headers.update(headers)
    req=urllib.request.Request(url,data=data,headers=default_headers)
    with urllib.request.urlopen(req,timeout=40) as r:
        return r.read()

def write(name,obj):
    (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")

def ago_text(dt):
    sec=max(0,int((datetime.now(TZ)-dt).total_seconds()))
    if sec<3600:return f"{max(1,sec//60)} dakika önce"
    if sec<86400:return f"{sec//3600} saat önce"
    return f"{sec//86400} gün önce"

def weather_code_name(c):
    names={0:"Açık",1:"Az bulutlu",2:"Parçalı bulutlu",3:"Kapalı",45:"Sisli",48:"Sisli",
           51:"Çiseleme",53:"Çiseleme",55:"Yoğun çiseleme",61:"Yağmurlu",63:"Yağmurlu",65:"Kuvvetli yağmur",
           71:"Karlı",73:"Karlı",75:"Yoğun kar",80:"Sağanak",81:"Sağanak",82:"Kuvvetli sağanak",
           95:"Fırtına",96:"Dolu ve fırtına",99:"Şiddetli fırtına"}
    return names.get(int(c),"Değişken")

def moon_info(dt):
    syn=29.53058867
    known=datetime(2000,1,6,18,14,tzinfo=timezone.utc)
    p=((dt.astimezone(timezone.utc)-known).total_seconds()/86400%syn)/syn
    illumination=round((1-__import__("math").cos(2*__import__("math").pi*p))/2*100)
    if p<.03 or p>.97:phase,icon="Yeni Ay","🌑"
    elif p<.22:phase,icon="Büyüyen Hilal","🌒"
    elif p<.28:phase,icon="İlk Dördün","🌓"
    elif p<.47:phase,icon="Büyüyen Ay","🌔"
    elif p<.53:phase,icon="Dolunay","🌕"
    elif p<.72:phase,icon="Küçülen Ay","🌖"
    elif p<.78:phase,icon="Son Dördün","🌗"
    else:phase,icon="Küçülen Hilal","🌘"
    return {"phase":phase,"illumination":illumination,"icon":icon,"waxing":p<0.5}

def update_weather():
    url=("https://api.open-meteo.com/v1/forecast?latitude=41.0082&longitude=28.9784"
         "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
         "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset"
         "&timezone=Europe%2FIstanbul&forecast_days=5")
    d=json.loads(get(url))
    cur=d["current"];daily=d["daily"]
    out={
      "current":{"temperature":cur["temperature_2m"],"feels_like":cur["apparent_temperature"],
                  "humidity":cur["relative_humidity_2m"],"wind_speed":cur["wind_speed_10m"],
                  "code":cur["weather_code"],"condition":weather_code_name(cur["weather_code"])},
      "sun":{"sunrise":daily["sunrise"][0][11:16],"sunset":daily["sunset"][0][11:16]},
      "moon":moon_info(datetime.now(TZ)),
      "daily":[]
    }
    days=["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"]
    for i,date_s in enumerate(daily["time"]):
        dt=datetime.fromisoformat(date_s)
        out["daily"].append({"day":days[dt.weekday()],"code":daily["weather_code"][i],
                             "max":daily["temperature_2m_max"][i],"min":daily["temperature_2m_min"][i]})
    write("weather.json",out)

def update_calendar():
    encoded=urllib.parse.quote(CALENDAR_ID,safe="")
    if not CALENDAR_ICS_URL:
        raise RuntimeError("CALENDAR_ICS_URL tanımlı değil")
    url=CALENDAR_ICS_URL
    cal=Calendar.from_ical(get(url))
    now=datetime.now(TZ);monday=(now-timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
    end=monday+timedelta(days=7)
    events=[]
    for ev in recurring_ical_events.of(cal).between(monday,end):
        start=ev.decoded("DTSTART");endv=ev.decoded("DTEND") if ev.get("DTEND") else start
        all_day=not isinstance(start,datetime)
        if all_day:
            sdt=datetime.combine(start,datetime.min.time(),TZ)
            time_txt="Tüm gün"
        else:
            sdt=start if start.tzinfo else start.replace(tzinfo=TZ)
            sdt=sdt.astimezone(TZ);time_txt=sdt.strftime("%H:%M")
        if all_day:
            edt=datetime.combine(endv,datetime.min.time(),TZ) if not isinstance(endv,datetime) else endv.astimezone(TZ)
        else:
            edt=endv if isinstance(endv,datetime) else sdt
            if isinstance(edt,datetime) and edt.tzinfo is None:edt=edt.replace(tzinfo=TZ)
            if isinstance(edt,datetime):edt=edt.astimezone(TZ)
        title=str(ev.get("SUMMARY","Etkinlik")).strip() or "Etkinlik"
        events.append({"title":title,"start":sdt.isoformat(),"end":edt.isoformat(),
                       "time":time_txt,"all_day":all_day})
    events.sort(key=lambda x:x["start"])
    write("calendar.json",events)

def update_quakes():
    url="https://api.orhanaydogdu.com.tr/deprem/kandilli/live?skip=0&limit=200"
    j=json.loads(get(url));arr=j if isinstance(j,list) else (j.get("result") or j.get("data") or [])
    out=[]
    for item in arr:
        mag=item.get("mag",item.get("magnitude",0))
        try:mag=float(mag)
        except:continue
        if mag<3.5:continue
        ds=item.get("date") or item.get("date_time") or item.get("tarih") or item.get("created_at")
        try:
            dt=datetime.fromisoformat(str(ds).replace("Z","+00:00"))
            if dt.tzinfo is None:dt=dt.replace(tzinfo=TZ)
            dt=dt.astimezone(TZ)
        except:dt=datetime.now(TZ)
        loc=item.get("title") or item.get("location") or item.get("place") or "Türkiye"
        depth=item.get("depth",0)
        try:depth=float(depth)
        except:depth=0
        out.append({"time":dt.strftime("%H:%M:%S"),"magnitude":mag,"location":loc,"depth":depth,"ago":ago_text(dt)})
    out.sort(key=lambda x:x["time"],reverse=True)
    write("earthquakes.json",out[:20])

def update_news():
    feeds=[
      ("Google News","https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"),
      ("Google News Türkiye","https://news.google.com/rss/search?q=Türkiye&hl=tr&gl=TR&ceid=TR:tr"),
      ("TRT Haber","https://www.trthaber.com/sondakika_articles.rss"),
      ("TRT Haber","https://www.trthaber.com/manset_articles.rss")
    ]

    out=[]
    errors=[]

    for source,url in feeds:
        try:
            root=ET.fromstring(get(url))
            items=root.findall(".//item")

            if not items:
                ns={"atom":"http://www.w3.org/2005/Atom"}
                items=root.findall(".//atom:entry",ns)

            for item in items[:20]:
                title=(item.findtext("title") or "").strip()
                if not title:
                    title=(item.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()

                if source.startswith("Google News"):
                    title=re.sub(r"\s+-\s+[^-]+$","",title).strip()

                raw_desc=(item.findtext("description") or
                          item.findtext("summary") or
                          item.findtext("{http://www.w3.org/2005/Atom}summary") or "")
                raw_desc=re.sub(r"<script.*?</script>"," ",raw_desc,flags=re.I|re.S)
                raw_desc=re.sub(r"<style.*?</style>"," ",raw_desc,flags=re.I|re.S)
                raw_desc=re.sub(r"<[^>]+>"," ",raw_desc)
                raw_desc=(raw_desc.replace("&nbsp;"," ")
                                  .replace("&amp;","&")
                                  .replace("&quot;",'"')
                                  .replace("&#39;","'"))
                raw_desc=re.sub(r"\s+"," ",raw_desc).strip()

                desc=raw_desc
                if title and desc.lower().startswith(title.lower()):
                    desc=desc[len(title):].lstrip(" -–—:|")

                desc=re.sub(r"\s+-\s+[^-]+$","",desc).strip()

                if len(desc)>240:
                    desc=desc[:237].rsplit(" ",1)[0]+"…"

                if not desc or desc==title:
                    desc=f"{source} üzerinden güncel haber."

                pub=(item.findtext("pubDate") or
                     item.findtext("published") or
                     item.findtext("updated") or
                     item.findtext("{http://www.w3.org/2005/Atom}published") or
                     item.findtext("{http://www.w3.org/2005/Atom}updated") or "")
                tm="SON"
                try:
                    from email.utils import parsedate_to_datetime
                    dt=parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt=dt.replace(tzinfo=timezone.utc)
                    tm=dt.astimezone(TZ).strftime("%H:%M")
                except:
                    try:
                        dt=datetime.fromisoformat(pub.replace("Z","+00:00"))
                        if dt.tzinfo is None:
                            dt=dt.replace(tzinfo=timezone.utc)
                        tm=dt.astimezone(TZ).strftime("%H:%M")
                    except:
                        pass

                normalized=re.sub(r"\W+"," ",title.lower()).strip()
                already=any(re.sub(r"\W+"," ",x["title"].lower()).strip()==normalized for x in out)

                if title and not already:
                    out.append({
                        "time":tm,
                        "title":title,
                        "description":desc,
                        "source":source
                    })

            if source.startswith("Google News") and len(out)>=12:
                break

        except Exception as e:
            errors.append(f"{source}: {e}")
            print("RSS",source,e)

    if not out:
        raise RuntimeError("Hiçbir RSS kaynağından haber alınamadı: "+" | ".join(errors))

    write("news.json",out[:18])

failures=[]
for fn in (update_weather,update_calendar,update_quakes,update_news):
    try:
        fn()
    except Exception as e:
        failures.append(f"{fn.__name__}: {e}")
        print(fn.__name__,e)

if failures:
    raise SystemExit("\n".join(failures))
