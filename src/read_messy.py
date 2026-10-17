import glob
import os

import pdfplumber

PDF_DIR = "data/messy"
OUT_DIR = "data/messy_text"
os.makedirs(OUT_DIR, exist_ok=True)

# Part 1: read ONE invoice and look at the raw text
with pdfplumber.open(f"{PDF_DIR}/invoice_001.pdf") as pdf:
    text = pdf.pages[0].extract_text()
print(text)

# Part 2: read ALL invoices and save each one's text in data/text/
count = 0
for path in sorted(glob.glob(f"{PDF_DIR}/*.pdf")):
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text() or ""
    name = os.path.basename(path).replace(".pdf", ".txt")
    with open(f"{OUT_DIR}/{name}", "w", encoding="utf-8") as f:
        f.write(text)
    count += 1

print(f"\nRead {count} invoices and saved their text in {OUT_DIR}")