from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.models import Dataset, DatasetAuthorship
from cv.settings import STUDENT_LEVELS

from tests.cvtests import AuthorshipTestCase


@attr('dataset')
class DatasetTestCase(AuthorshipTestCase):

    @classmethod
    def setUp(cls):
        super(DatasetTestCase, cls).setUp()
        params = {
            'title': 'This is a test dataset',
            'short_title': 'Test Dataset',
            'slug': 'test-dataset',
            'pub_date': '2010-01-01'
        }
        d = Dataset.objects.create(**params)
        auth = DatasetAuthorship(
            dataset=d, collaborator=cls.dubois, display_order=1)
        auth.save()

    def test_dataset_str(self):
        """Test string representation of dataset."""
        d = Dataset.objects.get(slug='test-dataset')
        self.assertEqual('Test Dataset', str(d))

    def test_get_absolute_url(self):
        """Test that instance returns correct URL"""
        d = Dataset.objects.get(slug='test-dataset')
        self.assertEqual('/datasets/test-dataset', d.get_absolute_url())

    def test_list_view(self):
        """Test valid url and template used for dataset list."""
        response = self.client.get('/datasets/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv/lists/dataset_list.html')

    def test_detail_view(self):
        d = Dataset.objects.get(slug='test-dataset')
        response = self.client.get(d.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv/details/dataset_detail.html')

    def test_dataset_single_author(self):
        """Test that single authorship works correctly."""
        d = Dataset.objects.get(slug='test-dataset')
        self.assertAuthorshipLength(d, 1)

    def test_dataset_multiple_author(self):
        """Test that authorship model returns correct number of authors."""
        d = Dataset.objects.get(slug='test-dataset')
        DatasetAuthorship(
            dataset=d, collaborator=self.dill, display_order=2,
            student_colleague=STUDENT_LEVELS['DOCTORAL_STUDENT']
            ).save()
        self.assertAuthorshipLength(d, 2)


