from docx import Document
from docx.oxml.ns import qn
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = Document(r'c:\Users\POWER\Desktop\NILM\nurai2026template.docx')

sectPr = doc.sections[0]._sectPr
cols = sectPr.xpath('w:cols')
if cols:
    import xml.etree.ElementTree as ET
    # print XML of w:cols
    print(ET.tostring(cols[0], encoding='utf-8').decode('utf-8'))
else:
    print("No w:cols element found")
