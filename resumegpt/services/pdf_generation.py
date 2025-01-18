from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .. import config
import os

class ResumePDFGenerator:
    def __init__(self, template_name: str = "professional"):
        self.styles = getSampleStyleSheet()
        self.template = self._load_template(template_name)
        
    def _load_template(self, template_name: str) -> Dict[str, Any]:
        """Load template configuration."""
        templates = {
            "professional": {
                "fonts": {
                    "heading": ("Helvetica-Bold", 14),
                    "subheading": ("Helvetica-Bold", 12),
                    "body": ("Helvetica", 10)
                },
                "colors": {
                    "primary": colors.HexColor("#2C3E50"),
                    "secondary": colors.HexColor("#7F8C8D"),
                    "accent": colors.HexColor("#3498DB")
                },
                "spacing": {
                    "section": 15,
                    "item": 8
                }
            },
            # Add more templates here
        }
        return templates.get(template_name, templates["professional"])
        
    def generate_pdf(self, resume_data: Dict[str, Any], output_path: str) -> str:
        """Generate PDF resume from structured data."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create story (content elements)
        story = []
        
        # Add header
        story.extend(self._create_header(resume_data['basic']))
        
        # Add sections
        story.extend(self._create_experience_section(resume_data['experiences']))
        story.extend(self._create_education_section(resume_data['education']))
        story.extend(self._create_skills_section(resume_data['skills']))
        story.extend(self._create_projects_section(resume_data['projects']))
        
        # Build PDF
        doc.build(story)
        return output_path 

    def _create_header(self, basic_info: Dict[str, Any]) -> list:
        """Create header section with basic information."""
        story = []
        
        # Name
        name_style = ParagraphStyle(
            'Name',
            parent=self.styles['Heading1'],
            fontSize=self.template['fonts']['heading'][1],
            textColor=self.template['colors']['primary']
        )
        story.append(Paragraph(basic_info['name'], name_style))
        story.append(Spacer(1, 10))
        
        # Contact info in a table
        contact_data = [
            [basic_info.get('email', ''), basic_info.get('phone', '')],
            [basic_info.get('location', ''), ' | '.join(basic_info.get('websites', []))]
        ]
        
        contact_table = Table(
            contact_data,
            colWidths=[250, 250],
            style=TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), self.template['colors']['secondary']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.template['fonts']['body'][0]),
                ('FONTSIZE', (0, 0), (-1, -1), self.template['fonts']['body'][1])
            ])
        )
        story.append(contact_table)
        story.append(Spacer(1, self.template['spacing']['section']))
        return story

    def _create_experience_section(self, experiences: List[Dict]) -> list:
        """Create experience section."""
        story = []
        
        # Section header
        story.append(self._create_section_header("Professional Experience"))
        
        for exp in experiences:
            # Company and title
            company_style = ParagraphStyle(
                'Company',
                parent=self.styles['Heading3'],
                fontSize=self.template['fonts']['subheading'][1],
                textColor=self.template['colors']['primary']
            )
            story.append(Paragraph(f"{exp['company']} - {exp['titles'][0]['name']}", company_style))
            
            # Date and location
            date_loc_style = ParagraphStyle(
                'DateLoc',
                parent=self.styles['Normal'],
                fontSize=self.template['fonts']['body'][1],
                textColor=self.template['colors']['secondary']
            )
            date_text = f"{exp['titles'][0].get('startdate', '')} - {exp['titles'][0].get('enddate', '')}"
            story.append(Paragraph(f"{date_text} | {exp.get('location', '')}", date_loc_style))
            
            # Highlights
            for highlight in exp.get('highlights', []):
                story.append(Paragraph(f"• {highlight}", self.styles['Normal']))
                story.append(Spacer(1, self.template['spacing']['item']))
                
            story.append(Spacer(1, self.template['spacing']['section']))
        
        return story

    def _create_section_header(self, text: str) -> Paragraph:
        """Create a section header with consistent styling."""
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=self.template['fonts']['heading'][1],
            textColor=self.template['colors']['primary'],
            spaceAfter=self.template['spacing']['item']
        )
        return Paragraph(text, header_style) 