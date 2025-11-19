
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class FileService:
    def __init__(self):
        """Initialize file service"""
        self.temp_dir = tempfile.gettempdir()
        self.styles = getSampleStyleSheet()

    def export_to_pdf(self, meeting, action_items):
        """
        Export meeting summary to PDF
        Args:
            meeting (dict): Meeting details
            action_items (list): List of action items
        Returns:
            str: Path to generated PDF file
        """
        try:
            # Create temporary PDF file
            pdf_filename = f"meeting_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.temp_dir, pdf_filename)

            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(f"Meeting Summary: {meeting.get('title', 'Untitled')}", title_style))
            story.append(Spacer(1, 20))

            # Meeting Details
            details_data = [
                ['Date:', meeting.get('date', 'Not specified')],
                ['Attendees:', meeting.get('attendees', 'Not specified')],
                ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]

            details_table = Table(details_data, colWidths=[1.5*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))

            story.append(details_table)
            story.append(Spacer(1, 20))

            # Meeting Summary
            story.append(Paragraph("Meeting Summary", self.styles['Heading2']))
            summary_text = meeting.get('summary', 'No summary available')
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Action Items
            if action_items:
                story.append(Paragraph("Action Items", self.styles['Heading2']))

                # Create action items table
                ai_data = [['Description', 'Assignee', 'Due Date', 'Priority']]
                for item in action_items:
                    ai_data.append([
                        item.get('description', '')[:60] + ('...' if len(item.get('description', '')) > 60 else ''),
                        item.get('assignee', 'Unassigned'),
                        item.get('due_date', 'Not specified'),
                        item.get('priority', 'Medium')
                    ])

                ai_table = Table(ai_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1*inch])
                ai_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(ai_table)

            # Build PDF
            doc.build(story)
            return pdf_path

        except Exception as e:
            print(f"Error creating PDF: {e}")
            raise Exception(f"Failed to export PDF: {e}")

    def export_to_text(self, meeting, action_items):
        """
        Export meeting summary to plain text
        Args:
            meeting (dict): Meeting details
            action_items (list): List of action items
        Returns:
            str: Formatted text content
        """
        try:
            lines = []
            lines.append("=" * 60)
            lines.append(f"MEETING SUMMARY: {meeting.get('title', 'Untitled').upper()}")
            lines.append("=" * 60)
            lines.append("")

            # Meeting details
            lines.append("MEETING DETAILS:")
            lines.append(f"Date: {meeting.get('date', 'Not specified')}")
            lines.append(f"Attendees: {meeting.get('attendees', 'Not specified')}")
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            # Summary
            lines.append("MEETING SUMMARY:")
            lines.append("-" * 20)
            summary = meeting.get('summary', 'No summary available')
            lines.append(summary)
            lines.append("")

            # Action items
            if action_items:
                lines.append("ACTION ITEMS:")
                lines.append("-" * 20)
                for i, item in enumerate(action_items, 1):
                    lines.append(f"{i}. {item.get('description', 'No description')}")
                    lines.append(f"   Assignee: {item.get('assignee', 'Unassigned')}")
                    lines.append(f"   Due Date: {item.get('due_date', 'Not specified')}")
                    lines.append(f"   Priority: {item.get('priority', 'Medium')}")
                    lines.append("")

            lines.append("=" * 60)
            lines.append("Generated by AI Meeting Notes Generator")
            lines.append("=" * 60)

            return "\n".join(lines)

        except Exception as e:
            print(f"Error creating text export: {e}")
            raise Exception(f"Failed to export text: {e}")

    def save_transcription(self, transcription, filename):
        """
        Save transcription to file
        Args:
            transcription (str): Meeting transcription
            filename (str): Output filename
        Returns:
            str: Path to saved file
        """
        try:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcription)
            return filepath
        except Exception as e:
            print(f"Error saving transcription: {e}")
            raise Exception(f"Failed to save transcription: {e}")

    def cleanup_temp_files(self, max_age_hours=24):
        """
        Clean up temporary files older than specified hours
        Args:
            max_age_hours (int): Maximum age in hours for temp files
        """
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('meeting_'):
                    filepath = os.path.join(self.temp_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                        os.remove(filepath)
                        print(f"Cleaned up old temp file: {filename}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
