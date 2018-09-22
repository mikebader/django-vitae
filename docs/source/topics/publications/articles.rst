.. _topics-pubs-articles:

Articles
^^^^^^^^
Article Model
"""""""""""""
=======================                         ========================================
Model field reference                           :class:`cv.models.publications.Article`
Authorship set                                  :class:`cv.models.publications.ArticleAuthorship`
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

