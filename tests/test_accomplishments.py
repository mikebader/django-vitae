from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from nose.plugins.attrib import attr
# from unittest import TestCase

from cv.models import Award, Degree, Position


@attr('accomplishments')
class AccomplishmentsTestCase(TestCase):

    # Awards
    def test_award(self):
        """Test creation, string representation, and url of award."""
        award = Award.objects.create(
            name='award', organization='important place', date='2000-01-01')
        self.assertEqual(str(award), 'award')
        self.assertEqual(award.get_absolute_url(), '/#award-1')

    def test_award_displayable(self):
        """Test that only displayable awards are in displayable manager."""
        Award.objects.create(
            name='award', organization='important place', date='2000-01-01',
            display=False)
        self.assertEqual(len(Award.displayable.all()), 0)

    # Degrees
    def test_degree(self):
        """Test creation, string representation, and url of degrees."""
        degree = Degree.objects.create(
            degree='B.A.', date_earned='2000-01-01',
            institution='college', city='anywhere', state='state')
        self.assertEqual(str(degree), 'B.A.')
        self.assertEqual(degree.get_absolute_url(), "/#degree-1")

    def test_degree_displayable(self):
        """Test that only dispayable degrees are in displayable manager."""
        Degree.objects.create(
            degree='B.A.', date_earned='2000-01-01',
            institution='college', city='anywhere', state='state',
            display=False)
        self.assertEqual(len(Degree.displayable.all()), 0)

    def test_degree_ordering(self):
        """Test reverse chronological ordering of degrees."""
        Degree.objects.create(
            degree='B.A.', date_earned='2000-01-01',
            institution='college', city='anywhere', state='state')
        Degree.objects.create(
            degree='M.A.', date_earned='2001-01-01',
            institution='college', city='anywhere', state='state')
        degrees = [str(degree) for degree in Degree.displayable.all()]
        self.assertEqual(degrees, ['M.A.', 'B.A.'])
        self.assertEqual(str(Degree.displayable.all().latest()), 'M.A.')

    # Positions
    def test_position(self):
        """Test creation, string representation, and url of positions."""
        position = Position.objects.create(
            title='Fancy title', institution='Fancy Institution',
            start_date='2002-01-01')
        self.assertEqual(str(position), 'Fancy title')
        self.assertEqual(position.get_absolute_url(), "/#position-1")

    def test_position_dates(self):
        """Positions require start date & end date must be after start date."""
        position_fields = {'title': 'Fancy Title', 'institution': 'Institute'}
        try:
            Position.objects.create(**position_fields)
        except ValidationError as e:
            self.assertTrue('start_date' in e.error_dict.keys())
            self.assertIn('This field cannot be null',
                          str(e.error_dict['start_date'][0]))
        position_fields.update({'end_date': '2000-01-01',
                                'start_date': '2010-01-01'})
        with self.assertRaises(ValidationError) as err:
            Position.objects.create(**position_fields)
        e = err.exception
        self.assertTrue('end_date' in e.error_dict.keys())
        self.assertIn('End date cannot be before start date',
                      str(e.error_dict['end_date']))

    def test_primary_position(self):
        """Primary position manager should only return primary positions."""
        Position.objects.create(
            title='Fancy title', institution='Fancy Institution',
            start_date='2002-01-01', primary_position=True)
        primary_positions = Position.primary_positions.all()
        self.assertEqual(len(primary_positions), 1)
        Position.objects.create(
            title='Fancier title', institution='Fancier Institution',
            start_date='2003-01-01')
        primary_positions = Position.primary_positions.all()
        self.assertEqual(len(primary_positions), 1)


    def test_position_ordering(self):
        """Positions should be reverse chronologically ordered."""
        Position.objects.create(
            title='Fancy title', institution='Fancy Institution',
            start_date='2002-01-01', end_date='2002-12-31')
        Position.objects.create(
            title='Fancier title', institution='Fancier Institution',
            start_date='2003-01-01', end_date='2004-01-01')
        positions = [str(position) for position in Position.objects.all()]
        self.assertEqual(['Fancier title', 'Fancy title'], positions)
        self.assertEqual('Fancier title', str(Position.objects.all().latest()))





