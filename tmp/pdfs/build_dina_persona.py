from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/dina-user-persona.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
FONT = Path('/System/Library/Fonts/Supplemental')
for name, file in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
W,H=595.28,841.89
INK='#17322F'; MUTED='#52635D'; GREEN='#18735C'; BG='#F7F7F0'; LINE='#D7DFD5'
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('Dina | Dividend hunter yang merencanakan rotasi modal')
c.setAuthor('Product Research | Sectors Hackathon Track 03')
def rect(x,top,w,h,color):
    c.setFillColor(HexColor(color));c.rect(x,H-top-h,w,h,fill=1,stroke=0)
def p(text,x,top,w,size=10.5,leading=15,color=INK,font='Body'):
    style=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color),alignment=TA_LEFT)
    para=Paragraph(text,style);_,h=para.wrap(w,H)
    assert top+h < 790, f'Overflow: {text[:60]} at {top+h}'
    para.drawOn(c,x,H-top-h)
    return top+h
def start(n,kicker,title,subtitle):
    rect(0,0,W,H,BG);rect(36,30,30,4,GREEN)
    p(kicker.upper(),36,45,520,9,12,GREEN,'Bold')
    y=p(title,36,68,520,27,31,INK,'Bold')
    p(subtitle,36,y+9,520,10,14,MUTED)
    c.setStrokeColor(HexColor(LINE));c.line(36,45,W-36,45)
    c.setFont('Body',8);c.setFillColor(HexColor(MUTED))
    c.drawString(36,29,'DRAFT 01  /  6 OKTOBER 2026  /  MARKET INTELLIGENCE')
    c.drawRightString(W-36,29,f'{n} / 3')
def label(text,x,y,w=250):
    return p(text.upper(),x,y,w,9,12,GREEN,'Bold')+7
def bullets(items,x,y,w):
    for s in items:
        y=p('• '+s,x,y,w,10.2,14.5)+7
    return y

start(1,'Proto-persona / pengguna utama','Dina','Dividend hunter yang merencanakan rotasi modal')
rect(36,133,523,82,INK)
p('Rajin mencari peluang berikutnya, tetapi belum tahu<br/>kapan bisa meninggalkan peluang sebelumnya.',51,146,492,15,20,'#FFFFFF','Bold')
p('29 tahun  |  Staf operasional  |  Pasar saham Indonesia',36,232,523,10,14,MUTED)
y=p('Nama, usia, pekerjaan, dan quote adalah ilustrasi. Pola perilaku dan kebutuhan masih hipotesis; belum hasil wawancara lintas pengguna.',36,253,523,9,13,MUTED)
y=p('“Aku mau ambil dividen lagi di saham lain. Tapi kalau yang ini belum balik modal, uangnya dari mana?”',36,y+15,523,14,19,INK,'Italic')
y=p('Dina menyisihkan penghasilan untuk investasi dan tidak bergantung pada dividen untuk kebutuhan hidup. Ia memahami dasar saham dan dividen. Dengan modal terbatas, ia ingin membandingkan konsentrasi, pembagian dana, dan perpindahan antar emiten.',36,y+13,523,10.5,15)
top=y+23
x1,x2,cw=36,309,250
a=label('Goals / hasil yang dituju',x1,top)
a=bullets(['Mengejar hasil bersih yang menarik dari modalnya.','Memilih pembagian dana dan aturan keluar.','Mengetahui dana yang tersedia untuk peluang berikutnya.'],x1,a,cw)
b=label('Motivations / alasan personal',x2,top)
b=bullets(['Ingin hasil menabungnya terasa berkembang.','Ingin keputusan memiliki alasan yang bisa ia jelaskan.','Ingin tetap mengendalikan rencana saat hasil berbeda dari harapan.'],x2,b,cw)
top=max(a,b)+12
a=label('Frustrations / yang dirasakan',x1,top)
a=bullets(['Frustrasi melihat peluang baru saat dana masih di saham lama.','Ragu apakah menunggu itu rasional atau enggan menerima rugi.','Senang menerima dividen, tetapi cemas melihat nilai saham turun.'],x1,a,cw)
b=label('Pain points / momen kesulitan',x2,top)
b=bullets(['Jadwal berdekatan: belum menghitung benturan penggunaan modal.','Membandingkan yield tanpa harga jual, biaya, dan waktu kepemilikan.','Mengubah alokasi atau aturan jual berarti menghitung ulang rencana.'],x2,b,cw)
p('Definisi BEP Dina: harga jual sama dengan harga beli. Biaya tetap dihitung; ini berbeda dari impas total investasi.',36,max(a,b)+12,523,9,13,MUTED)
c.showPage()

start(2,'Skenario penggunaan / hipotesis','Satu modal, beberapa peluang','Cerita ini menggambarkan pengalaman produk yang dituju, bukan fitur atau hasil yang sudah diverifikasi.')
y=137
scenes=[
('01  Menemukan peluang','Sepulang kerja, Dina menemukan tiga kandidat pembagi dividen. Ia membayangkan memakai dana yang sama bergantian, tetapi jadwalnya berdekatan.'),
('02  Menemui dilema','Ia ingin mengambil peluang berikutnya tanpa asal menjual posisi lama. “Kalau harga belum kembali ke harga beli, aku mau menjual dengan rugi atau menunggu?”'),
('03  Menguji rencana','Dina memasukkan modal dan periode, memilih kandidat dari data Sectors, lalu menentukan alokasi serta aturan masuk dan keluar. Ia memeriksa biaya dan menjalankan replay historis.'),
('04  Melihat konsekuensi','Ia membandingkan dividen, perubahan nilai saham, biaya, dan waktu dana tersedia. Lalu ia mencoba aturan menunggu harga beli. Posisi yang belum pulih tetap tercatat sampai akhir periode.'),
('05  Mengambil keputusan','Dina dapat menjelaskan rencana pilihannya, risiko yang bersedia diterima, dan kapan perlu meninjaunya kembali. Ia tetap mengambil keputusan dan mengeksekusi transaksi sendiri.')]
for title,body in scenes:
    y=p(title,36,y,523,11.5,16,GREEN,'Bold')+5
    y=p(body,36,y,523,10.5,15)+14
y=label('User story',36,y,523)
y=p('Sebagai investor individu yang merencanakan rotasi dividen, saya ingin membandingkan aturan alokasi dan keluar, agar dapat memilih rencana berdasarkan hasil bersih, risiko, dan ketersediaan dana untuk peluang berikutnya.',36,y,523,11,16)+19
y=label('Output yang membantu keputusan',36,y,523)
y=p('<b>Hasil:</b> dividen, perubahan nilai saham, biaya, dan hasil bersih.<br/><b>Risiko:</b> penurunan nilai serta posisi yang belum pulih.<br/><b>Waktu:</b> kas tersedia dan dana yang masih berada dalam saham.<br/><b>Perbandingan:</b> konsekuensi perubahan aturan pada periode yang sama.',36,y,523,10.5,16)+16
p('Ukuran keberhasilan pengalaman: Dina bisa menjelaskan konsekuensi pilihannya. Replay historis tidak memastikan hasil masa depan; peluang keuntungan dan kebutuhan produknya tetap harus diuji.',36,y,523,9.5,14,MUTED)
c.showPage()

start(3,'Dasar riset / batas validasi','Apakah labelnya tepat?','Usulan label: dividend hunter yang merencanakan rotasi modal. Ini deskripsi perilaku, bukan klasifikasi investor baku.')
y=137
y=p('<b>Ya, sebutkan dividend hunter secara eksplisit, lalu jelaskan perilakunya.</b> Istilah dividend capture lebih dekat dengan pembelian untuk memperoleh hak dividen dan penjualan setelahnya. Rotasi modal adalah rencana lanjutan persona kita; bukti strategi tidak otomatis memvalidasi seluruh karakter Dina.',36,y,523,10.5,15)+17
sources=[
('1  Istilah lokal memiliki makna beragam','Tulisan Hani Putranto di Stockbit (11 Februari 2023) memakai dividend hunter sekaligus untuk pendekatan menahan saham jangka panjang. Ini menunjukkan pemakaian istilah oleh anggota komunitas, bukan definisi resmi atau survei pasar.', 'https://stockbit.com/post/10750711','Stockbit / tulisan komunitas'),
('2  Strategi dividend capture dikenal','Fidelity membahas pembelian sebelum ex-dividend dan penjualan sesudahnya, beserta dampak harga, biaya, dan pajak. Ini menguatkan keberadaan konsep strategi; konteks pajak dan settlement AS tidak dipindahkan ke Indonesia.', 'https://www.fidelity.com/learning-center/investment-products/stocks/why-dividends-matter','Fidelity / Why Dividends Matter'),
('3  Ada bukti empiris perilaku individu','Park & Park (2010), Korean Journal of Financial Studies 39(4), 491-515: abstrak melaporkan perubahan transaksi sekitar ex-dividend pada kelompok individu dengan transaksi lebih besar setelah perubahan pajak. Tidak ditemukan perubahan serupa pada kelompok terkecil. Bukti Korea ini tidak mengukur pasar Indonesia.', 'https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART001508267','KCI / abstrak dan metadata artikel'),
('4  Ada cerita praktik yang dekat dengan Dina','Penulis unggahan “25 Days of Dividend Capture” menceritakan pembelian bergantian, batas modal, dan pembayaran dividen yang belum menjadi kas. Ini petunjuk untuk wawancara; identitas, transaksi, dan klaim return tidak diaudit dan tidak digunakan sebagai bukti profitabilitas.', 'https://www.reddit.com/r/dividends/comments/1ac8f1n/25_days_of_dividend_capture/','Reddit / laporan pribadi')]
for title,body,url,linklabel in sources:
    y=p(title,36,y,523,10.5,14,GREEN,'Bold')+4
    y=p(body,36,y,523,9.7,13.5)+3
    y=p(f'<link href="{url}" color="{GREEN}"><u>{linklabel}</u></link>',36,y,523,9,12)+13
y=label('Yang masih perlu divalidasi',36,y,523)
y=p('Seberapa umum rotasi ini pada retail Indonesia? Bagaimana mereka menghitung alternatif sekarang? Apa tindakan mereka ketika harga belum pulih? Apakah simulator cukup berguna untuk dipakai berulang atau dibayar? Usia, pekerjaan, emosi, dan kebutuhan Dina belum terverifikasi.',36,y,523,9.7,13.5)+13
p('Metode persona mengikuti Community Challenge Persona Guide yang diberikan pengguna. Sumber internet diakses 6 Oktober 2026. Riset ini memvalidasi istilah dan memberi bukti terbatas tentang perilaku, bukan ukuran pasar, permintaan produk, atau keuntungan strategi.',36,y,523,8.5,12,MUTED)
c.save()
print(OUT)
