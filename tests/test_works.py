from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.models import Dataset, DatasetAuthorship, \
                      OtherWriting
from cv.settings import STUDENT_LEVELS

from tests.cvtests import AuthorshipTestCase


@attr('otherwriting')
class OtherWritingTestCase(TestCase):

    @classmethod
    def setUp(cls):
        params = {
            'title': 'Brilliant Op Ed',
            'short_title': 'Brilliant',
            'slug': 'brilliant',
            'type': 'Op Ed',
            'venue': 'Op Ed Aggregator',
            'date': '2018-01-01'
        }
        cls.extra_writing_params = {
            'title': 'Another Brilliant Op Ed',
            'short_title': 'Another Brilliant',
            'slug': 'another-brilliant',
            'venue': 'Op Ed Aggregator',
            'date': '2018-01-02'
        }
        OtherWriting.objects.create(**params)

    def test_otherwriting_str(self):
        w = OtherWriting.objects.get(slug='brilliant')
        self.assertEqual('Brilliant', str(w))

    def test_otherwriting_required_fields(self):
        """Tests that model cannot be saved without required fields."""
        for k in self.extra_writing_params:
            test_dict = self.extra_writing_params.copy()
            test_dict.pop(k)
            try:
                OtherWriting.objects.create(**test_dict)
            except ValidationError as e:
                if k == 'date':
                    self.assertIn('This field cannot be null',
                                  str(e.error_dict[k][0]))
                else:
                    self.assertIn('This field cannot be blank',
                                  str(e.error_dict[k][0]))

    def test_otherwriting_abstract_html(self):
        """Test markdown conversion of abstract field."""
        w = OtherWriting.objects.get(slug='brilliant')
        w.abstract = 'This is **the abstract**'
        w.save()
        self.assertHTMLEqual(
            w.abstract_html,
            '<p>This is <strong>the abstract</strong></p>'
        )

    def test_othwriting_date_order(self):
        """Test reverse date ordering of other writings."""
        w = OtherWriting.objects.get(slug='brilliant')
        w2 = OtherWriting.objects.create(
            **self.extra_writing_params)
        writings = OtherWriting.objects.all()
        for a, b in zip([w2, w], writings):
            self.assertEqual(str(a), str(b))


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


