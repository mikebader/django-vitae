"""Create PDF file of CV to be used in views."""
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from cv.settings import CV_PERSONAL_INFO


# Define dimensions
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]
MARGINS = [inch, inch, inch, inch]  # Top, Right, Bottom, Left
TEXT_WIDTH = PAGE_WIDTH - (MARGINS[1] + MARGINS[3]) - 12
pageinfo = "LastName"

class SectionHeader(Paragraph):
    """Create a section header instance with appropriate style."""
    def __init__(self, text, style, *args, **kwargs):
        self.style = style
        Paragraph.__init__(self, text, style=style, *args, **kwargs)

    def draw(self):
        Paragraph.draw(self)
        self.canv.setLineWidth(.5)
        self.canv.line(-6, -3, TEXT_WIDTH + 6, -3)


class DateBlock(Paragraph):
    """Create a line that includes a block for a date."""
    def __init__(self, text, date, style, *args, **kwargs):
        self.text = "<para leftIndent=\"54\">" + text + "</para>"
        self.date = date
        self.style = style
        Paragraph.__init__(self, self.text, style, *args, **kwargs)

    def wrap(self, aW=396, aH=0):
        w, h = Paragraph.wrap(self, aW, aH)
        self.h = h
        return w, h

    def draw(self):
        self.canv.setFont("Times-Roman", 11)
        self.canv.drawString(0, self.h - 11, self.date)
        Paragraph.draw(self)


class CVPdf(object):
    """Instance of a PDF representation of a CV."""

    def __init__(self):
        """Creates styles and container to hold CV information."""
        self.cv = list()
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name="Infoblock",
                                       fontName="Times-Roman",
                                       fontSize=11,
                                       alignment=TA_CENTER,))

        self.styles.add(ParagraphStyle(name="SectionHeader",
                                       fontName="Times-Bold",
                                       fontSize=13,
                                       alignment=TA_LEFT,
                                       spaceBefore=0,
                                       spaceAfter=3,
                                       leftIndent=0))

        self.styles.add(ParagraphStyle(name="Dateblock",
                                       fontName="Times-Roman",
                                       fontSize=11,
                                       alignment=TA_LEFT,
                                       bulletFontSize=11,
                                       spaceAfter=6,
                                       leftIndent=54,
                                       allowOrphans=1,))

    def date_block(self, text, date, *args, **kwargs):
        """Defines a line to be written with the DateBlock style."""
        return DateBlock(text, date, self.styles["Dateblock"])

    def section_header(self, text):
        """Defines a line to be written as a section header."""
        return SectionHeader(text, self.styles["SectionHeader"])

    # Define page styles
    def myFirstPage(self, canvas, doc):
        """Creates canvas to represent style for first page."""
        canvas.saveState()
        canvas.setFont('Times-Bold', 13)
        canvas.drawCentredString(
            TEXT_WIDTH / 2.0 + MARGINS[3] + 6,
            PAGE_HEIGHT - MARGINS[0] - 6,
            CV_PERSONAL_INFO['name']
        )
        # canvas.setLineWidth(1.5)
        # canvas.line(MARGINS[3],PAGE_HEIGHT-(MARGINS[0]+6),PAGE_WIDTH-MARGINS[1],PAGE_HEIGHT-(MARGINS[0]+6))
        canvas.setFont('Times-Roman', 11)
        canvas.drawString(PAGE_WIDTH - inch, 0.75 * inch, "%d" % doc.page)
        canvas.restoreState()

    def myLaterPages(self, canvas, doc):
        """Creates canvas to represent style for non-first pages."""
        canvas.saveState()
        canvas.setFont('Times-Roman', 11)
        canvas.drawString(
            PAGE_WIDTH - inch, 0.75 * inch, "Page %d" % (doc.page)
        )
        canvas.restoreState()

    def build_heading(self):
        for key in ['address', 'phone', 'email']:
            if key in CV_PERSONAL_INFO.keys():
                lines = CV_PERSONAL_INFO[key].split("\n")
                for line in lines:
                    self.cv.append(Paragraph(line, self.styles["Infoblock"]))

    def build_cv(self, file):
        """Combine elements to build a CV from parts."""
        educ = [
            {"date": "2009",
             "text": "Ph.D., Sociology, University of Michigan, Ann Arbor, Michigan"},
            {"date": "2003",
             "text": ("B.A., Architecture & Art History, "
                      "Rice University, Houston, Texas")}
        ]
        doc = SimpleDocTemplate(file,
                                pagesize=letter,
                                topMargin=MARGINS[0],
                                rightMargin=MARGINS[1],
                                bottomMargin=MARGINS[2],
                                leftMargin=MARGINS[3])
        self.build_heading()
        self.cv.append(Spacer(PAGE_WIDTH, 24))
        self.cv.append(self.section_header("Education"))
        for e in educ:
            self.cv.append(self.date_block(**e))
        doc.build(
            self.cv,
            onFirstPage=self.myFirstPage,
            onLaterPages=self.myLaterPages
        )
        pdf = file.getvalue()
        file.close()
        return pdf
