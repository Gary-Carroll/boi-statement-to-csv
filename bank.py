import pdfplumber
import fitz
import numpy as np
import tabula
import pandas as pd

pdf_path = "your_boi_statement.pdf"
doc = fitz.open(pdf_path)

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages): # set top of table to be slightly above first instance of 'BALANCE'
        y0 = next((int(word['top'] - 3) for word in page.extract_words() if word['text'] == 'BALANCE'), None)
        
        if y0 is None:
            break

        columns_x = [75, 140, 320, 410, 505, 590]  # left edges of columns and right edge of last column

        row_ys = list(np.arange(y0, 648, 12.1))   # y-coordinates of horizontal lines
        row_ys.append(647) # add bottom line for table

        page_fit = doc[i]

        for x in columns_x:
            page_fit.draw_line((x, y0), (x, 648), width=0.5)

        for y in row_ys:
            page_fit.draw_line((columns_x[0], y), (columns_x[-1], y), width=0.5)

doc.save('output.pdf')
doc.close()

dfs = tabula.read_pdf('output.pdf', pages='all', multiple_tables=True, lattice=True)
dfs = [df for df in dfs if len(df) > 0 and df.columns[1] == 'BALANCE FORWARD']

for df in dfs:
    df.columns = ["Date", "Details", "Payments - Out", "Payments - In", "Balance"]
    
df = pd.concat(dfs)
df['Date'] = df['Date'].ffill()
df['Date'] = pd.to_datetime(df['Date'], format='%d %b %Y', errors='coerce')
df = df.dropna(subset=['Date', 'Details'])

for col in ['Payments - Out', 'Payments - In', 'Balance']:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '', regex=False), errors='coerce')


df.to_csv('statement.csv', index=False)
