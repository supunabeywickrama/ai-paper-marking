from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from backend.models import ExtractedContent

async def create_clean_pdf(output_path: str, extracted_contents: list[ExtractedContent]):
    """
    Generates a clean, rewritten PDF document using ReportLab.
    This helps students read their garbled handwriting in a clean digital format.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    y_offset = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_offset, "Clean Reconstructed Answer Sheet")
    y_offset -= 40
    
    c.setFont("Helvetica", 12)
    for content in extracted_contents:
        if y_offset < 50:
            c.showPage()
            y_offset = height - 50
            c.setFont("Helvetica", 12)
            
        q_label = f"Question {content.question_number}{content.question_part or ''}"
        c.drawString(50, y_offset, q_label)
        y_offset -= 20
        
        # Handle long text wrapping (simplified for this orchestrator)
        text = str(content.reconstructed_text or content.raw_extracted or "[Visual Element]")
        chunks = [text[i:i+80] for i in range(0, len(text), 80)]
        for chunk in chunks:
            c.drawString(70, y_offset, chunk)
            y_offset -= 15
            if y_offset < 50:
                c.showPage()
                y_offset = height - 50
                c.setFont("Helvetica", 12)
        y_offset -= 10
        
    c.save()
