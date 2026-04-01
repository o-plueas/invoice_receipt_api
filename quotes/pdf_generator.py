
# quotes/pdf_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
from datetime import datetime
import os

def generate_quote_pdf(quote):
    """Generate a professional PDF for a quote"""
    from settings_app.models import SystemSettings
    system_settings = SystemSettings.load()
    
    # Create directory if not exists
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'quotes', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # File path
    filename = f"quote_{quote.reference_number}.pdf"
    filepath = os.path.join(pdf_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(system_settings.pdf_primary_color),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(system_settings.pdf_primary_color),
        spaceAfter=12,
    )
    
    # Add logo if exists
    if system_settings.company_logo:
        try:
            logo = Image(system_settings.company_logo.path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    story.append(Paragraph("QUOTE", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Company info and quote details side by side
    company_info = [
        [Paragraph(f"<b>{system_settings.company_name}</b>", styles['Normal'])],
        [Paragraph(system_settings.company_address, styles['Normal'])],
        [Paragraph(f"Email: {system_settings.company_email}", styles['Normal'])],
        [Paragraph(f"Phone: {system_settings.company_phone}", styles['Normal'])],
    ]
    
    quote_info = [
        [Paragraph(f"<b>Quote #:</b> {quote.reference_number}", styles['Normal'])],
        [Paragraph(f"<b>Date:</b> {quote.created_at.strftime('%B %d, %Y')}", styles['Normal'])],
        [Paragraph(f"<b>Status:</b> {quote.get_status_display()}", styles['Normal'])],
    ]
    
    header_table = Table(
        [[company_info, quote_info]],
        colWidths=[3.5*inch, 3*inch]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Client information
    story.append(Paragraph("CLIENT INFORMATION", heading_style))
    client_data = [
        ['Name:', quote.name],
        ['Email:', quote.email],
        ['Phone:', quote.phone],
        ['Service Type:', quote.get_service_type_display()],
    ]
    
    client_table = Table(client_data, colWidths=[1.5*inch, 4.5*inch])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(system_settings.pdf_primary_color)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(client_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Message/Requirements
    story.append(Paragraph("PROJECT REQUIREMENTS", heading_style))
    story.append(Paragraph(quote.message, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
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
    
    # Build PDF
    doc.build(story)
    
    return f"quotes/pdfs/{filename}"

