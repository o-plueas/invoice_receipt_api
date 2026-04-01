

# invoices/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.conf import settings
from datetime import datetime
import os

def generate_invoice_pdf(invoice):
    """Generate a professional PDF for an invoice"""
    from settings_app.models import SystemSettings
    system_settings = SystemSettings.load()
    
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'invoices', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = f"invoice_{invoice.invoice_number}.pdf"
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
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Header info
    header_data = [
        [system_settings.company_name, f"Invoice #: {invoice.invoice_number}"],
        [system_settings.company_address, f"Date: {invoice.issue_date.strftime('%B %d, %Y')}"],
        [system_settings.company_email, f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}"],
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Bill to
    story.append(Paragraph("<b>BILL TO:</b>", styles['Heading3']))
    story.append(Paragraph(invoice.quote.name, styles['Normal']))
    story.append(Paragraph(invoice.quote.email, styles['Normal']))
    story.append(Paragraph(invoice.quote.phone, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Line items table
    line_items_data = [['Description', 'Qty', 'Unit Price', 'Amount']]
    
    for item in invoice.line_items.all():
        line_items_data.append([
            item.title,
            str(item.quantity),
            f"{system_settings.currency_symbol}{item.unit_price:,.2f}",
            f"{system_settings.currency_symbol}{item.amount:,.2f}"
        ])
    
    # Add totals
    line_items_data.append(['', '', 'Subtotal:', f"{system_settings.currency_symbol}{invoice.subtotal:,.2f}"])
    line_items_data.append(['', '', f'Tax ({invoice.tax_rate}%):', f"{system_settings.currency_symbol}{invoice.tax_amount:,.2f}"])
    line_items_data.append(['', '', 'TOTAL:', f"{system_settings.currency_symbol}{invoice.total:,.2f}"])
    
    items_table = Table(line_items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(system_settings.pdf_primary_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Payment instructions
    story.append(Paragraph("<b>Payment Instructions:</b>", styles['Heading3']))
    story.append(Paragraph(system_settings.payment_instructions, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    if system_settings.bank_details:
        story.append(Paragraph("<b>Bank Details:</b>", styles['Heading3']))
        story.append(Paragraph(system_settings.bank_details, styles['Normal']))
    
    # Footer
    footer_text = f"""
    <para align=center>
    <font size=8 color='grey'>
    {system_settings.email_footer}<br/>
    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </font>
    </para>
    """
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(story)
    
    return f"invoices/pdfs/{filename}"
