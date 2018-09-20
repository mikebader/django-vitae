from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline

from .models import Collaborator, CVFile, Journal, Discipline, Award, \
					Position, Degree, \
					Grant, GrantCollaboration, \
					Article, ArticleAuthorship, \
					Chapter, ChapterAuthorship, ChapterEditorship, \
					Book, BookAuthorship, BookEdition, \
					Report, ReportAuthorship, \
					Talk, Presentation, OtherWriting, \
					MediaMention, Service, JournalService, Student, \
					Course, CourseOffering 

## Uncomment the following two lines if you would like to use the `researchprojects` app
## to link lines in CV to research projects
# from researchprojects.models import ResearchProjectItem
# project_admin_inlines = ['GrantAdmin','ArticleAdmin','ChapterAdmin','BookAdmin','TalkAdmin','MediaMentionAdmin']


# Admin class models for `cv`
class CVFileInline(GenericTabularInline):
	model = CVFile
	extra = 1
	
class DisciplineAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ['name']}
	
class CollaboratorAdmin(admin.ModelAdmin):
	fieldsets = (
		('Name', {'fields':(('first_name','middle_initial','last_name','suffix'),)}),
		('Information', {'fields': ('institution','website',('email','alternate_email'))})
		)
	list_display = ('last_name','first_name','email')
	list_display_links = ('last_name','first_name','email')
	
class JournalAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields':(('title'),('issn','abbreviated_title'),('primary_discipline'))}),
		(None, {'fields':('website','other_disciplines'),'classes':('collapse',)})
		)
	list_display = ('title','issn')
	list_display_links = ('title','issn')
	list_filter = ('primary_discipline',)
	filter_horizontal = ['other_disciplines']

class AwardAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Award`` model of ``cv``."""
	
	fieldsets=(
		(None,{'fields':('name','organization','date')}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	list_display = ('name','organization','date')
	date_hierarchy = 'date'

class DegreeAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Degree`` model of ``cv``."""
	
	fieldsets = (
		(None, {'fields':(
			('degree','date_earned','display'),
			('major','honors'),
			('institution',),('city','state','country')
			)}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	list_display = ('degree','date_earned')

class PositionAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Position`` model of ``cv``."""
	
	fieldsets = (
		('Position description', 
			{'fields':(('title','department','institution','project'),)}),
		(None, {'fields':(('start_date','end_date'),('current_position','primary_position'))})			
		)
	list_display = ('title','institution','start_date','end_date','display')
	list_display_links = ('title','institution')
	list_editable = ('display',)
	date_hierarchy = 'start_date'

class GrantCollaborationInline(admin.TabularInline):
	model = GrantCollaboration
	extra = 3

class GrantAdmin(admin.ModelAdmin):
	
	fieldsets = (
		(None, {'fields':(('title','display'),'short_title','slug')}),
		('Funder', {'fields':('source',('agency','agency_acronym'),('division','division_acronym'))}),
		('Grant information',
			{'fields':(('grant_number','amount'),('start_date','end_date'),'abstract')}),
		('Disciplines', {'fields':('primary_discipline','other_disciplines')}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title','source','agency','start_date','end_date')
	list_editable = ('start_date','end_date','source')
	date_hierarchy = 'start_date'
	list_filter = ('source','agency','primary_discipline')
	filter_horizontal = ['other_disciplines']
	
	inlines = [GrantCollaborationInline, CVFileInline]
	
class ArticleAuthorshipInline(admin.TabularInline):
	model = ArticleAuthorship
	extra = 5

class ArticleAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Article`` model of ``cv``."""
	
	fieldsets = (
		(None, {'fields':(
			('title','status','display'),('submission_date','pub_date'),'short_title','slug'
			)}),
		('Abstract', {'fields':('abstract',)}),
		('Publication Info', {'fields':(
			('journal','volume','issue','start_page','end_page'),('url',),('series','number'),('doi','pmcid','pmid')
			)}),
		('Grant information', {'fields':('grants',)}),
		('Disciplines', {'fields':('primary_discipline','other_disciplines')}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title','status','submission_date','pub_date','journal')
	list_editable = ('status','submission_date','pub_date')
	date_hierarchy = 'pub_date'
	list_filter = ('status','primary_discipline')
	filter_horizontal = ['other_disciplines']
	
	inlines = [ArticleAuthorshipInline, CVFileInline]

class ChapterAuthorshipInline(admin.TabularInline):
	model = ChapterAuthorship
	extra = 5 

class ChapterEditorshipInline(admin.TabularInline):
	model = ChapterEditorship
	extra = 2 

class ChapterAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Chapter`` model of ``cv``."""
	
	fieldsets = (
		(None, {'fields':(
			('title','status','display'), 
			('pub_date',),('short_title',),('slug',))}),
		('Abstract', {'fields':('abstract',)}),
		('Book information', {'fields':(
			('book_title','isbn','url'),
			('start_page','end_page'),
			('publisher','place','edition'),
			('volume','volumes','series','series_number'))}),
		('Grant information', {'fields':('grants',)}),
		('Disciplines', {'fields':('primary_discipline','other_disciplines')}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title','status','book_title')
	list_editable = ('status',)
	date_hierarchy = 'pub_date'
	list_filter = ('status','primary_discipline')
	filter_horizontal = ['other_disciplines','grants']
	
	inlines = [ChapterAuthorshipInline, ChapterEditorshipInline, CVFileInline]

class BookAuthorshipInline(admin.TabularInline):
	model = BookAuthorship
	extra = 1

class BookEditionInline(admin.TabularInline):
	model = BookEdition
	extra = 1

class BookAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Artilce`` model of ``cv``."""
	
	fieldsets = (
		(None, {'fields':(
			('title','display','status','pub_date'),('short_title','slug')
			)}),
		('Summary', {'fields':('summary','url')}),
		('Publisher Information', {'fields':(
			('publisher','place'),('volume','num_pages'),
			('isbn'),('series','series_number')
			)}),
		('Grant information', {'fields':('grants',)}),
		('Disciplines', {
			'fields':('primary_discipline','other_disciplines'),
			'classes':('collapse',)
			}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title','status','pub_date')
	list_editable = ('status',)
	date_hierarchy = 'pub_date'
	filter_horizontal = ['other_disciplines']
	
	inlines = [BookAuthorshipInline, BookEditionInline, CVFileInline]

class ReportAuthorshipInline(admin.TabularInline):
	model = ReportAuthorship
	extra = 5

class ReportAdmin(admin.ModelAdmin):
	
	"""Make administration interface for ``Report`` model of ``cv``."""
	
	fieldsets = (
		(None, {'fields': (
			('title','status','display'),('pub_date'),'short_title','slug'
			)}),
		('Abstract', {'fields': ('abstract',)}),
		('Report Information', {'fields':(
			('report_number','report_type'),('institution','place'),'pages','url','doi'
			)}),
		('Grant information', {'fields':('grants',)}),
		('Disciplines', {'fields':('primary_discipline','other_disciplines')}),
		('Extra Information', {'fields':('extra',),'classes':('collapse',)})		
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title','status','report_type')
	list_editable = ('status',)
	date_hierarchy = 'pub_date'
	list_filter = ('status','primary_discipline')
	filter_horizontal = ['other_disciplines']
	
	inlines = [ReportAuthorshipInline, CVFileInline]

class PresentationInline(admin.TabularInline):
	model = Presentation
	extra = 2

class TalkAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields':(('title','display'),('short_title','slug'))}),
		('Abstract', {'fields':('abstract',)}),
		('Collaborators',{'fields':('collaborator',)}),
		('Related CV Items', {'fields':('grants','article_from_talk')}),
		('Disciplines', {
			'fields':('primary_discipline','other_disciplines'),
			'classes':('collapse',)
			}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)
	prepopulated_fields = {'slug':['short_title']}
	list_display = ('title',)
	date_hierarchy = 'latest_presentation_date'
	inlines = [PresentationInline, CVFileInline]
	filter_horizontal = ['collaborator']

class PresentationAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields':(('presentation_date','type'))}),
		(None, {'fields':(('event','event_acronym'))}),
		(None, {'fields':(('city','state','country'))})
		)

class MediaMentionAdmin(admin.ModelAdmin):
	fieldsets = (
		('Media mention information', {'fields':(('title','date','url'),)}),
		('Media outlet information',{'fields':(('outlet','section','author'),)}),
		('Content of mention', {'fields':('description','snapshot')}),
		('Relevant product', {'fields':('article','book','talk')})
		)

class OtherWritingAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields':(('title','display','type'),'slug','date','venue')}),
		('Publication Information', {'fields':(
			('pages','url','place'),('volume','issue'))}),
		('Abstract',{'fields':('abstract',)}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)
	prepopulated_fields = {'slug':['title']}
	list_display = ('type','title','date','venue')
	list_filter = ['type']
	date_hierarchy = 'date'	
	
class ServiceAdmin(admin.ModelAdmin):
	fieldsets = (
		('Basic Information',{'fields':(('role','type','display'),('group',),('organization',))}),
		('Dates',{'fields':(('start_date','end_date'),)}),
		('Description', {'fields':('description',)}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)
	list_display = ('organization','role','type','start_date','end_date')
	date_hierarchy = 'end_date'
	list_filter = ('type','organization')
	list_editable = ('start_date','end_date')

class JournalServiceAdmin(admin.ModelAdmin): 
	fieldsets = (
		('Basic Information',{'fields':('journal','is_reviewer')}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)

class StudentAdmin(admin.ModelAdmin):
	fieldsets = (
		('Student information', {'fields':(
			('first_name','middle_name','last_name'),
			('display','student_level'))}),
		('Advising information', {'fields': (
			('role','thesis_title'),
			('graduation_date','is_current_student'),
			'first_position', 'current_position')}),
		('Extra information',{'fields':('extra',),'classes':('collapse',)})
		)
	list_display = ('last_name','first_name','graduation_date','is_current_student')
	list_editable = ('graduation_date','is_current_student')
	date_hierarchy = 'graduation_date'
	list_filter = ('student_level','is_current_student')


class CourseOfferingInline(admin.TabularInline):
	model = CourseOffering
	extra = 2


class CourseAdmin(admin.ModelAdmin):
	fieldsets = (
		('Course Information', {'fields':(
			'title', 'slug', 'student_level')}),
		('Description', {'fields':(
			('short_description'),
			('full_description'))})
		)
	list_display = ('title', 'student_level')
	list_filter = ('student_level',)
	inlines = [CourseOfferingInline]

def register_hidden_models(*model_names):
	"""Hide models from list of models on CV admin but allow models to be edited using 
	plus symbol on related models."""
	## Copied from murraybiscuit's answer on StackOverflow: 
	## https://stackoverflow.com/a/41193766
	for m in model_names:
		ma = type(
			str(m)+'Admin',
			(admin.ModelAdmin,),
			{
				'get_model_perms': lambda self, request: {}
			})
		admin.site.register(m, ma)


## The following lines detect whether ResearchProjectInline is imported then adds a
## tabular inline to the admin defined in the `project_admin_inlines` above
try:
	class ResearchProjectItemInline(GenericTabularInline):
		model=ResearchProjectItem
		extra=1
	def researchprojects_installed():
		return True
except NameError:
	def researchprojects_installed():
		return False	

if researchprojects_installed():
	import importlib
	for admin_type in project_admin_inlines:
		c = getattr(importlib.import_module('cv.admin'),admin_type)
		c.inlines+=[ResearchProjectItemInline]

register_hidden_models(Journal,Discipline)

admin.site.register(Collaborator,CollaboratorAdmin)	
admin.site.register(Award,AwardAdmin)
admin.site.register(Degree,DegreeAdmin)
admin.site.register(Position,PositionAdmin)
admin.site.register(Grant,GrantAdmin)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Chapter,ChapterAdmin)
admin.site.register(Book,BookAdmin)
admin.site.register(Report,ReportAdmin)
admin.site.register(Talk,TalkAdmin)
admin.site.register(OtherWriting,OtherWritingAdmin)
admin.site.register(Presentation,PresentationAdmin)
admin.site.register(MediaMention,MediaMentionAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(JournalService,JournalServiceAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Course, CourseAdmin)
