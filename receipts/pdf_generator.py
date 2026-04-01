

# receipts/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.conf import settings
from datetime import datetime
import os

def generate_receipt_pdf(receipt):
    """Generate a professional PDF for a receipt"""
    from settings_app.models import SystemSettings
    system_settings = SystemSettings.load()
    
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'receipts', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = f"receipt_{receipt.receipt_number}.pdf"
    filepath = os.path.join(pdf_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor(system_settings.pdf_primary_color),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Add logo
    if system_settings.company_logo:
        try:
            logo = Image(system_settings.company_logo.path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    story.append(Paragraph("PAYMENT RECEIPT", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Receipt info
    receipt_info = [
        ['Receipt Number:', receipt.receipt_number],
        ['Date:', receipt.created_at.strftime('%B %d, %Y')],
        ['Invoice Number:', receipt.invoice.invoice_number],
        ['Payment Method:', receipt.payment_method],
        ['Transaction ID:', receipt.transaction_id],
    ]
    
    receipt_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(system_settings.pdf_primary_color)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Payment details
    story.append(Paragraph("<b>PAYMENT DETAILS</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice = receipt.invoice
    
    payment_details = [
        ['Description', 'Amount'],
        ['Subtotal', f"{system_settings.currency_symbol}{invoice.subtotal:,.2f}"],
        [f'Tax ({invoice.tax_rate}%)', f"{system_settings.currency_symbol}{invoice.tax_amount:,.2f}"],
        ['Total Amount', f"{system_settings.currency_symbol}{invoice.total:,.2f}"],
        ['Amount Paid', f"{system_settings.currency_symbol}{receipt.amount_paid:,.2f}"],
    ]
    
    payment_table = Table(payment_details, colWidths=[4*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(system_settings.pdf_primary_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (1, -1), 14),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#dcfce7')),
        ('TEXTCOLOR', (0, -1), (1, -1), colors.HexColor('#166534')),
    ]))
    
    story.append(payment_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Paid to
    story.append(Paragraph("<b>PAID TO:</b>", styles['Heading3']))
    story.append(Paragraph(system_settings.company_name, styles['Normal']))
    story.append(Paragraph(system_settings.company_address, styles['Normal']))
    story.append(Paragraph(system_settings.company_email, styles['Normal']))
    story.append(Spacer(1, 0.4*inch))
    
    # Customer info
    story.append(Paragraph("<b>CUSTOMER:</b>", styles['Heading3']))
    story.append(Paragraph(invoice.quote.name, styles['Normal']))
    story.append(Paragraph(invoice.quote.email, styles['Normal']))
    story.append(Paragraph(invoice.quote.phone, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Thank you message
    thank_you_style = ParagraphStyle(
        'ThankYou',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor(system_settings.pdf_primary_color),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph("<b>Thank you for your payment!</b>", thank_you_style))
    
    # Footer
    footer_text = f"""
    <para align=center>
    <font size=8 color='grey'>
    This is a computer-generated receipt. No signature required.<br/>
    {system_settings.email_footer}<br/>
    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </font>
    </para>
    """
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(story)
    
    return f"receipts/pdfs/{filename}"
