# from django.test import TestCase
# import datetime as dt
# 
# from cv.models import Position, Talk, Presentation, Discipline
# 
# # Create your tests here.
# 
# class PositionModelTests(TestCase):
# 	@classmethod
# 	def setUpTestData(cls):
# 		cls.position = Position.objects.create(
# 			display=True,
# 			title="Second Position Name",
# 			start_date= dt.date(2015,12, 1),
# 			end_date = dt.date(2015,12, 2),
# 			project = "Project name",
# 			institution = "Beta Univ.",
# 			current_position = True,
# 			primary_position = True
# 		)
# 		cls.position.save()
# 		cls.position2 = Position.objects.create(
# 			display=False,
# 			title="First Position Name",
# 			start_date= dt.date(2014,12, 1),
# 			end_date = dt.date(2014,12, 2),
# 			project = "Project name",
# 			institution = "Alpha Univ.",
# 			current_position = False,
# 			primary_position = False
# 		)
# 		cls.position2.save()
# 		
# 	def test_primary_position_manager(self):
# 		primaries = Position.primarypositions.all()
# 		self.assertEqual(len(primaries),1)
# 		self.assertEqual(str(primaries[0]),"Second Position Name")
# 	
# 	def test_displayable(self):
# 		displayable = Position.displayable.all()
# 		self.assertEqual(len(displayable),1)
# 		
# 	def test_default_manager(self):
# 		objects = Position.objects.all()
# 		self.assertEqual(len(objects),2)
# 
# 
# class TalkModelTests(TestCase):
# 	@classmethod
# 	def setUpTestData(cls):
# 		cls.discipline = Discipline.objects.create(name = 'Life', slug = 'life')
# 		cls.discipline.save()
# 		cls.talk = Talk.objects.create(
# 			title = "Talk about something important"
# 			, short_title = "Important talk "
# 			, slug = "important-talk"
# 			, primary_discipline = cls.discipline
# 			, abstract = "*abstract*"
# 			)
# 		cls.talk.save()
# 
# 	def test_abstract_html(self):
# 		"""Test that abstract_html saves Markdown version of abstract."""
# 		talk = Talk.objects.all()[0]
# 		self.assertEqual(talk.abstract_html,'<p><em>abstract</em></p>')
# 		
# 	def test_save_first_presentation(self):
# 		"""
# 		Test that the first presentation for a talk gets saved in 				
# 		``talk.latest_presentation_date`` 
# 		
# 		"""
# 		vals = {'talk': self.talk, 'presentation_date':"2011-01-01"
# 				,'event':"Important event", 'type':10}
# 		presentation = Presentation(**vals)		
# 		presentation.save()
# 		presentation = Presentation.objects.all()[0]
# 		talk = Talk.objects.all()[0]
# 		self.assertEqual(presentation.presentation_date, talk.latest_presentation_date)
# 	
# 	def test_save_subsequent_presentation(self):
# 		"""Test that second presentation after the first replaces ``talk.latest_presentation_date``"""
# 		first_vals = {'talk': self.talk, 'presentation_date':dt.date(2015,1,1)
# 				,'event':"Important event", 'type':10}
# 		second_vals = {'talk': self.talk, 'presentation_date':dt.date(2016,1,1)
# 				,'event':"Second important event", 'type':10}
# 		presentation_list = [Presentation(**vals).save() for vals in [first_vals,second_vals]]
# 		presentations = Presentation.objects.all()
# 		self.assertEqual(presentations[0].presentation_date,second_vals['presentation_date'])
# 		self.assertEqual(self.talk.latest_presentation_date,second_vals['presentation_date'])
# 
# 	def test_save_previous_presentation(self):
# 		"""Test that second presentation before the first does not replace ``talk.latest_presentation_date``"""
# 		first_vals = {'talk': self.talk, 'presentation_date':dt.date(2013,1,1)
# 				,'event':"Important event", 'type':10}
# 		first_presentation = Presentation(**first_vals).save()
# 		self.assertEqual(self.talk.latest_presentation_date,first_vals['presentation_date'])
# 		second_vals = {'talk': self.talk, 'presentation_date':dt.date(2012,1,1)
# 				,'event':"Second important event", 'type':10}
# 		second_presentation = Presentation(**second_vals).save()
# 		self.assertNotEqual(self.talk.latest_presentation_date,second_vals['presentation_date'])
# 	
# 		