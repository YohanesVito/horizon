import json, re, html
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
data=json.loads((ROOT/'tmp/pdfs/video-page-export.json').read_text())
OUT=ROOT/'output/pdf/konsep-dan-script-video-dividen.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
fontdir=Path('/System/Library/Fonts/Supplemental')
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(fontdir/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
INK=colors.HexColor('#17322F'); GREEN=colors.HexColor('#18735C'); GRAY=colors.HexColor('#53645F')
WIDTH=511.28
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=14.7,textColor=INK,spaceAfter=8),
 'note':ParagraphStyle('note',fontName='Body',fontSize=9.2,leading=13.3,textColor=GRAY,spaceAfter=8),
 'h1':ParagraphStyle('h1',fontName='Bold',fontSize=23,leading=27,textColor=INK,spaceAfter=13),
 'h2':ParagraphStyle('h2',fontName='Bold',fontSize=17,leading=21,textColor=GREEN,spaceBefore=10,spaceAfter=11,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='Bold',fontSize=12,leading=16,textColor=GREEN,spaceBefore=10,spaceAfter=8,keepWithNext=True),
 'scene':ParagraphStyle('scene',fontName='Bold',fontSize=12,leading=17,textColor=GREEN,spaceBefore=11,spaceAfter=8,keepWithNext=True),
 'voice':ParagraphStyle('voice',fontName='Body',fontSize=11,leading=16,textColor=INK,spaceAfter=9,leftIndent=10,borderPadding=9,borderColor=colors.HexColor('#C7DCD1'),borderWidth=.7,backColor=colors.HexColor('#F0F5EF')),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=9.3,leading=13,textColor=INK),
 'th':ParagraphStyle('th',fontName='Bold',fontSize=9.3,leading=13,textColor=colors.white),
}
def inline(s):
    s=s.replace('–','-').replace('—','-').replace('\u2011','-')
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#18735C"><u>\1</u></link>',s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return s.replace('\n','<br/>')
def para(s,style='body'):
    return Paragraph(inline(s),styles[style])
def table(md):
    lines=md.splitlines(); rows=[]
    for i,line in enumerate(lines):
        if i==1:continue
        cells=[x.strip() for x in line.strip().strip('|').split('|')]
        rows.append([para(x,'th' if i==0 else 'cell') for x in cells])
    n=len(rows[0]); widths=[130,WIDTH-130] if n==2 else [94,213,WIDTH-307]
    t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F0F4EE'),colors.white]),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#D6DFD6'))]))
    return [t,Spacer(1,12)]

story=[para('Konsep dan script video\nSimulator rotasi dividen','h1'),para('Sectors Hackathon / Track 03 Market Intelligence','h3'),para('Ekspor draft 6 Oktober 2026. Memuat konsep, judging video, teaser, dan catatan produksi. Angka hasil tetap berupa placeholder sampai simulasi diverifikasi.','note'),para('[Page sumber](https://chatgpt.com/space/page_f0a72194ac1881918d2f51e8ce5e99d5)','note')]
blocks=data['content']['blocks']
i=0; scene=[]
def flush():
    global scene
    if scene: story.append(KeepTogether(scene));scene=[]
while i<len(blocks):
    b=blocks[i]['markdown'];i+=1
    if b.startswith('**00.') or b.startswith('**01.') or b.startswith('**02.'):
        flush();scene=[para(b.strip('*'),'scene')];continue
    if b.startswith('#'):
        flush()
        if b in ['## Konsep cerita','### Lima pertanyaan yang harus terjawab','## Naskah judging video','## Naskah teaser satu menit','## Persiapan bukti demo','## Arahan produksi dan iterasi']:
            story.append(PageBreak())
        story.append(para(b.lstrip('# ').strip(),'h3' if b.startswith('###') else 'h2'));continue
    if b.startswith('|'):
        flush();story.extend(table(b));continue
    style='voice' if b.startswith('Narasi:') else 'note' if b.startswith(('Visual:','Catatan','Teks penutup:')) else 'body'
    obj=para(b,style)
    if scene:scene.append(obj)
    else:story.append(obj)
flush()

def footer(c,doc):
    w,h=doc.pagesize
    c.setStrokeColor(colors.HexColor('#D6DFD6'));c.line(42,39,w-42,39)
    c.setFont('Body',8);c.setFillColor(GRAY)
    c.drawString(42,26,'DRAFT / DINA / SIMULATOR ROTASI DIVIDEN')
    c.drawRightString(w-42,26,str(doc.page))
    if doc.page>1:
        c.setFont('Body',8);c.drawString(42,h-29,'KONSEP DAN SCRIPT VIDEO  |  SECTORS HACKATHON')

doc=SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),rightMargin=42,leftMargin=42,topMargin=48,bottomMargin=54,title='Konsep dan script video simulator rotasi dividen',author='Product Research')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(str(OUT))
print('Output:',OUT,'Pages:',len(r.pages))
for i,page in enumerate(r.pages):
    txt=page.extract_text()
    print(i+1,len(txt),txt[:90].replace('\n',' / '))
