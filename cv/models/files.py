from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cv.settings import FILE_TYPES_CHOICES

from markdown import markdown


def cv_file_path(instance, filename):
        """Defines path for CV files."""
        return 'cv/{0}/{1}/{2}'.format(
            instance.content_type, instance.object_id, filename)


class CVFile(models.Model):
    """
    Model for storing files related to CV objects.

    :param file: The file to be uploaded.
    :type name: :class:`django.db.models.FileField`



    :attr:`Field.default`
        The default value for the field. This can be a value or a callable
        object. If callable it will be called every time a new object is
        created.

    :attr:`~CVFile.file`

        :class:`django.db.models.FileField` instance (required)

        The file to be uploaded.

    :attr:`~CVFile.name`

        string; maximum length of 80 characters (required)

        The name to be used when the file is displayed

    type : integer (required)
        Type of file defined by choices defined in ``CV_FILE_TYPES`` setting

    is_primary : boolean
        Indicates that the file is the main document associated with an instace
        of a model in :class:`cv` (for example, the accepted manuscript related
        to an instance of :class:`cv.models.Article` or slide presentation for
        an instance of :class:`cv.models.Talk`). Values of ``True`` are
        ordered first in default object manager.

    copyright : string; maximum length of 200 characters
        Allows user to include copyright information regarding the file.

    description : string
        A description of the file using Markdown syntax (converts Markdown
        to HTML and saves in ``description_html`` field that cannot be edited
        directly.
    """

    file = models.FileField(_('file'), upload_to=cv_file_path)
    name = models.CharField(max_length=80)
    type = models.IntegerField(choices=FILE_TYPES_CHOICES)
    is_primary = models.BooleanField(default=False)
    copyright = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(
        ContentType,
        related_name='cv_file_content_type',
        limit_choices_to=models.Q(app_label='cv'),
        on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    description_html = models.TextField(blank=True, editable=False)

    class Meta:
        verbose_name = _('CV file')
        verbose_name_plural = _('CV files')
        ordering = ['-is_primary']

    def __str__(self):
        """String representation of :class:`cv.models.CVFile`."""
        return "%s [%s]" % (self.object, self.name)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """Saves instance of :class:`cv.models.CVFile`.

        Translates ``description`` field content to HTML and saves
        in ``description_html`` field.
        """
        self.description_html = markdown(self.description)
        super(CVFile, self).save(force_insert, force_update, *args, **kwargs)
