from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, darkblue
import re

def create_pdf_from_markdown(markdown_file, pdf_file):
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=darkblue,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=blue,
        spaceBefore=20
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=black,
        leftIndent=20,
        fontName='Helvetica-Bold'
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        textColor=black,
        leftIndent=40,
        rightIndent=20
    )
    
    # Story to hold all elements
    story = []
    
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into sections
    sections = content.split('## ')
    
    # Add title
    story.append(Paragraph("Customer Support Q&A Database", title_style))
    story.append(Spacer(1, 20))
    
    for section in sections[1:]:  # Skip the first empty section
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Section title (first line)
        section_title = lines[0].strip()
        story.append(Paragraph(section_title, heading_style))
        
        # Process the rest of the section
        current_text = ""
        in_question = False
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a question (starts with **Q:)
            if line.startswith('**Q:'):
                # If we have accumulated text, add it as an answer
                if current_text and in_question:
                    story.append(Paragraph(current_text.strip(), answer_style))
                    current_text = ""
                
                # Extract question text
                question_text = line.replace('**Q:', '').replace('**', '').strip()
                story.append(Paragraph(question_text, question_style))
                in_question = True
                
            elif line.startswith('**A:'):
                # Extract answer text
                answer_text = line.replace('**A:', '').replace('**', '').strip()
                story.append(Paragraph(answer_text, answer_style))
                in_question = False
                
            elif in_question and line.startswith('**'):
                # This might be the answer part
                answer_text = line.replace('**', '').strip()
                story.append(Paragraph(answer_text, answer_style))
                in_question = False
                
            elif in_question:
                # Continue building the answer
                current_text += line + " "
        
        # Add any remaining text
        if current_text and in_question:
            story.append(Paragraph(current_text.strip(), answer_style))
        
        story.append(Spacer(1, 20))
    
    # Build the PDF
    doc.build(story)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    create_pdf_from_markdown('customer_support_qa.md', 'customer_support_qa.pdf') 