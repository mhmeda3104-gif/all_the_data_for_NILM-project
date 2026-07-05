import win32com.client
import os

try:
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc_path = r"C:\Users\POWER\Desktop\NILM\NILM_Final_Paper.docx"
    
    if os.path.exists(doc_path):
        doc = word.Documents.Open(doc_path)
        # Force a pagination update
        doc.Repaginate()
        page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
        print(f"Page count of NILM_Final_Paper.docx is: {page_count}")
        doc.Close(False)
    else:
        print("File not found.")
    word.Quit()
except Exception as e:
    print(f"Error checking page count: {e}")
