import re, json
import xml.etree.ElementTree as ET


raw_xml = open('content.xml').read(1000000)

tree = ET.parse('content.xml')
root = tree.getroot()

ns = {
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}

table = root.find('.//table:table', ns)
rows = table.findall('.//table:table-row', ns)

all_vals = []
for row in rows:
    cells = row.findall('./table:table-cell', ns)
    row_vals = []
    for cell in cells:
        link = cell.get('{%s}formula' % ns['table'])
        colrep = cell.get('{%s}number-columns-repeated' % ns['table'])
        val = None
        if link:
            match = re.search('HYPERLINK\("([^"]+)"', link)
            val = match.group(1)
        else:
            txt = cell.findtext('./text:p', None, ns)
            if txt:
                val = txt
        if val:
            val = str(val.replace('\t', ' ').replace('\n', ' '))
            row_vals.append(val)
        if colrep:
            cols = int(colrep)
            if cols < 100:
                for i in range(0, cols - 1):
                    row_vals.append('')
    all_vals.append(row_vals)


all_csv = ''
for row in all_vals:
    all_csv += '\t'.join(row) + '\n'

with open('content.tsv', 'w') as f:
    f.write(all_csv)