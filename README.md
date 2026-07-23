# TA2ADN Dashboard v2

## Yerel çalıştırma

```cmd
pip install -r requirements.txt
python scripts\update_data.py
python -m http.server 8000
```

Tarayıcı:
`http://localhost:8000`

## Google Takvim

Takvimin Google Calendar ayarlarında **Herkese açık** olması gerekir.
Script, takvimin iCal kaynağından bu haftanın tüm etkinliklerini alır.
Google iframe kullanılmaz.

## GitHub Pages

1. Tüm dosyaları deponun köküne yükleyin.
2. Settings > Pages > Deploy from a branch > main / root.
3. Actions sekmesinden `Dashboard verilerini güncelle` iş akışını bir kez çalıştırın.

## Takvimde `Busy` görünüyorsa

Google yalnızca boş/dolu bilgisini yayımlıyordur. Google Calendar içinden
**Ayarlar ve paylaşım > Takvimi entegre et > Gizli iCal biçimindeki adres**
bağlantısını kopyalayıp `scripts/update_data.py` içindeki `CALENDAR_ICS_URL`
alanına yapıştırın. Bu bağlantıyı herkese açık bir GitHub deposuna koymayın.

## Özel Google Takvim bağlantısı

Takvim adresi proje dosyalarına yazılmaz.

### Yerel kullanım

`verileri-guncelle.bat` dosyasını çalıştırın ve gizli iCal adresini yapıştırın.

### GitHub

Repository > Settings > Secrets and variables > Actions > New repository secret:

- Name: `CALENDAR_ICS_URL`
- Value: Google Calendar gizli iCal bağlantısı

Ardından Actions bölümünden veri güncelleme iş akışını çalıştırın.

## MGM radar kırpma

Radar panelinin ölçüsü değişmez. Görüntü yatayda `%122` genişletilir ve sağdaki
saat/renk lejantı panelin dışında bırakılır. Oranı değiştirmek için
`style.css` içindeki `.radar img` bölümündeki `width:122%` değerini değiştirin.

## v5 ekran yerleşimi

Dashboard artık ekranın dikey ortasına değil üst kenarına hizalanır.
Önceki sürümde kullanılmayan 32 piksel, radar ve haftalık takvim satırına
eklenmiştir. 1920×1080 ve 1280×720 gibi 16:9 ekranlarda üstte boşluk kalmaz.

## v6 yerleşimi

- Haftalık takvim sağ tarafta radar ve orta satır boyunca uzatıldı.
- En altta Google News solda, son depremler sağda yer alır.
- Haber alanında başlık ve kısa açıklama birlikte gösterilir.
- Güneş ve ay bölümlerine görsel ikonlar eklendi.
- Ay ikonu mevcut evreye göre otomatik değişir.

## v7 değişiklikleri

- Ay evresi artık emoji yerine beyaz, sade bir görsel olarak çizilir.
- Ay evresi, aydınlanma oranı ve büyüyen/küçülen durumu her veri güncellemesinde otomatik hesaplanır.
- Haber kaynağı TRT Haber resmî RSS akışlarına çevrildi.
- Hava tahmini Open-Meteo üzerinden İstanbul koordinatları için alınır.
- Radar alanı MGM'nin resmî hareketli İstanbul radar sayfasını kullanır ve yalnızca radar bölümü görünecek şekilde kırpılır.

## v8 MGM hareketli radar

MGM'nin kendi sayfası iframe olarak kullanılmaz. Bunun yerine:
`istppi1.jpg` ile `istppi15.jpg` arasındaki 15 resim önceden yüklenir ve
700 ms aralıkla sırayla gösterilir. Kareler 5 dakikada bir yeniden alınır.

Radar çerçevesinin boyutu değişmez; görüntü `%122` genişletildiği için
sağdaki siyah lejant panel dışında kalır.

## v9 RSS düzeltmesi

Haber güncellemesini engelleyen `desc is not defined` hatası giderildi.
TRT Haber'in resmî Son Dakika, Manşet ve Türkiye RSS akışları kullanılır.
HTML etiketleri açıklamalardan temizlenir; uzun açıklamalar kart için kısaltılır.
RSS tarihleri RFC 2822 biçiminde güvenli şekilde ayrıştırılır.
