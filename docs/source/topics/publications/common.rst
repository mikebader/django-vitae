.. _topics-pubs-common-features:

Common Features
===============

Publications, regardless of type, all have some common traits such as titles and lists of 
authors. Django-Vitae defines a number of common features across the four different types of 
publications. Internally, Django-Vitae does this by defining a series of abstract classes. 
The different publication models inherit from the 
:class:`~cv.models.VitaePublicationModel` abstract model. 

.. _topics-pubs-common-fields:

Common Fields
-------------

The following fields are common across the four types of publications: 

:attr:`title`
   The title of the publication (**required**).

:attr:`short_title`
	A shortened title of the publication with a maximum length of 80 characters 
	(**required**). 
	
	This can be the "running head" of a publication. Django-Vitae uses the slugified version 
	of the short title to construct URLs for the item. 
	
:attr:`slug`
	A slugified version of the short-title to use in URLs (**required**).
	
	The slugs are automatically constructed from the :attr:`short_title` in 
	:class:`~cv.admin`.

.. _topics-pubs-status-table:

:attr:`status`
	The point in the publication process where the publication currently rests 
	(**required**).

	All publication models include an :attr:`status` field, which represents the where in 
	publication process the publication currently exists. Django-Vitae implements the 
	:attr:`status` field by using an :class:`~django:django.db.models.IntegerField` with 
	the :attr:`choices` parameter defined in :mod:`cv.constants.PUBLICATION_STATUS`:

	==========  ====================================
	Integer		Status
	==========  ====================================
	0			In preparation
	1			Working paper
	20			Submitted
	30			Revision for resubmission invited
	35			Resubmitted
	40			Conditionally accepted
	50			Forthcoming
	55			In press
	60			Published
	99			"Resting"
	==========  ====================================	

:attr:`pub_date`
    The date that the publication was published in final form.

:attr:`primary_discipline`
	The discipline to which the publication contributes most directly. 
	
	A :class:`~django:django.db.models.ForeignKey` relationship to a 
	:class:`cv.models.Discipline` object. Can be useful for researchers who work in 
	multiple disciplines to separate their CV into sections for each discipline. 

:attr:`other_disciplines`
	Disciplines other than the primary discipline to which the publication contributes.
	
	A :class:`~django:django.db.models.ManyToManyField` relationship to  
	:class:`cv.models.Discipline` objects. 


.. _topics-pubs-ordering: 

Ordering
--------

The publication models order model instances by :attr:`status` in ascending order then by 
:attr:`pub_date` in descending order. This places the publications with the highest 
probability of changing at the top of sorted lists. 

.. note::
    The publication models do not use :attr:`pub_date` field to identify published 
    articles and the built-in templates do not print the :attr:`pub_date` field. 
    Therefore, users can use the :attr:`pub_date` field to order unpublished manuscripts 
    in a convenient order. 


.. _topics-pubs-common-managers:

Managers
--------

For all types of publications, users may access instances of publication models using four 
custom managers (in addition to the default manager using :attr:`objects`) that will 
return all objects: 

:attr:`displayable` : default 
	uses :class:`cv.models.DisplayableManager` that returns only articles for which 
	``display==True``.

.. _topics-pubs-published-manager:

:attr:`published`
	uses :class:`cv.models.PublishedManager` that returns all articles that have been 
	accepted for publication or published (forthcoming, in press, and published).

.. _topics-pubs-inprep-manager:

:attr:`inprep` 
	uses :class:`cv.models.InprepManager` that returns all articles being prepared for 
	publication.

.. _topics-pubs-revise-manager:

:attr:`revise`
	uses :class:`cv.models.ReviseManager` that returns all articles that are 
	in the process of submission or revision (submitted, under revision for
	resubmission, resubmitted, or conditionally accepted).

The custom managers the include multiple statuses retain the default ordering of the 
model (that is, they are ordered by :attr:`status`, then :attr:`pub_date`, then
:attr:`submission_date`). 

.. _topics-pubs-collaboration-sets:

Authorship Sets
---------------

Publication types also share the common trait of having authors. More 
precisely, publications have *authorships* since a list of authors 
contains information, such as the order of authorship. 

For all publication type models, Django-Vitae includes an :attr:`authorship` 
attribute that returns a :class:`~django.db.models.query.QuerySet` of 
authorships, e.g.::

   >>> from cv.models import Article
   >>> article = Article.objects.all().first()
   >>> article.authorship.all()
   <QuerySet [<ArticleAuthorship: Kahneman, Daniel>, 
      <ArticleAuthorship: Tversky, Amos]>]

Internally, the authorship attributes are implemented as a 
:class:`django.db.models.ManyToManyField`s that relate an instance of the 
publication type (e.g., :class:`Article`, :class:`Book`, etc.) to 
:class:`Collaborator` through a third model. 

Authorship models for all publication types have three common fields: 

:attr:`display_order`
	Integer that classifies the position of the author in the list of authors 
	(**required**)

:attr:`print_middle`
	Boolean that indicates whether the author's middle initials should be printed in list 
	of authors (default=True)

:attr:`student_colleague`
   Choice field with possible values defined by :ref:`cv-student-levels-choices` 
   setting; allows display of student collaborations
