from django.db import models
from django.utils.translation import gettext_lazy as _

from cv.settings import STUDENT_LEVELS_CHOICES

from .people import Collaborator, Student


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
