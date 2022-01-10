=====
Views
=====

.. module:: cv.views
   :noindex:
   :synopsis: Django-Vitae views

.. toctree::
   :name: viewstoc
   :maxdepth: 1
   :caption: Contents:

Django-Vitae uses four types of views: views for the complete CV, a list view
for a list of a single section (e.g., articles or books), a detail view that
contains information for particular items on the CV, and a view returning
downloadable citations. 

.. _views-complete:

Complete Document Views
-----------------------

.. highlight:: html+django

Django-Vitae provides two views that print the entire document in each of two
formats: :ref:`HTML <views-html>` and :ref:`PDF <views-pdf>`. 

.. _views-html:

HTML
^^^^

The primary view provided by Django Vitae, :class:`~cv.views.CVView`,
represents a CV as a webpage. This is the view made available at the
application's root URL (i.e., ``/``). 

.. _views-cvview-context:

Context
"""""""

The :class:`~cv.views.CVView` view returns a dictionary as the context.
The keys of the context dictionary have the pattern ``<model>_list`` where
model is the lowercase name of a cv model class (e.g., ``article`` or
``book``). The value stored for the section list key depends on the model:

  **Publication Models** (:class:`~cv.models.Article`,
  :class:`~cv.models.Book`, :class:`~cv.models.Chapter`, and
  :class:`~cv.models.Report`) contain  dictionaries with four keys:

        * ``total``: an integer recording the total number of items of the
          type
        * ``published``: a :class:`QuerySet` of published items
        * ``revision``: a :class:`QuerySet` of items under revision
        * ``inprep``: a :class:`QuerySet` of items in preparation

  :class:`~cv.models.Grant` contains a dictionary with three keys:

        * ``total`` : an integer recording the total number of internal and
          external grants
        * ``internal``: a :class:`QuerySet` of internal grants
        * ``external``: a :class:`QuerySet` of external grants

  :class:`~cv.models.Service` contains a dictionary with four keys:

        * ``total``: an integer recording total number of service items
        * ``discipline``: a :class:`QuerySet` of services provided to the
          discipline
        * ``university``: a :class:`QuerySet` of services provided to the
          university
        * ``department``: a :class:`QuerySet` of services provided to the
          department

  **All others** provide a :class:`QuerySet` of items of the type


The :class:`~cv.views.CVView` view renders the website using the template
``cv/cv.html``. The sections may be rendered with the inclusion template
tag :ttag:`section_list` that takes the string of the model name and the key
of the dictionary passed to the context and renders the output according to
the template for the model stored in the ``cv/sections/`` directory. For
example, to render the section of articles, you would use the following in a
template::

    {% load cv %}
    {% section_list 'article' article_list %}

As noted above, the :ttag:`section_list` uses the template stored in
``cv/sections/<model_name>.html`` (singular, not plural) to render the list
for that section. To change the rendering of a section, you may write a
custom template for that section and store that file in your local
``cv/sections/`` directory. 

.. _views-pdf: 

PDF
^^^

The :meth:`cv.views.pdf.cv_pdf` method-based view produces a PDF of the CV
using the `Report Lab`_ library. The PDF view may be retrieved as the
``/pdf/`` URL.  

.. _Report Lab: https://www.reportlab.com/

.. _views-single-section:

Single-Section View
-------------------

The :class:`cv.views.CVListView` returns a list of items from a single section
and is available at ``/<model_name_plural>`` URLs. The single-section view
uses the ``cv:section_list`` name in the URLconf. 

The :class:`~cv.views.CVListView` will use the template
``cv/lists/cv_list.html`` to render the HTML *unless* the template
``cv/lists/<model_name>.html`` exists. If the latter does exist, then the
section list will be rendered using that template instead. By default, the
``cv/lists/cv_list.html`` uses the same template files to render lists of
items that :class:`~cv.views.CVView` uses (i.e., those stored in the
``cv/sections/`` directory). 


.. _views-detail:

Detail View
-----------

The :class:`cv.views.CVDetailView` returns information about a single item.
The view is rendered at URLs ``/<model_name>/<slug>/`` the single-item view
uses the ``cv:detail_view`` name in the URLconf. 

An HTML page describing the item will be rendered using the template
``cv/details/cv_detail.html`` to render the HTML *unless* the template
``cv/details/<model_name>.html`` exists. If the latter does exist, then the
section list will be rendered using that template instead. 

.. _views-citation:

Citation View
-------------

The :meth:`~cv.views.citation_view` returns a downloadable citation of a
single item. The responses may be downloaded and used in citation management
software like Zotero_ or BibTeX_.

.. _Zotero: https://www.zotero.org/
.. _BibTex: http://www.bibtex.org/Format/

The model classes available for citation downloads are determined by the
setting :setting:`CITATION_VIEWS_AVAILABLE`. Models
:class:`~cv.models.Book`, :class:`~cv.models.Article`,
:class:`~cv.models.Chapter`, :class:`~cv.models.Report`,
:class:`~cv.models.Talk`, and :class:`~cv.models.Dataset` are available by
default.

The available formats for citations are determined by the
:setting:`CITATION_DOWNLOAD_FORMATS`
setting. :setting:`CITATION_DOWNLOAD_FORMATS` is a dictionary where keys are
strings representing the formats used in the URL (generally by the extension
of the file file type) and values are `MIME type`_ strings. The default
citation download formats are `Reference Manager (RIS)`_ and BibTex_ that
use files ending in ``.ris`` and ``.bib`` respectively. As a result, the
default :setting:`CITATION_DOWNLOAD_FORMATS` is initialized with the
dictionary::

    {
        'ris': 'application/x-research-info-systems',
        'bib': 'application/x-bibtex' 
    }

.. _`MIME type`: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
.. _`Reference Manager (RIS)`: https://en.wikipedia.org/wiki/RIS_(file_format)

If we were hosting W.E.B. Du Bois' CV, for example, we could download the
BibTeX citation for *The Philadelphia Negro* if the slug were
``philadelphia-negro`` at the URL ``book/philadelphia-negro/cite/bib``. If
the user has a BibTex distribution installed, she will be asked if she wants
to open the citation in that distribution; if not, the user will be asked by
her browser how to handle the file.

The view relies on a template being available at
``cv/citations/<model_name>.<fmt>`` for each model in the
:setting:`CITATION_VIEWS_AVAILABLE` dictionary.