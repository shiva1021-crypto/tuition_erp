# finance/utils.py
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def generate_receipt_pdf(payment):
    """
    Draws a PDF receipt for a given FeePayment object.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 1. Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "FEE RECEIPT")
    
    # 2. Institute Info (We get this from the tenant schema context, usually just hardcode or fetch name)
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, "Tuition Center ERP") 
    p.drawString(50, height - 95, "Official Payment Record")

    p.line(50, height - 110, width - 50, height - 110)

    # 3. Payment Details
    y = height - 150
    p.setFont("Helvetica", 12)
    
    # Helper to draw rows
    def draw_row(label, value, y_pos):
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_pos, label)
        p.setFont("Helvetica", 12)
        p.drawString(200, y_pos, str(value))
        return y_pos - 30

    # Data Extraction
    student_name = payment.installment.allocation.student.user.get_full_name()
    enrollment = payment.installment.allocation.student.enrollment_number
    fee_type = payment.installment.allocation.fee_structure.name
    amount = f"Rs. {payment.amount}"
    date = payment.payment_date.strftime("%Y-%m-%d")
    mode = payment.mode
    txn_id = payment.transaction_id or "N/A"

    y = draw_row("Receipt No:", f"RCPT-{payment.id}", y)
    y = draw_row("Student Name:", student_name, y)
    y = draw_row("Enrollment ID:", enrollment, y)
    y = draw_row("Fee Type:", fee_type, y)
    y = draw_row("Payment Date:", date, y)
    y = draw_row("Payment Mode:", mode, y)
    y = draw_row("Transaction Ref:", txn_id, y)

    # 4. Total Amount Box
    p.setStrokeColor(colors.black)
    p.rect(50, y - 20, 400, 40, fill=0)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(60, y - 5, f"Amount Paid:  {amount}")

    # 5. Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "This is a computer-generated receipt and does not require a signature.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer