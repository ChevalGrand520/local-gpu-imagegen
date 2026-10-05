"""Export the retained, simple SVG diagrams as vector PDF with embedded fonts."""
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor

ROOT = Path(__file__).resolve().parent
FONT_ROOT = Path('/System/Library/Fonts/Supplemental')
for name, filename in [('FigureArial', 'Arial.ttf'), ('FigureArialBold', 'Arial Bold.ttf')]:
    font = FONT_ROOT / filename
    if not font.exists():
        raise FileNotFoundError(font)
    pdfmetrics.registerFont(TTFont(name, str(font)))

def points(value):
    numbers = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', value)]
    assert len(numbers) % 2 == 0
    return list(zip(numbers[::2], numbers[1::2]))

def export(name):
    source = ROOT / (name + '.svg')
    root = ET.fromstring(source.read_text())
    width, height = float(root.attrib['width']), float(root.attrib['height'])
    output = ROOT / (name + '.pdf')
    pdf = canvas.Canvas(str(output), pagesize=(width, height), invariant=1)
    pdf.setTitle(name)
    texts = []
    for element in root:
        kind = element.tag.split('}')[-1]
        a = element.attrib
        if kind == 'defs':
            continue
        pdf.saveState()
        stroke = a.get('stroke', 'none') != 'none'
        fill = a.get('fill', 'black') != 'none'
        if stroke:
            pdf.setStrokeColor(toColor(a['stroke']))
        if fill:
            pdf.setFillColor(toColor(a.get('fill', 'black')))
        pdf.setLineWidth(float(a.get('stroke-width', 1)))
        if a.get('stroke-dasharray'):
            pdf.setDash([float(x) for x in re.split(r'[, ]+', a['stroke-dasharray'])])
        if kind == 'rect':
            x, y = float(a.get('x', 0)), float(a.get('y', 0))
            w, h = float(a['width']), float(a['height'])
            if a.get('rx'):
                pdf.roundRect(x, height-y-h, w, h, float(a['rx']), stroke=stroke, fill=fill)
            else:
                pdf.rect(x, height-y-h, w, h, stroke=stroke, fill=fill)
        elif kind == 'text':
            text = ''.join(element.itertext())
            texts.append(text)
            pdf.setFont('FigureArialBold' if a.get('font-weight') == 'bold' else 'FigureArial', float(a['font-size']))
            draw = pdf.drawCentredString if a.get('text-anchor') == 'middle' else pdf.drawString
            draw(float(a['x']), height-float(a['y']), text)
        elif kind in ('path', 'polyline', 'polygon'):
            if kind == 'path':
                assert re.sub(r'[ML\s,0-9.\-]', '', a['d']) == '', 'Unsupported SVG path command'
                ps = points(a['d'])
            else:
                ps = points(a['points'])
            p = pdf.beginPath()
            p.moveTo(ps[0][0], height-ps[0][1])
            for x, y in ps[1:]:
                p.lineTo(x, height-y)
            if kind == 'polygon':
                p.close()
            pdf.drawPath(p, stroke=stroke, fill=fill)
            if a.get('marker-end'):
                assert a['marker-end'] == 'url(#arrow-default)'
                x, y = ps[-1]
                px, py = ps[-2]
                angle = math.atan2(y-py, x-px)
                scale = float(a.get('stroke-width', 1))
                arrow = pdf.beginPath()
                arrow.moveTo(x, height-y)
                for local_x, local_y in [(-8*scale, -4*scale), (-8*scale, 4*scale)]:
                    ax = x + local_x*math.cos(angle) - local_y*math.sin(angle)
                    ay = y + local_x*math.sin(angle) + local_y*math.cos(angle)
                    arrow.lineTo(ax, height-ay)
                arrow.close()
                pdf.setFillColor(toColor('#555555'))
                pdf.drawPath(arrow, stroke=0, fill=1)
        else:
            raise ValueError('Unsupported SVG element: '+kind)
        pdf.restoreState()
    pdf.showPage()
    pdf.save()
    from pypdf import PdfReader
    result = PdfReader(output)
    assert len(result.pages) == 1
    extracted = result.pages[0].extract_text()
    assert all(text in extracted for text in texts)
    assert not result.pages[0].get('/Resources', {}).get('/XObject'), 'Unexpected raster content'
    fonts = result.pages[0]['/Resources']['/Font']
    embedded = 0
    for font_ref in fonts.values():
        descriptor = font_ref.get_object().get('/FontDescriptor')
        if descriptor and descriptor.get_object().get('/FontFile2'):
            embedded += 1
    assert embedded >= 1
    print(output.name, 'labels:', len(texts), 'embedded fonts:', embedded)

if __name__ == '__main__':
    for name in ['architecture', 'known-job-recovery']:
        export(name)
