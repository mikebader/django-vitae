.. _topics-pubs-reports:

Reports
^^^^^^^

Report Model
""""""""""""

The :class:`~cv.models.Report` class stores instances of reports that can also be used for other non-article publications. The :attr:`abstract` field
takes Markdown_ input and saves the converted HTML to the non-editable 
:attr:`abstract_html` field. 

.. _Markdown: https://daringfireball.net/projects/markdown/syntax


=======================                         ========================================
Model field reference                           :class:`cv.models.Report`
Authorship set                                  :class:`cv.models.ReportAuthorship`
=======================                         ========================================

Report Views
""""""""""""
**Report List** : :class:`cv.views.ReportListView`

   ===============  ================================================================   
   Context object   ``{{report_objects}}``
   Template         ``'cv/lists/report_list.html'``
   URL              ``'reports/'``
   URL name         ``'report_object_list'``
   MIME type        ``text/html``
   ===============  ================================================================   

   Returns context ``{{report_objects}}`` with four objects on the dot path: 

   ``total_reports``
      Integer of total number of books from all three managers:
   
   ``report_published_list``
      :class:`~django.db.models.query.QuerySet` of all published books (uses the 
      `published manager <topics-pubs-published-manager>`)
   
   ``report_revise_list``
      queryset of all books in the revision process (uses the `revise manager 
      <topics-pubs-revise-manager>`)
   
   ``report_inprep_list`` 
      queryset of all books in preparation for submission (uses the `inprep manager 
      <topics-pubs-published-manager>`)

**Report Detail**: :class:`cv.views.ReportDetailView`

   ===============  ================================================================   
   Context object   ``{{report}}``
   Template         ``'cv/details/report_detail.html'``
   URL              ``'reports/<slug:slug>/'``
   URL name         ``'report_object_detail'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   Returns context ``{{report}}`` that represents a single 
   :class:`~cv.models.Report` instance.

**Report Citation**: :func:`cv.views.report_citation_view`

   ===============  ================================================================   
   Context object   ``{{report}}``
   Templates        ``'cv/citations/report.ris'``
                    ``'cv/citations/report.bib'``
   URL              ``'reports/<slug:slug>/citation/<str:format>/'``
   URL name         ``'report_citation'``
   MIME types       ``application/x-research-info-systems``
                    ``application/x-bibtex``
   ===============  ================================================================



