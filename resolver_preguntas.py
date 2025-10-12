# Instalación de librerías necesarias (ejecutar solo una vez)
# pip install pymupdf reportlab pandas

import fitz  # PyMuPDF
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

#input_pdf = "1600_preguntas_constitucion_espanola_1.pdf"
input_pdf = r"C:\PROGRAMACION\Python\constitucion\1600_preguntas_constitucion_espanola_1.pdf"
output_pdf = "1600_preguntas_constitucion_espanola_resuelto.pdf"

# Paso 1: extraer respuestas correctas (a partir de la página 95)
doc = fitz.open(input_pdf)
answers = {}
for page_num in range(94, len(doc)):  # página 95 en adelante
    page = doc[page_num]
    text = page.get_text("text")
    for line in text.splitlines():
        match = re.match(r"(\d+)\.\s*-\s*([a-dA-D])", line.strip())
        if match:
            q_num = int(match.group(1))
            ans = match.group(2).lower()
            answers[q_num] = ans

# Paso 2: extraer preguntas y opciones (páginas 1–94)
questions = {}
for page_num in range(0, 94):
    page = doc[page_num]
    text = page.get_text("text")
    lines = text.splitlines()
    current_q = None
    for line in lines:
        q_match = re.match(r"^(\d+)\.-", line.strip())
        if q_match:
            current_q = int(q_match.group(1))
            questions[current_q] = {"pregunta": line.strip(), "opciones": []}
        elif current_q and re.match(r"^[a-d]\)", line.strip()):
            questions[current_q]["opciones"].append(line.strip())

# Paso 3: generar el nuevo PDF
styles = getSampleStyleSheet()
normal = styles["Normal"]
highlight = ParagraphStyle(
    "Correcta",
    parent=normal,
    textColor=colors.green,
    fontName="Helvetica-Bold",
    underline=True   # 👈 subrayado
)

story = []
for q_num in sorted(questions.keys()):
    q = questions[q_num]
    # Pregunta
    story.append(Paragraph(q["pregunta"], normal))
    story.append(Spacer(1, 4))
    # Opciones
    for opt in q["opciones"]:
        letra = opt[0].lower()
        if q_num in answers and letra == answers[q_num]:
            #story.append(Paragraph(opt, highlight))  # correcta en verde y negrita
            story.append(Paragraph("✔ " + opt, highlight))
        else:
            story.append(Paragraph(opt, normal))
    story.append(Spacer(1, 10))

doc_out = SimpleDocTemplate(output_pdf, pagesize=A4, leftMargin=40, rightMargin=40)
doc_out.build(story)

print("✅ PDF generado:", output_pdf)
