from django.db import models
from django.utils.translation import gettext_lazy as _

from cv.settings import STUDENT_LEVELS_CHOICES

from .people import Collaborator, Student
from .publications import Article, Book, Chapter, Report
from .works import Grant, Talk, Dataset


class CollaborationModel(models.Model):
    """Abstract model connecting collaborators to products.

    Collaborators are tied to the user through specific collaborations. For
    example, a paper with two authors--the user and a
    collaborator--represents one *collaboration* that has unique
    characteristics such as the order of authorship. A second paper by the
    same two authors would represent a new collaboration. The abstract
    collaboration model allows for these connections across a variety of
    different collaboration types.

    Fields:

    collaborator : ForeignKey field to the Collaborator model.

    print_middle : Should the collaborator's middle initial be inlcuded in
    the CV entry?

    display_order : Integer representing the order in which
    collaborators are listed.
    """
    collaborator = models.ForeignKey(Collaborator, on_delete=models.CASCADE)
    print_middle = models.BooleanField(
        default=True,
        help_text=_('Display author\'s middle initial?'))
    display_order = models.IntegerField(
        help_text=_('Order that collaborators should be listed'))

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.collaborator)


class StudentCollaborationModel(models.Model):
    """Abstract collaboration model to note collaborations with students.

    Often advisors wish to highlight collaborations with students on CVs.
    This abstract class adds a single field that allows the user to
    indicate whether a collaborator was a student and, if so, the level
    of the student (e.g., undergrad, masters, doctoral).
    """

    student_colleague = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True


# Publications
class ArticleAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to article."""

    article = models.ForeignKey(
        Article, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['article', 'display_order']
        unique_together = ('article', 'display_order')


class BookAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store authorship object relating collaborators to book."""

    book = models.ForeignKey(
        Book, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['book', 'display_order']
        unique_together = ('book', 'display_order')


class ChapterAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to article."""

    chapter = models.ForeignKey(
        Chapter, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = (('chapter', 'display_order'))


class ChapterEditorship(CollaborationModel):
    """Store object relating editors to chapter."""

    chapter = models.ForeignKey(
        Chapter, related_name="editorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = (('chapter', 'display_order'))


class ReportAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to report."""

    report = models.ForeignKey(
        Report, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = ('report', 'display_order')


# Works
class GrantCollaboration(CollaborationModel):
    """Store object relating collaborators to grant."""

    grant = models.ForeignKey(
        Grant, related_name="collaboration", on_delete=models.PROTECT)
    is_pi = models.BooleanField(
        _('Is principal investigator?'), default=False)
    role = models.CharField(
        _('Role'), max_length=50, blank=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return str(self.collaborator)


class TalkCollaboration(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to article."""

    talk = models.ForeignKey(
        Talk, related_name="collaboration", on_delete=models.CASCADE)

    class Meta:
        ordering = ['talk', 'display_order']
        unique_together = ('talk', 'display_order')


class DatasetCollaboration(CollaborationModel, StudentCollaborationModel):
    """Store object relating creators of dataset to a dataset instance."""

    dataset = models.ForeignKey(
        Dataset, related_name="collaboration", on_delete=models.CASCADE)

    class Meta:
        ordering = ['dataset', 'display_order']
        unique_together = ('dataset', 'display_order')
