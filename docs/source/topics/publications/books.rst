.. _topics-pubs-books:

Books
-----

Book Model
^^^^^^^^^^
=======================  ==============================================
Model field reference    :class:`cv.models.publications.Book`
Authorship set           :class:`cv.models.publications.BookAuthorship`
=======================  ==============================================

The :class:`~cv.models.publications.Book` model represents an instance 
of books, including information about different 
:ref:`editions <topics-pubs-book-editions>` of the same book.


Book Views
^^^^^^^^^^

**Book List** : :class:`cv.views.CVListView`
   ===============  ================================================================   
   Context object   ``{{object_list}}``
   Template         ``'cv/lists/book_list.html'``
   URL              ``'books/'``
   MIME type        ``text/html``
   ===============  ================================================================   

   The book list view produces a page with a list of the author's 
   books. This may be useful for profiling an authors' books with, 
   for example, summaries and blurbs. This can be accomplished through
   the use of custom templates. The default template produces a list of
   books using the same section formatting as the listing in the book 
   section of the complete CV. 

   The page renders an instance of the :class:`cv.views.CVListView` view
   with the named parameter ``model_name`` set to ``'book'``. The view
   returns ``{{object_list}}`` in the context with four objects on its 
   dot path: 

   ``total_books``
      Integer of total number of books from all three managers:
   
   ``book_published_list``
      queryset of all published books (uses the :attr:`published()`
      method of the :class:`~cv.models.managers.PublicationManager`)
   
   ``book_revise_list``
      queryset of all books in the revision process (uses the 
      :attr:`revise()` method of the 
      :class:`~cv.models.managers.PublicationManager`)
   
   ``book_inprep_list`` 
      queryset of all books in preparation for submission (uses
      the :attr:`inprep()` method of the 
      :class:`~cv.models.managers.PublicationManager`)

   The URL can be accessed in templates by using the `URL template 
   filter`_ with the named URL ``section_list`` and ``model_name`` 
   parameter equal to ``book``, i.e.::

   {% url section_list model_name='book' %}

.. _URL template filter: https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#url

**Book Detail**: :class:`cv.views.CVDetailView`
   ===============  ==================================================================   
   Context object   ``{{book}}``
   Template         ``'cv/details/book_detail.html'``
   URL              ``'books/<slug:slug>/'``
   MIME type        ``text/html``
   ===============  ==================================================================
   
   The book detail view produces a page that represents a single book. 
   This could be used to, for example, create a feature page for a 
   published book. The default view includes the title, abstract, 
   edition information, and links to download the citation information
   in both RIS and BibTeX formats (described below). The page is 
   rendered as an instance of the :class:`cv.views.CVDetailView` with
   the named parameters ``model_name`` set to ``'book'`` and ``slug``
   set to the book's slug attribute. The view returns the context
   ``{{book}}`` that represents the :class:`Book` instance. 

   The URL can be accessed using the named URL ``item_detail`` with
   ``model_name`` set to ``'book'`` and ``slug`` set to the book's 
   slug attribute, i.e.::

   {% url item_detail model_name='book' slug='slug-from-short-title' %}   


**Book Citation**: :func:`cv.views.citation_view`
   ===============  ================================================================   
   Context object   ``{{book}}``
   Templates        ``'cv/citations/book.ris'``
                    ``'cv/citations/book.bib'``
   URL              ``'books/<slug:slug>/citation/<str:format>/'``
   MIME types       ``application/x-research-info-systems`` or
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


.. _topics-pubs-book-editions:

Book Editions
^^^^^^^^^^^^^

Django-Vitae allows users to link multiple editions of a book with the 
:class:`~cv.models.publications.BookEdition` class. This is done through 
a ForeignKey relationship to the :ref:`book <topics-pubs-books>`. The 
:class:`~cv.models.publications.Book` model includes the 
:meth:`~cv.models.publications.Book.get_editions` method to return all 
editions associated with the book in reverse chronological order 
(i.e., newest first). 

If an edition has been related to a book, the default templates will 
use the publication information (publisher, place of publication, ISBN) 
of the edition instance, not the publication information defined for 
the book instance. 

.. _topics-pubs-book-custom-methods:

Custom Methods
^^^^^^^^^^^^^^

The :class:`~cv.models.publications.Book` class has two custom 
methods related to editions:

   .. method:: add_edition(dict)

      Creates a new :class:`~cv.models.publications.BookEdition` 
      instance with the referencing the :class:`Book` instance 
      on which the user calls the method.

      * ``dict``: a dictionary containing field/value pairs for 
        :class:`~cv.models.publications.BookEdition` fields; 
        ``edition`` must be one of the ``dict`` keys

   .. method:: get_editions()

      Convenience function that returns a 
      :class:`~django.db.models.query.QuerySet` of all the 
      :class:`BookEdition` objects related to the :class:`Book` 
      instance




