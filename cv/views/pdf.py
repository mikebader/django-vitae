"""Create PDF file of CV to be used in views."""
from django.apps import apps
from django.template import Context, Template
from django.template.loader import get_template

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from cv.settings import CV_PERSONAL_INFO
from cv.templatetags.cvtags import year_range
from cv.models import Position, Article, Book



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

class SubsectionHeader(Paragraph):
    def __init__(self, text, style, *args, **kwargs):
        self.style = style
        Paragraph.__init__(self, text, style=style, *args, **kwargs)

    def draw(self):
        Paragraph.draw(self)

class DateBlock(Paragraph):
    """Create a line that includes a block for a date."""
    def __init__(self, text, date, style, *args, **kwargs):
        self.text = "<para leftIndent=\"54\">" + text + "</para>"
        self.date = date
        self.style = style
        Paragraph.__init__(self, self.text, style=style, *args, **kwargs)

    def wrap(self, aW=396, aH=0):
        w, h = Paragraph.wrap(self, aW, aH)
        self.h = h
        return w, h

    def draw(self):
        self.canv.setFont("Times-Roman", 11)
        self.canv.drawString(0, self.h - 11, self.date)
        Paragraph.draw(self)


class CVPdfStyle:
    """Defines styles for PDF representation of CV."""
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

        self.styles.add(ParagraphStyle(name="SubsectionHeader",
                                      fontName="Times-Italic",
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
                                       allowOrphans=0,))

    def section_header(self, text):
        """Defines a line to be written as a section header."""
        return SectionHeader(text, style=self.styles["SectionHeader"])

    def subsection_header(self, text):
        """Defines a line to be written as a subsection header."""
        return SubsectionHeader(text, style=self.styles["SubsectionHeader"])

    def date_block(self, text, date, *args, **kwargs):
        """Defines a line to be written with the DateBlock style."""
        return DateBlock(text=text, date=date, style=self.styles["Dateblock"])

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

class CVPdfEntryMixin():
    def make_date(self, instance, date_field):
        if type(date_field) == str:
            date = getattr(instance, date_field)
            return '{}'.format(date.year) if date else ''
        return '{0}–{1}'.format(
            getattr(instance, date_field[0]).year,
            getattr(instance, date_field[1]).year
        )

    def get_context_data(self, instance):
        context = {self.model_name: instance}
        return context

    def make_entries(self, template, instances):
        entries = list()
        template = get_template(template)
        for instance in instances:
            instance_dict = dict()
            instance_dict['date'] = ''
            if self.date_field:
                instance_dict['date'] = self.make_date(
                    instance, self.date_field)
            context = self.get_context_data(instance)
            instance_dict['text'] = template.render(context)
            entries.append(instance_dict)
        return entries


class CVPdfSubsectionContainer:
    def __init__(self, subsection_entries):
        self.subsection_entries = subsection_entries


class CVPdfSection(CVPdfEntryMixin):
    def __init__(self, model_name, display_name=None, template=None,
                 date_field=None, subsections=None):
        self.model_name = model_name
        self.model = apps.get_model('cv', self.model_name)
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.model._meta.verbose_name_plural.title()
        if not template:
            template = 'cv/pdf/{}.xml'.format(self.model_name)
        self.template = template
        self.date_field = date_field

        self.entries_exist = False
        if self.model.displayable.all().count() > 0:
            self.entries_exist = True
        self.subsections = subsections
        self.elems = list()

    def make_section_header_name(self):
        return self.display_name

    def make_section_entries(self):
        if self.entries_exist is True:
            if self.subsections:
                subsection_entries = list()
                for s in self.subsections:
                    s_entries = self.make_entries(self.template, s[1])
                    print(s_entries)
                    if s_entries:
                        subsection_entries.append({s[0]: s_entries})
                return CVPdfSubsectionContainer(subsection_entries)
            return self.make_entries(
                self.template,
                self.model.displayable.all())
        return None


class CVPdf(CVPdfStyle):
    """A PDF representation of a CV."""
    def build_primary_positions(self):
        for position in Position.primarypositions.all():
            line = '{}'.format(position.title)
            if position.department:
                line += ', {}'.format(position.department)
            self.cv.append(
                Paragraph(line, self.styles["Infoblock"])
            )

    def build_heading(self):
        self.build_primary_positions()
        for key in ['address', 'phone', 'email']:
            if key in CV_PERSONAL_INFO.keys():
                lines = CV_PERSONAL_INFO[key].split("\n")
                for line in lines:
                    self.cv.append(Paragraph(line, self.styles["Infoblock"]))

    def build_section(self, section_obj):
        entries = section_obj.make_section_entries()
        if entries:
            self.cv.append(self.section_header(
                section_obj.make_section_header_name()))
            if type(entries) == CVPdfSubsectionContainer:
                for subsection in entries.subsection_entries:
                    for k in subsection.keys():
                        self.cv.append(self.subsection_header(k))
                        for e in subsection[k]:
                            self.cv.append(self.date_block(**e))
                        self.cv.append(Spacer(PAGE_WIDTH, 20))
            else:
                for e in entries:
                    self.cv.append(self.date_block(**e))
            self.cv.append(Spacer(PAGE_WIDTH, 20))

    def build_cv(self, file):
        """Combine elements to build a CV from parts."""
        doc = SimpleDocTemplate(file,
                                pagesize=letter,
                                topMargin=MARGINS[0],
                                rightMargin=MARGINS[1],
                                bottomMargin=MARGINS[2],
                                leftMargin=MARGINS[3])
        self.build_heading()
        self.cv.append(Spacer(PAGE_WIDTH, 24))

        degrees = CVPdfSection(
            'degree', display_name='Education', date_field='date_earned')
        self.build_section(degrees)

        positions = CVPdfSection(
            'position', display_name='Employment',
            date_field=('start_date', 'end_date'))
        self.build_section(positions)

        awards = CVPdfSection(
            'award',
            display_name='Honors & Awards', date_field='date',
        )
        self.build_section(awards)

        books = CVPdfSection(
            'book', date_field='pub_date',
            subsections=[
                ('Published', Book.published.all()),
                ('Under Review', Book.revise.all()),
                ('In Preparation', Book.inprep.all())
            ])
        self.build_section(books)

        articles = CVPdfSection(
            'article', date_field='pub_date',
            subsections=[
                ('Published', Article.published.all()),
                ('Under Review', Article.revise.all()),
                ('In Preparation', Article.inprep.all())
            ])
        self.build_section(articles)

        chapters = CVPdfSection('chapter', date_field='pub_date')
        self.build_section(chapters)

        reports = CVPdfSection('report', date_field='pub_date')
        self.build_section(reports)

        grants = CVPdfSection('report', date_field=('start_date', 'end_date'))
        self.build_section(grants)

        otherwriting = CVPdfSection(
            'otherwriting',
            display_name='Op-Eds, Book Reviews, and Other Writing',
            date_field='date')
        self.build_section(otherwriting)

        talks = CVPdfSection('talk')
        self.build_section(talks)

        students = CVPdfSection('student')
        self.build_section(students)

        courses = CVPdfSection('course')
        self.build_section(courses)

        service = CVPdfSection('service')
        self.build_section(service)

        doc.build(
            self.cv,
            onFirstPage=self.myFirstPage,
            onLaterPages=self.myLaterPages
        )
        pdf = file.getvalue()
        file.close()
        return pdf
