"""Vector protocol diagrams, not measured latency plots. Requires reportlab."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,black,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
pdfmetrics.registerFont(TTFont("FigureSans", str(Path(reportlab.__file__).parent/"fonts/Vera.ttf")))
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
BLUE=HexColor('#17618c');GRAY=HexColor('#f0f2f4')
def text(c,x,y,s,size=8,center=False):
 c.setFillColor(black);c.setFont('FigureSans',size)
 (c.drawCentredString if center else c.drawString)(x,y,s)
def arrow(c,x1,y1,x2,y2,dashed=False):
 c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(.8);c.setDash(3,2) if dashed else c.setDash()
 c.line(x1,y1,x2,y2);c.setDash();import math
 a=math.atan2(y2-y1,x2-x1);p=c.beginPath();p.moveTo(x2,y2)
 for off in [2.6,-2.6]:p.lineTo(x2+5*math.cos(a+off),y2+5*math.sin(a+off))
 p.close();c.drawPath(p,fill=1,stroke=0)
def box(c,x,y,w,h,lines):
 c.setFillColor(GRAY);c.setStrokeColor(BLUE);c.roundRect(x,y,w,h,3,fill=1,stroke=1)
 for i,l in enumerate(lines):text(c,x+w/2,y+h/2+(len(lines)-1)*5-i*10,l,8,True)
c=canvas.Canvas(str(OUT/'f02-sequence.pdf'),pagesize=(504,260), initialFontName='FigureSans')
xs=[55,186,318,451];labels=['Research client','Prompt proxy','ComfyUI backend','Observer / controller']
for x,l in zip(xs,labels):
 text(c,x,245,l,8,True);c.setStrokeColor(HexColor('#aaa'));c.setDash(2,2);c.line(x,27,x,233);c.setDash()
for y,a,b,label in [(217,0,1,'Call 1: fresh run; seed 4101'),(193,1,2,'POST accepted'),(148,2,3,'Start + terminal + completed history'),(91,0,1,'Call 2: new run; seed 4102'),(68,1,2,'Second accepted submission'),(44,2,3,'Second execution binding')]:
 arrow(c,xs[a],y,xs[b],y);text(c,(xs[a]+xs[b])/2,y+7,label,7,True)
arrow(c,318,172,186,172);text(c,252,179,'Acceptance response',7,True)
c.setStrokeColor(black);c.line(177,166,187,178);c.line(177,178,187,166);text(c,32,169,'Dropped response',7)
text(c,55,128,'Call 1: unresolved',8,True);arrow(c,451,113,55,113,True);text(c,251,119,'Controller permits next call after first binding',7,True)
text(c,252,9,'Protocol order only; arrow spacing does not represent measured time.',7,True);c.save()
c=canvas.Canvas(str(OUT/'recovery-scope.pdf'),pagesize=(252,225), initialFontName='FigureSans')
box(c,54,185,144,29,['Generation through run R'])
box(c,54,128,144,36,['Explicit unknown submission','No durable backend job ID'])
arrow(c,126,185,126,164)
box(c,10,62,107,37,['Run R: unresolved','Further submit blocked'])
box(c,139,62,103,37,['Inspect run R','No automatic reconcile'])
arrow(c,102,128,65,99);arrow(c,153,128,190,99)
box(c,38,8,176,32,['A new run R2 has separate state','Outside the same-run guard'])
arrow(c,66,62,92,40,True);text(c,126,49,'Separate caller decision',7,True);c.save()
print('Wrote two vector diagrams; protocol/scope illustrations, not empirical timing claims')
