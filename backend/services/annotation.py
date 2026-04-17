import fitz

async def create_annotated_pdf(original_pdf_path: str, output_path: str, evaluations: list[dict]):
    """
    Uses PyMuPDF to draw text annotations (marks, feedback ticks) directly onto the PDF.
    """
    try:
        doc = fitz.open(original_pdf_path)
        
        # Simple annotation on the first page for demonstration
        if len(doc) > 0:
            page = doc[0]
            y_offset = 50
            
            # Add a big header with total marks
            total_marks = sum(e["marks"] for e in evaluations)
            max_total = sum(e["max_marks"] for e in evaluations)
            
            page.insert_text((50, y_offset), f"AI MARKED: {total_marks}/{max_total}", fontsize=20, color=(1, 0, 0))
            y_offset += 30
            
            for ev in evaluations:
                q_label = f"Q{ev['question_number']}{ev['question_part'] or ''}"
                text = f"{q_label}: {ev['marks']}/{ev['max_marks']} - {ev['feedback']}"
                page.insert_text((50, y_offset), text, fontsize=10, color=(0, 0, 1))
                y_offset += 20
                
        doc.save(output_path)
    except Exception as e:
        print(f"Error annotating PDF: {e}")
        # Create an empty file to prevent pipeline crashing completely
        with open(output_path, "wb") as f:
            f.write(b"")
