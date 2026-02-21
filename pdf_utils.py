import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n\n"
    except Exception as e:
        print(f"Extraction error: {e}")
    return text.strip()


def generate_optimized_pdf(text: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)

    styles = getSampleStyleSheet()
    heading = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=12)
    normal = styles['Normal']
    bullet = ParagraphStyle('Bullet', parent=normal, leftIndent=20, bulletIndent=10, spaceAfter=6)

    elements = []

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 0.2*inch))
            continue

        if line.isupper() or len(line) < 60 and (':' in line or line.endswith('.')):
            elements.append(Paragraph(line, heading))
        elif line.startswith('•'):
            elements.append(Paragraph(line, bullet))
        else:
            elements.append(Paragraph(line, normal))

    doc.build(elements)
    print(f"✅ PDF generated: {output_path}")


def generate_cover_letter_pdf(cover_text: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(cover_text.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(elements)
    print(f"✅ Cover letter PDF generated: {output_path}")