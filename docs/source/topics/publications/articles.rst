.. _topics-pubs-articles:

Articles
--------

Article Model
^^^^^^^^^^^^^
=======================  =================================================
Model field reference    :class:`cv.models.publications.Article`
Authorship set           :class:`cv.models.publications.ArticleAuthorship`
=======================  =================================================

The :class:`~cv.models.publications.Article` model represents an instance
of an article or other publications with similar characteristics as 
articles (e.g., proceedings). 


.. _topics-pubs-articles-views:

Article Views
^^^^^^^^^^^^^

**Article List** : :class:`cv.views.CVListView`
   ===============  ==================================================================  
   Context object   ``{{object_list}}``
   Template         ``'cv/lists/article_list.html'``
   URL              ``'articles/'``
   MIME type        ``text/html``
   ===============  ================================================================== 
	
   The article list view produces a page with a list of an author's 
   articles. This may be helpful if an author does not wish to display
   a full CV, but wants to list just their articles. The page renders
   an instance of the :class:`cv.views.CVListView` view with the named 
   parameter ``model_name`` set to ``'article'``. The view returns the 
   ``{{object_list}}`` in the context with four objects on its dot path:

   ``total_articles``
      Integer of total number of article objects from all three status-based managers:

   ``article_published_list``
      queryset of all published articles (uses the :attr:`published()`
      method of the :class:`~cv.models.managers.PublicationManager`)
   
   ``article_revise_list``
      queryset of all articles in the revision process (uses the 
      :attr:`revise()` method of the 
      :class:`~cv.models.managers.PublicationManager`)
   
   ``article_inprep_list`` 
      queryset of all articles in preparation for submission (uses
      the :attr:`inprep()` method of the 
      :class:`~cv.models.managers.PublicationManager`)

   The URL can be accessed in templates by using the `URL template 
   filter`_ with the named URL ``section_list`` and ``model_name`` 
   parameter equal to ``article``, i.e.::

   {% url section_list model_name='article' %}

.. _URL template filter: https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#url


**Article Detail**: :class:`cv.views.CVDetailView`
   ===============  ================================================================   
   Context object   ``{{article}}``
   Template         ``'cv/details/article_detail.html'``
   URL              ``'articles/<slug:slug>/``
   MIME type        ``text/html``
   ===============  ================================================================
   
   The article detail view produces a page that represents a single 
   article. The default template includes the title, the abstract, 
   a link to the published version of the article (if published and 
   a URL is defined), and links to download the citation in both 
   RIS and BibTeX formats (described below). The page is rendered as 
   an instance of the class :class:`cv.views.CVDetailView` with the 
   named parameters ``model_name`` set to ``'article'`` and ``slug``
   set to the article's slug attribute. The view returns the 
   context ``{{article}}`` that represents the  :class:`Article` 
   instance.

   The URL can be accessed using the named URL ``item_detail`` with
   ``model_name`` set to ``'article'`` and ``slug`` set to the 
   article's slug attribute, i.e.::

   {% url item_detail model_name='article' slug='slug-from-short-title' %}

**Article Citation**: :func:`cv.views.citation_view`
   ===============  ================================================================   
   Context object   ``{{article}}``
   Templates        ``'cv/citations/article.ris'``
                    ``'cv/citations/article.bib'``
   URL              ``'articles/<slug:slug>/cite/<str:format>/'``
   MIME type        ``application/x-research-info-systems`` or 
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

