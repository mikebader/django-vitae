.. _topics-pubs-chapters:

Chapters
^^^^^^^^

Chapter Model
"""""""""""""

The :class:`~cv.models.publications.Chapter` class stores instances of chapters. 

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
Model field reference                           :class:`cv.models.publications.Chapter`
Authorship set                                  :class:`cv.models.publications.ChapterAuthorship`
=======================                         ========================================

Chapter Views
"""""""""""""

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
   
   ``chapter_published_list``
      :class:`~django.db.models.query.QuerySet` of all published chapters (uses the 
      `published manager <topics-pubs-published-manager>`)
   
   ``chapter_revise_list``
      :class:`~django.db.models.query.QuerySet` of all chapters in the 
      revision process (uses the `revise manager <topics-pubs-revise-manager>`)
   
   ``chapter_inprep_list`` 
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
   :class:`~cv.models.publications.Chapter` instance.

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

