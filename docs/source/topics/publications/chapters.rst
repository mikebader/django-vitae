.. _topics-pubs-chapters:

Chapters
--------

Chapter Model
^^^^^^^^^^^^^
=======================  =================================================
Model field reference    :class:`cv.models.publications.Chapter`
Authorship set           :class:`cv.models.publications.ChapterAuthorship`
Editorship set           :class:`cv.models.publications.ChapterEditorship`
=======================  =================================================

The :class:`~cv.models.publications.Chapter` model represents an instance
of a chapter. In addition to the :attr:`authorship` attribute that saves 
authorship information, the :class:`Chapter` class also has an 
:attr:`editorship` attribute that contains information about editors of 
the volume in which the chapter appears. The editorship relationship 
operates the same way as 
:ref:`authorship sets <topics-pubs-collaboration-sets>` and include 
the same fields, except that the ``editorship`` model does not contain a 
``student_colleague`` field.

Chapter Views
^^^^^^^^^^^^^

**Chapter List** : :class:`cv.views.CVListView`
   ===============  ================================================================   
   Context object   ``{{chapter_objects}}``
   Template         ``'cv/lists/chapter_list.html'``
   URL              ``'chapters/'``
   MIME type        ``text/html``
   ===============  ================================================================   

   The chapter list view produces a page with a list of the author's 
   chapters. The page renders an instance of the 
   :class:`cv.views.CVListView` with the named parameter 
   ``model_name`` set to ``'chapter'``. This view returns the object 
   ``{{object_list}}`` in the context with four objects on its dot 
   path: 

   ``total_chapters``
      Integer of total number of chapters from all three managers:
   
   ``chapter_published_list``
      queryset of all published chapters (uses the :attr:`published()`
      method of the :class:`~cv.models.managers.PublicationManager`)
   
   ``chapter_revise_list``
      queryset of all chapters in the revision process (uses the 
      :attr:`revise()` method of the 
      :class:`~cv.models.managers.PublicationManager`)
   
   ``chapter_inprep_list`` 
      queryset of all chapters in preparation for submission (uses
      the :attr:`inprep()` method of the 
      :class:`~cv.models.managers.PublicationManager`)

   The URL can be accessed in templates by using the `URL template 
   filter`_ with the named URL ``section_list`` and ``model_name`` 
   parameter equal to ``chapter``, i.e.::

   {% url section_list model_name='chapter' %}

.. _URL template filter: https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#url

**Chapter Detail**: :class:`cv.views.ChapterDetailView`
   ===============  ================================================================   
   Context object   ``{{chapter}}``
   Template         ``'cv/details/chapter_detail.html'``
   URL              ``'chapters/<slug:slug>/'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   The chapter detail view produces a page that represents a single
   chapter. The default template includes the title, the abstract, 
   and links to download the citation in both RIS and BibTeX formats 
   (described below). The page is rendered as an instance of the 
   :class:`cv.views.CVDetailView` view with the named parameters
   ``model_name`` set to ``'chapter'`` and the ``slug`` set to the
   value of the chapter's slug field. The view returns the context
   ``{{chapter}}`` that represents a the
   :class:`~cv.models.publications.Chapter` instance.

   The URL can be accessed using the named URL ``item_detail`` with
   with ``model_name`` set to ``article`` and ``slug`` set to the 
   article's slug attribute, i.e.::

   {% url item_detail model_name='chapter' slug='slug-from-short-title' %}   

**Chapter Citation**: :func:`cv.views.book_citation_view`
   ===============  ================================================================   
   Context object   ``{{chapter}}``
   Templates        ``'cv/citations/chapter.ris'``
                    ``'cv/citations/chapter.bib'``
   URL              ``'chapter/<slug:slug>/citation/<str:format>/'``
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

