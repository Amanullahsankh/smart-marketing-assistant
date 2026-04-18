from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os
from textwrap import wrap

def create_portfolio(business_name, services_text, filename=None):
    """Generate a professional, readable PDF portfolio with proper text wrapping."""
    if filename is None:
        filename = f"{business_name.replace(' ', '_')}_Portfolio.pdf"

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    left_margin = 60
    right_margin = width - 60
    text_width = right_margin - left_margin

    # Header
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left_margin, height - 50, f"{business_name} – Portfolio")

    c.setFont("Helvetica", 10)
    c.drawRightString(right_margin, height - 65, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Intro
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, height - 110, "Welcome to your Smart Marketing Portfolio!")

    intro_text = (
        "This document presents an overview of our company's key services and expertise. "
        "We focus on innovation, AI-driven automation, and digital transformation to help "
        "clients achieve scalable and measurable growth."
    )
    y = height - 130
    c.setFont("Helvetica", 11)
    for line in wrap(intro_text, width=90):
        c.drawString(left_margin, y, line)
        y -= 15

    # Services
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.drawString(left_margin, y, "Our Key Services:")
    y -= 20
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)

    for line in services_text.splitlines():
        line = line.strip("•-* ")
        if not line:
            continue
        if y < 120:
            c.showPage()
            y = height - 100
        for wrapped_line in wrap(f"• {line}", width=90):
            c.drawString(left_margin + 20, y, wrapped_line)
            y -= 15
        y -= 5

    # Impact section
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.drawString(left_margin, y, "Our Impact")
    y -= 20
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    impact_text = (
        "We empower businesses by integrating AI, data analytics, and automation to boost productivity, "
        "enhance customer experience, and reduce operational costs. Our solutions help companies innovate "
        "faster, scale efficiently, and achieve measurable success."
    )
    for line in wrap(impact_text, width=90):
        c.drawString(left_margin, y, line)
        y -= 15

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.drawString(left_margin, 40, "Smart Marketing Assistant – Auto-Generated Portfolio | Powered by AI Automation")

    c.save()
    print(f"✅ Professional Portfolio (wrapped text) created: {os.path.abspath(filename)}")
    return filename
