# boi-statement-to-csv
This script processes BOI account statements in PDF format, as downloaded from the BOI app.
It detects the start of the transaction table on each page, adds lines using pdf_plumber and fitz, and extracts the table data using tabula.
The data is then cleaned to include only actual transaction details.
