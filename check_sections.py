from docx import Document
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = Document(r'c:\Users\POWER\Desktop\NILM\nurai2026template.docx')

for s, section in enumerate(doc.sections):
    print(f"\n--- Section {s} ---")
    print(f"Orientation: {section.orientation}")
    print(f"Page width: {section.page_width.inches:.2f} in, Page height: {section.page_height.inches:.2f} in")
    print(f"Top margin: {section.top_margin.inches:.2f} in, Bottom margin: {section.bottom_margin.inches:.2f} in")
    print(f"Left margin: {section.left_margin.inches:.2f} in, Right margin: {section.right_margin.inches:.2f} in")
    # Check for columns
    from docx.oxml.ns import qn
    sectPr = section._sectPr
    cols = sectPr.xpath('w:cols')
    if cols:
        col_count = cols[0].get(qn('w:num'))
        print(f"Columns: {col_count}")
    else:
        print("Columns: 1 (Default)")
