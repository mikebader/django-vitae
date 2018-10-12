.. _topics-pubs-reports:

Reports
-------

Report Model
^^^^^^^^^^^^
=======================  =================================================
Model field reference    :class:`cv.models.Report`
Authorship set           :class:`cv.models.ReportAuthorship`
=======================  =================================================

The :class:`~cv.models.publications.Report` model represents an instance
of a report or a publication with a similar format to a report (e.g., 
policy brief, working paper, etc.)

.. _topics-pubs-reports-views:

Report Views
^^^^^^^^^^^^
**Report List** : :class:`cv.views.CVListView`

   ===============  ================================================================   
   Context object   ``{{report_objects}}``
   Template         ``'cv/lists/report_list.html'``
   URL              ``'reports/'``
   MIME type        ``text/html``
   ===============  ================================================================   

   The report list view produces a page with a list of an author's
   reports. The page is a rendered instance of the 
   :class:`cv.views.CVListView` view with the named parameter 
   ``model_name`` set to ``'report'``. The view returns the object
   ``{{object_list}}`` in the context with with four objects on 
   its dot path: 

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

   The URL can be accessed in templates by using the `URL template 
   filter`_ with the named URL ``section_list`` and ``model_name`` 
   parameter equal to ``report``, i.e.::

   {% url section_list model_name='report' %}

.. _URL template filter: https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#url

**Report Detail**: :class:`cv.views.CVDetailView`
   ===============  ================================================================   
   Context object   ``{{report}}``
   Template         ``'cv/details/report_detail.html'``
   URL              ``'reports/<slug:slug>/'``
   MIME type        ``text/html``
   ===============  ================================================================
   
   The report detail view produces a representation of a single 
   report. The page renders an instance of 
   :class:`cv.views.CVDetailView` with the named parameters 
   ``model_name`` set to ``'report'`` and the ``slug`` set to the 
   value of the report's ``slug`` field. The view returns the 
   context object ``{{report}}`` that represents a single 
   :class:`~cv.models.Report` instance.

**Report Citation**: :func:`cv.views.citation_view`
   ===============  ================================================================   
   Context object   ``{{report}}``
   Templates        ``'cv/citations/report.ris'``
                    ``'cv/citations/report.bib'``
   URL              ``'reports/<slug:slug>/citation/<str:format>/'``
   MIME types       ``application/x-research-info-systems``
                    ``application/x-bibtex``
   ===============  ================================================================

   Creates representation of a report as a file that can be 
   downloaded or exported to citation management software. 

   The :attr:`<str:format>` named parameter should be one of:
   
   ``'ris'``
      will create downloadable citation using Reference Manager format specification (see 
      http://endnote.com/sites/rm/files/m/direct_export_ris.pdf).
    
   ``'bib'``
      will create downloadable citation using the BibTeX format specification (see
      http://www.bibtex.org/Format/)
   

