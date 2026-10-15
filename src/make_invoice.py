from reportlab.lib.pagesizes import A4          # A4 page size
from reportlab.pdfgen import canvas             # tool for drawing on a PDF

c = canvas.Canvas("data/invoice_001.pdf", pagesize=A4)   # create an empty PDF in the data folder
width, height = A4                                        # page size in points

c.setFont("Helvetica-Bold", 18)
c.drawString(50, height - 60, "INVOICE")                  # title near the top

c.setFont("Helvetica", 11)
c.drawString(50, height - 100, "Vendor: Sharma Electronics Pvt Ltd")
c.drawString(50, height - 118, "Invoice No: INV-0001")
c.drawString(50, height - 136, "Date: 2026-10-14")

c.drawString(50, height - 180, "Item")                    # table header
c.drawString(300, height - 180, "Qty")
c.drawString(380, height - 180, "Price")

items = [("Laptop", 1, 45000), ("Mouse", 2, 500)]         # our fake products
y = height - 200
total = 0
for name, qty, price in items:                            # one row per item
    c.drawString(50, y, name)
    c.drawString(300, y, str(qty))
    c.drawString(380, y, str(price))
    total += qty * price                                  # add to the grand total
    y -= 18                                               # move down for the next row

c.setFont("Helvetica-Bold", 11)
c.drawString(50, y - 20, f"Total: {total}")               # write the total at the end

c.save()                                                  # write the file to disk
print("Invoice created, total =", total)
