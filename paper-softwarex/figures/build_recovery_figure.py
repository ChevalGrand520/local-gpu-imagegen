"""Render the manuscript's CPU engine-fixture state diagram as SVG and PNG."""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
image = Image.new('RGB', (1400, 320), 'white')
draw = ImageDraw.Draw(image)
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font = ImageFont.truetype(font_path, 25)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="320" viewBox="0 0 1400 320" font-family="Arial, sans-serif">', '<rect width="1400" height="320" fill="white"/>']

def box(x, y, w, h):
    draw.rectangle((x, y, x+w, y+h), outline='#555555', width=2)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#555555" stroke-width="2"/>')

def label(x, y, value):
    draw.text((x, y), value, font=font, fill='#222222', anchor='mt')
    svg.append(f'<text x="{x}" y="{y+24}" text-anchor="middle" font-size="25" fill="#222222">{escape(value)}</text>')

def arrow(points):
    draw.line(points, fill='#555555', width=2)
    x, y = points[-1]
    draw.polygon([(x,y),(x-12,y-6),(x-12,y+6)], fill='#555555')
    coords = ' '.join(f'{x},{y}' for x,y in points)
    svg.append(f'<polyline points="{coords}" fill="none" stroke="#555555" stroke-width="2"/>')
    svg.append(f'<polygon points="{x},{y} {x-12},{y-6} {x-12},{y+6}" fill="#555555"/>')

box(20, 65, 280, 95)
label(160, 82, 'unresolved')
label(160, 117, 'retained job ID')
box(415, 65, 330, 95)
label(580, 82, 'get_run')
label(580, 117, 'generate_round:recover')
box(1080, 65, 300, 95)
label(1230, 82, 'generated')
label(1230, 117, 'image path recorded')
arrow([(300,110),(415,110)])
label(355, 31, 'inspect')
arrow([(745,110),(1080,110)])
label(910, 31, 'same key / request hash')
label(910, 165, 'forward recovery_job_id')
box(1080, 225, 300, 75)
label(1230, 247, 'unresolved')
arrow([(160,160),(160,260),(1080,260)])
label(590, 225, 'stop-only: no further action')
svg.append('</svg>')
(ROOT / 'known-job-recovery.svg').write_text('\n'.join(svg) + '\n')
image.save(ROOT / 'known-job-recovery.png')
