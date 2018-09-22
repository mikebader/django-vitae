.. _topics-pubs-books:

Books
^^^^^

Book Model
""""""""""

The :class:`~cv.models.publications.Book` class stores instances of books. The :attr:`summary` field
takes Markdown_ input and saves the converted HTML to the non-editable 
:attr:`summary_html` field. 

.. _Markdown: https://daringfireball.net/projects/markdown/syntax

The :class:`Book` model can store information about different editions of 
book instances. 

=======================                         ========================================
Model field reference                           :class:`cv.models.publications.Book`
Authorship set                                  :class:`cv.models.publications.BookAuthorship`
=======================                         ========================================

Custom Methods
""""""""""""""

The :class:`~cv.models.publications.Book` class has two custom methods related to 
`Book Editions`_:

   .. method:: add_edition(dict)

      Creates a new :class:`~cv.models.publications.BookEdition` instance with the 
      referencing the :class:`Book` instance on which the user calls the method.

      * ``dict``: a dictionary containing field/value pairs for 
        :class:`~cv.models.publications.BookEdition` fields; ``edition`` must be one of the 
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
   ``book_published_list``
      :class:`~django.db.models.query.QuerySet` of all published books (uses the 
      `published manager <topics-pubs-published-manager>`)
   
   ``book_revise_list``
      queryset of all books in the revision process (uses the `revise manager 
      <topics-pubs-revise-manager>`)
   
   ``book_inprep_list`` 
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
   :class:`~cv.models.publications.Book` instance.

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


Django-Vitae allows users to link multiple editions of a book with the 
:class:`~cv.models.publications.BookEdition` class. This is done through a ForeignKey relationship to 
the :ref:`book <topics-pubs-books>`. The :class:`~cv.models.publications.Book` model includes the 
:meth:`~cv.models.publications.Book.get_editions` method to return all editions associated with the 
book in reverse chronological order (i.e., newest first). 

If an edition has been related to a book, the default templates will use the publication
information (publisher, place of publication, ISBN) of the edition instance, not the 
publication information defined for the book instance. 


