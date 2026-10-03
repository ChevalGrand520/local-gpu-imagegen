"""Fill the retained SoftwareX v6 template without rebuilding other parts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
import re
from lxml import etree as E

ROOT = Path(__file__).resolve().parent
REF = ROOT / 'templates/softwarex-osp-template-v6.docx'
OUT = ROOT / 'manuscript-v0.2.docx'
QA = Path('/tmp/softwarex-template-qa')
EXPECTED = '9fcf40ede96a2f188ee4ef77134e0596d01e1b65fd9db63f2874d29f2ecb916d'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}

def tag(name):
    return '{' + W + '}' + name

def text_of(element):
    return ''.join(element.xpath('.//w:t/text()', namespaces=NS))

assert sha256(REF.read_bytes()).hexdigest() == EXPECTED
assert (ROOT / 'templates/artifact.md').exists()
with ZipFile(REF) as zin:
    parts = {name: zin.read(name) for name in zin.namelist()}
    infos = zin.infolist()
inventory = {k: {'bytes': len(v), 'sha256': sha256(v).hexdigest()} for k, v in parts.items()}
QA.mkdir(exist_ok=True)
(QA / 'template-part-inventory.json').write_text(json.dumps(inventory, indent=2))
doc = E.fromstring(parts['word/document.xml'])
body = doc.find('w:body', NS)
source = list(body)
original_sect = E.tostring(source[-1])

def para(index, text, bold=None, numbered=True):
    p = deepcopy(source[index])
    pp = p.find('w:pPr', NS)
    rp = p.find('w:r/w:rPr', NS)
    rp = deepcopy(rp) if rp is not None else E.Element(tag('rPr'))
    for x in list(rp):
        if E.QName(x).localname in ('i', 'iCs', 'b', 'bCs', 'highlight', 'u', 'color'):
            rp.remove(x)
    if bold is not None:
        x = E.SubElement(rp, tag('b')); x.set(tag('val'), '1' if bold else '0')
    for x in list(p):
        if x is not pp:
            p.remove(x)
    if pp is not None:
        for x in list(pp):
            if E.QName(x).localname == 'rPr' or (not numbered and E.QName(x).localname in ('numPr', 'ind')):
                pp.remove(x)
    r = E.SubElement(p, tag('r')); r.append(rp)
    t = E.SubElement(r, tag('t')); t.text = text.replace('`', '')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p

def cell_text(cell, text):
    prototype = cell.find('w:p', NS)
    if prototype is None:
        prototype = para(23, '', bold=False)
    else:
        prototype = deepcopy(prototype)
    # Body pattern preserves the table paragraph properties and Arial sizing.
    p = para(23, text, bold=False, numbered=False)
    pp = prototype.find('w:pPr', NS)
    old = p.find('w:pPr', NS)
    if old is not None: p.remove(old)
    if pp is not None:
        pp = deepcopy(pp)
        for x in list(pp):
            if E.QName(x).localname in ('numPr', 'rPr'): pp.remove(x)
        p.insert(0, pp)
    for x in list(cell):
        if E.QName(x).localname != 'tcPr': cell.remove(x)
    cell.append(p)

metadata = deepcopy(source[33])
meta_values = [
    '0.9.1; source snapshot 088ea6192a0b6486ad2f416a9442689aaf982065',
    'https://github.com/ChevalGrand520/local-gpu-imagegen/tree/088ea6192a0b6486ad2f416a9442689aaf982065',
    'MIT License', 'Git', 'Python; stdio Model Context Protocol; ComfyUI and WebUI adapters',
    'Python >=3.11; Windows product platform; py7zr==1.1.3. Backend and model installation is separate. CI: Python 3.11/3.12 on Windows and Ubuntu.',
    'https://github.com/ChevalGrand520/local-gpu-imagegen/blob/088ea6192a0b6486ad2f416a9442689aaf982065/README.md',
    'ChengZhen0105@outlook.com',
]
for row, value in zip(metadata.findall('w:tr', NS)[1:], meta_values):
    cells = row.findall('w:tc', NS)
    originals = [E.tostring(x) for x in cells[:2]]
    cell_text(cells[2], value)
    assert originals == [E.tostring(x) for x in cells[:2]]

def row_rules(table):
    for i, row in enumerate(table.findall('w:tr', NS)):
        pr = row.find('w:trPr', NS)
        if pr is None: pr = E.Element(tag('trPr')); row.insert(0, pr)
        for x in list(pr):
            if E.QName(x).localname == 'trHeight': pr.remove(x)
        if pr.find('w:cantSplit', NS) is None: E.SubElement(pr, tag('cantSplit'))
        if i == 0 and pr.find('w:tblHeader', NS) is None: E.SubElement(pr, tag('tblHeader'))

row_rules(metadata)
blocks = re.split(r'\n\s*\n', (ROOT / 'manuscript-v0.2.md').read_text().strip())
for x in list(body): body.remove(x)
body.append(para(16, blocks[0][2:], bold=True, numbered=False))
for block in blocks[1:4]: body.append(para(23, block, bold=False, numbered=False))
body.append(para(21, 'Abstract', bold=True))
body.append(para(23, blocks[5], bold=False))
assert 90 <= len(blocks[5].split()) <= 110
body.append(para(25, 'Keywords', bold=True))
body.append(para(23, blocks[6].split(': ', 1)[1], bold=False))
body.append(para(29, 'Metadata', bold=True))
body.append(metadata)

heading_map = {1: 35, 2: 44, 3: 53, 4: 56, 5: 68}
started = False
subheading_index = 0
for block in blocks[7:]:
    if block.startswith('## 1.'): started = True
    if not started: continue
    if block.startswith('## '):
        title = block[3:]
        m = re.match(r'([1-5])\. (.*)', title)
        if m:
            subheading_index = 0
            body.append(para(heading_map[int(m[1])], m[2], bold=True))
        else:
            body.append(para(76, title, bold=True, numbered=False))
    elif block.startswith('### '):
        # The mandatory 2.1 and 2.2 slots use source subheading numbering.
        title = re.sub(r'^\d+\.\d+\. ', '', block[4:])
        subheading_index += 1
        if title in ('Architecture', 'Software functionalities', 'Inspection and interfaces'):
            body.append(para(46, 'Software architecture' if title == 'Architecture' else title, bold=True))
        else:
            body.append(para(76, title, bold=True, numbered=False))
    elif block.startswith('|'):
        lines = block.splitlines()
        data = [[c.strip() for c in line.strip('|').split('|')] for line in lines if not re.match(r'^\|[- :|]+\|$', line)]
        table = deepcopy(source[33])
        for row in table.findall('w:tr', NS): table.remove(row)
        grid = table.find('w:tblGrid', NS)
        for x in list(grid): grid.remove(x)
        widths = [2000, 1100, 1300, 1350, 1550, 2178]
        for width in widths:
            x = E.SubElement(grid, tag('gridCol')); x.set(tag('w'), str(width))
        for values in data:
            row = E.Element(tag('tr'))
            for width, value in zip(widths, values):
                cell = deepcopy(source[33].findall('w:tr', NS)[1].findall('w:tc', NS)[2])
                cw = cell.find('w:tcPr/w:tcW', NS)
                if cw is not None: cw.set(tag('w'), str(width))
                cell_text(cell, value); row.append(cell)
            table.append(row)
        row_rules(table); body.append(para(23, 'Table 1. Fixed paired Windows operations', bold=True)); body.append(table)
    else:
        body.append(para(23, block, bold=False))
body.append(deepcopy(source[-1]))
assert E.tostring(body[-1]) == original_sect
parts['word/document.xml'] = E.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
settings = E.fromstring(parts['word/settings.xml'])
upd = settings.find('w:updateFields', NS)
if upd is None: upd = E.SubElement(settings, tag('updateFields'))
upd.set(tag('val'), 'true')
parts['word/settings.xml'] = E.tostring(settings, xml_declaration=True, encoding='UTF-8', standalone=True)
core = E.fromstring(parts['docProps/core.xml'])
for local, value in [('creator', 'Zhen Cheng'), ('lastModifiedBy', 'Zhen Cheng'), ('title', blocks[0][2:])]:
    for e in core.iter():
        if E.QName(e).localname == local: e.text = value
parts['docProps/core.xml'] = E.tostring(core, xml_declaration=True, encoding='UTF-8', standalone=True)
editable = {'word/document.xml', 'word/settings.xml', 'docProps/core.xml'}
assert all(sha256(v).hexdigest() == inventory[k]['sha256'] for k, v in parts.items() if k not in editable)
with ZipFile(OUT, 'w', ZIP_DEFLATED) as zout:
    for info in infos: zout.writestr(info, parts[info.filename])
assert sha256(REF.read_bytes()).hexdigest() == EXPECTED
print('Created', OUT)
print('Preserve-only parts identical:', len(parts) - len(editable))
print('Abstract words:', len(blocks[5].split()))
