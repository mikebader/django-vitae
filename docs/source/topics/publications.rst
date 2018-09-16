Publications
============

Publications are the central component of Django-CV since publications are the key 
element of CVs. Django-CV includes four types of publications: :ref:`books 
<topics-pubs-books>`, :ref:`articles <topics-pubs-articles>`, :ref:`chapters 
<topics-pubs-chapters>`, and :ref:`reports <topics-pubs-reports>`. 

.. _topics-pubs-common-features:

Common Features
---------------

Publications, regardless of type, all have some common traits such as titles and lists of 
authors. Django-CV defines a number of common features across the four different types of 
publications. Internally, Django-CV does this by defining a series of abstract classes. 
The different publication models inherit from the 
:class:`~cv.models.VitaePublicationModel` abstract model. 

.. _topics-pubs-common-fields:

Common Fields
^^^^^^^^^^^^^

The following fields are common across the four types of publications: 

:attr:`title`
   The title of the publication (**required**).

:attr:`short_title`
	A shortened title of the publication with a maximum length of 80 characters 
	(**required**). 
	
	This can be the "running head" of a publication. Django-CV uses the slugified version 
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
	publication process the publication currently exists. Django-CV implements the 
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
^^^^^^^^

The publication models order model instances by :attr:`status` in ascending order then by 
:attr:`pub_date` in descending order. This places the publications with the highest 
probability of changing at the top of sorted lists. 

.. note::
    The publication models do not use :attr:`pub_date` field to identify published 
    articles and the built-in templates do not print the :attr:`pub_date` field. 
    Therefore, users can use the :attr:`pub_date` field to order unpublished manuscripts 
    in a convenient order. 


.. _topics-pubs-common-managers:

Common Managers
^^^^^^^^^^^^^^^

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
precisely, publications have _authorships_ since a list of authors 
contains information, such as the order of authorship. 

For all publication type models, Django-CV includes an :attr:`authorship` 
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


.. _topics-pubs-types:

Types of Publications
---------------------
 

.. _topics-pubs-articles:

Articles
^^^^^^^^
=======================                         ========================================
Model field reference                           :class:`cv.models.Article`
Authorship set                                  :class:`cv.models.ArticleAuthorship`
=======================                         ========================================


The :class:`Article` model contains two non-editable fields managed internally that can be 
accessed for article instances: 

* :attr:`abstract_html` that converts text entered in Markdown in :attr:`abstract` field 
   to html, and 

* :attr:`is_published` that indicates whether :attr:`status` field is one of 
   "Forthcoming," "In Press," or "Published".   

The functions :func:`get_previous_published` and :func:`get_next_published` will get the 
next and previous *published* articles based on the :attr:`pub_date` field. 


.. _topics-pubs-articles-views:

Article Views
"""""""""""""

**Article List** : :class:`cv.views.ArticleListView`
   ===============  ================================================================   
   Context object   ``{{article_objects}}``
   Template         ``'cv/lists/article_list.html'``
   URL              ``r'^articles/$'``
   URL name			  ``'article_object_list'``
   MIME type        ``text/html``
   ===============  ================================================================   
	
   Returns context ``{{article_objects}}`` with four objects on the dot path:

   ``total_articles``
      Integer of total number of article objects from all three status-based managers:

   ``article_published_list``
      queryset of all published articles (uses the `published manager 
      <topics-pubs-published-manager>`)
   
   ``article_revise_list``
      queryset of all articles in the revision process (uses the `revise manager 
      <topics-pubs-revise-manager>`)
   
   ``article_inprep_list`` 
      queryset of all articles in preparation for submission (uses the `inprep manager 
      <topics-pubs-published-manager>`)

**Article Detail**: :class:`cv.views.ArticleDetailView`
   ===============  ================================================================   
   Context object   ``{{article}}``
   Template         ``'cv/details/article_detail.html'``
   URL              ``'articles/<slug:slug>/``
   URL name			  ``'article_object_detail'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   Returns context ``{{article}}`` that represents a single :class:`Article` instance.

**Article Citation**: :func:`cv.views.article_citation_view`
   ===============  ================================================================   
   Context object   ``{{article}}``
   Templates        ``'cv/citations/article.ris'``
                    ``'cv/citations/article.bib'``
   URL              ``'articles/<slug:slug>/citation/<str:format>/'``
   URL name			  ``'article_citation'``
   MIME type        ``application/x-research-info-systems``
   ===============  ================================================================
   
   Returns view to allow citation to be downloaded to citation management software.
   
   The :attr:`(?P<format>[\w]+)` named parameter should be one of:
   
   ``'ris'``
      will create downloadable citation using Reference Manager format specification (see 
      http://endnote.com/sites/rm/files/m/direct_export_ris.pdf).
    
   ``'bib'``
      will create downloadable citation using the BibTeX format specification (see
      http://www.bibtex.org/Format/)


.. _topics-pubs-books:

Books
^^^^^

The :class:`~cv.models.Book` class stores instances of books. The :attr:`summary` field
takes Markdown_ input and saves the converted HTML to the non-editable 
:attr:`summary_html` field. 

.. _Markdown: https://daringfireball.net/projects/markdown/syntax

The :class:`Book` model can store information about different editions of 
book instances. 

=======================                         ========================================
Model field reference                           :class:`cv.models.Book`
Authorship set                                  :class:`cv.models.BookAuthorship`
=======================                         ========================================

Custom Methods
""""""""""""""

The :class:`~cv.models.Book` class has two custom methods related to 
`Book Editions`_:

   .. method:: add_edition(dict)

      Creates a new :class:`~cv.models.BookEdition` instance with the 
      referencing the :class:`Book` instance on which the user calls the method.

      * ``dict``: a dictionary containing field/value pairs for 
        :class:`~cv.models.BookEdition` fields; ``edition`` must be one of the 
        ``dict`` keys



   .. method:: get_editions()

      Convenience function to a :class:`~django.db.models.query.QuerySet` of all 
      the :class:`BookEdition` objects related to the :class:`Book` instance


Book Views
""""""""""

**Book List** : :class:`cv.views.BookListView`

   ===============  ================================================================   
   Context object   ``{{book_objects}}``
   Template         ``'cv/lists/book_list.html'``
   URL              ``'books/'``
   URL name			  ``'book_object_list'``
   MIME type        ``text/html``
   ===============  ================================================================   

   Returns context ``{{book_objects}}`` with four objects on the dot path: 

   ``total_books``
      Integer of total number of books from all three managers:
   ``books_published_list``
      :class:`~django.db.models.query.QuerySet` of all published books (uses the 
      `published manager <topics-pubs-published-manager>`)
   
   ``books_revise_list``
      queryset of all books in the revision process (uses the `revise manager 
      <topics-pubs-revise-manager>`)
   
   ``books_inprep_list`` 
      queryset of all books in preparation for submission (uses the `inprep manager 
      <topics-pubs-published-manager>`)

**Book Detail**: :class:`cv.views.BookDetailView`

   ===============  ================================================================   
   Context object   ``{{book}}``
   Template         ``'cv/details/book_detail.html'``
   URL              ``'books/<slug:slug>/'``
   URL name			  ``'book_object_detail'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   Returns context ``{{book}}`` that represents a single 
   :class:`~cv.models.Book` instance.

**Book Citation**: :func:`cv.views.book_citation_view`

   ===============  ================================================================   
   Context object   ``{{book}}``
   Templates        ``'cv/citations/book.ris'``
                    ``'cv/citations/book.bib'``
   URL              ``'books/<slug:slug>/citation/<str:format>/'``
   URL name			  ``'book_citation'``
   MIME types       ``application/x-research-info-systems``
                    ``application/x-bibtex``
   ===============  ================================================================
   
   Returns view to allow citation to be downloaded to citation management software.
   
   The :attr:`<str:format>` named parameter should be one of:
   
   ``'ris'``
      will create downloadable citation using Reference Manager format specification (see 
      http://endnote.com/sites/rm/files/m/direct_export_ris.pdf).
    
   ``'bib'``
      will create downloadable citation using the BibTeX format specification (see
      http://www.bibtex.org/Format/)


.. _pub-overview-book-editions:

Book Editions
"""""""""""""


Django-CV allows users to link multiple editions of a book with the 
:class:`~cv.models.BookEdition` class. This is done through a ForeignKey relationship to 
the :ref:`book <topics-pubs-books>`. The :class:`~cv.models.Book` model includes the 
:meth:`~cv.models.Book.get_editions` method to return all editions associated with the 
book in reverse chronological order (i.e., newest first). 

If an edition has been related to a book, the default templates will use the publication
information (publisher, place of publication, ISBN) of the edition instance, not the 
publication information defined for the book instance. 


.. _topics-pubs-chapters:

Chapters
^^^^^^^^

The :class:`~cv.models.Chapter` class stores instances of chapters. 

Like Articles_, the :attr:`abstract` field takes Markdown_ input and saves 
the converted HTML to the (non-editable) :attr:`summary_html` field. 

In addition to the :attr:`authorship` attribute that saves authorship 
information, the :class:`Chapter` class also has an :attr:`editorship` 
attribute that contains information about editors of the volume in which the 
chapter appears. Like the :attr:`authorship` attribute, the 
:attr:`editorship` returns a foreign key 
:class:`~django.db.models.fields.related.RelatedManager` (read more about 
`related managers`_). 

.. _Markdown: https://daringfireball.net/projects/markdown/syntax
.. _related managers: https://docs.djangoproject.com/en/2.0/ref/models/relations/#django.db.models.fields.related.RelatedManager

=======================                         ========================================
Model field reference                           :class:`cv.models.Chapter`
Authorship set                                  :class:`cv.models.ChapterAuthorship`
=======================                         ========================================

**Chapter List** : :class:`cv.views.ChapterListView`

   ===============  ================================================================   
   Context object   ``{{chapter_objects}}``
   Template         ``'cv/lists/chapter_list.html'``
   URL              ``'chapters/'``
   URL name         ``'chapter_object_list'``
   MIME type        ``text/html``
   ===============  ================================================================   

   Returns context ``{{chapter_objects}}`` with four objects on the dot path: 

   ``total_chapters``
      Integer of total number of chapters from all three managers:
   
   ``chapters_published_list``
      :class:`~django.db.models.query.QuerySet` of all published chapters (uses the 
      `published manager <topics-pubs-published-manager>`)
   
   ``chapters_revise_list``
      :class:`~django.db.models.query.QuerySet` of all chapters in the 
      revision process (uses the `revise manager <topics-pubs-revise-manager>`)
   
   ``chapters_inprep_list`` 
      :class:`~django.db.models.query.QuerySet` of all chapters in 
      preparation for submission (uses the `inprep manager 
      <topics-pubs-published-manager>`)

**Chapter Detail**: :class:`cv.views.ChapterDetailView`
   ===============  ================================================================   
   Context object   ``{{chapter}}``
   Template         ``'cv/details/chapter_detail.html'``
   URL              ``'chapters/<slug:slug>/'``
   URL name         ``'chapter_object_detail'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   Returns context ``{{chapter}}`` that represents a single 
   :class:`~cv.models.Chapter` instance.

**Chapter Citation**: :func:`cv.views.book_citation_view`
   ===============  ================================================================   
   Context object   ``{{chapter}}``
   Templates        ``'cv/citations/chapter.ris'``
                    ``'cv/citations/chapter.bib'``
   URL              ``'chapter/<slug:slug>/citation/<str:format>/'``
   URL name         ``'chapter_citation'``
   MIME types       ``application/x-research-info-systems``
                    ``application/x-bibtex``
   ===============  ================================================================
   
   Returns view to allow citation to be downloaded to citation management software.
   
   The :attr:`<str:format>` named parameter should be one of:
   
   ``'ris'``
      will create downloadable citation using Reference Manager format specification (see 
      http://endnote.com/sites/rm/files/m/direct_export_ris.pdf).
    
   ``'bib'``
      will create downloadable citation using the BibTeX format specification (see
      http://www.bibtex.org/Format/)


.. _topics-pubs-reports:

Reports
^^^^^^^




