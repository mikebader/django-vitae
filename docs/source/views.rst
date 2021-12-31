Views
=====

.. toctree::
   :name: viewstoc
   :maxdepth: 1
   :caption: Contents:

``django-vitae`` uses four types of views: views for the complete CV with different sections, a list view for a list of a single section (e.g., articles or books), a detail view that contains information for particular items on the CV, and a view returning citations. 

.. _views-complete:

Complete Document Views
^^^^^^^^^^^^^^^^^^^^^^^

Django Vitae provides two views that print the entire document in each of two formats: HTML and PDF. 

.. _views-html:

HTML
""""

The primary view provided by Django Vitae, :class:`cv.views.CVView`,  represents a CV as a webpage. This is the view made available at the application's root URL (i.e., 
``/``). 

The view renders the website using the template ``cv/cv.html``. The ``cv/cv.html`` template inherits from the ``cv/base.html`` template that renders each of the sections into a Django template block. The order of the sections should be defined in ``cv/cv.html`` by using those block names and then using the ``{{block.super}}`` context to render each section from the definitions in ``cv/base.html``. 

.. note::

    The ``cv/base.html`` template may be removed in future versions in favor of rendering the sections directly in ``cv/cv.html``. 

The :class:`~cv.views.CVView` view returns variables for each model in a ``<<model>>_list`` that contains items for that type of entry. The value of the context variable depends on the model.

  **Publication Models** (:class:`~cv.models.Article`, :class:`~cv.models.Book`, :class:`~cv.models.Chapter`, and :class:`~cv.models.Report`) contain  dictionaries with four keys:

        * ``total``: an integer recording the total number of items of the type
        * ``published``: a :class:`QuerySet` of published items
        * ``revision``: a :class:`QuerySet` of items under revision
        * ``inprep``: a :class:`QuerySet` of items in preparation

  :class:`~cv.models.Grant` contains a dictionary with three keys:

        * ``total`` : an integer recording the total number of internal and external grants
        * ``internal``: a :class:`QuerySet` of internal grants
        * ``external``: a :class:`QuerySet` of external grants

  :class:`~cv.models.Service` contains a dictionary with four keys:

        * ``total``: an integer recording total number of service items
        * ``discipline``: a :class:`QuerySet` of services provided to the discipline
        * ``university``: a :class:`QuerySet` of services provided to the university
        * ``department``: a :class:`QuerySet` of services provided to the department

  **All others** provide a :class:`QuerySet` of items of the type


The sections are rendered with the inclusion template tag :meth:`~cv.templatetags.cv.section_list` that takes two required and one optional parameter: the string name of the model (e.g., ``'article'`` for articles), the name of the context variable containing items (e.g., ``article_list``), and the section title as a string (e.g., ``'Publications: Articles'``).

The :meth:`~cv.templatetags.cv.section_list` tag will use the template stored in ``cv/sections/<<model_name>>.html`` to render the list for that section. Therefore, if you wanted to change how a single section was rendered, you could write a custom template for that section and store that file in your local ``cv/sections/`` directory. 

``django-vitae`` is designed to work "out of the box" so that someone could simply enter their information and have a CV rendered. The ``cv/skeleton.html`` template contains all of the formatting, JavaScript, and CSS. The default template uses CSS styles and Javascript from `Bootstrap`_ and icons from `Font Awesome`_ icons, using their respective `CDNs`_. 

.. _Bootstrap: https://getbootstrap.com/ 
.. _Font Awesome: https://fontawesome.com/
.. _CDNs: https://en.wikipedia.org/wiki/Content_delivery_network/


Custom theming (e.g., to fit with the rest of a website) can be accomplished by including a local ``cv/skeleton.html`` template. Simply be sure to include a block named ``centerbar`` where you would like the content to render. 

.. _views-pdf: 

PDF
"""

Django Vitae will also create a PDF of your CV "on-the-fly". 

The PDF version of your CV can be found at the ``/pdf/`` URL. The 
URL retrives the view :class:`cv.views.pdf.cv_pdf`. The view 
gathers data from different sections of the CV and then creates a 
PDF using the `Report Lab`_ library. 

.. _Report Lab: https://www.reportlab.com/

**Template Structure**::

  cv/
    pdf/
        pdf_list.json
        <model name>.html

Creating PDFs requires that much of the style be controlled 
internally in the code. The internal coding makes it difficult to 
customize the *style* of the PDF version of the CV. The *content* 
can be customized, however, by using templates. 

The content of the PDF, including the order, is controlled by the 
template ``cv/pdf/pdf_list.json`` `JSON`_ file. The JSON file is 
structured as a list of dictionaries. Each dictionary **must** have 
a ``model_name`` key that is the model name in lowercase. In 
addtion, the dictionary **may** have the following keys: 

   ``display_name``
      A string of the section heading (including any capitalization 
      that you desire)

   ``date_field``
      May either be a string representing the name of the field 
      that you would like to use to display as the date in each 
      entry for that section **or** a list of two strings, the 
      field names to be used to render the start and end dates. 

   ``subsections``
      A list of lists; each of the sub-lists should include two 
      string values: the first contains the heading for the 
      subsection and the second is a string representing the method 
      of the :attr:`displayable` manager to use to get the queryset 
      for that subsection. 

The ``templates/cv/pdf/`` also contains an XML file for each 
section of the PDF. The XML files use the intra-paragraph markup 
described in the ReportLab `User Guide`_ (subsection 6.3) that 
include the ``<i>`` tag for italics, ``<b>`` for boldface, and 
``<a>`` for links (among others). 

.. _JSON: https://en.wikipedia.org/wiki/JSON
.. _User Guide: https://www.reportlab.com/docs/reportlab-userguide.pdf


.. _views-single:

Single-Section View
^^^^^^^^^^^^^^^^^^^

The :class:`~cv.views.CVListView` returns a list of items from a single section and is available at ``/<<model_name_plural>>`` URLs, relative to the location of the CV directory, using the ``cv:section_list`` `URLconf`_ name. 

.. _URLconf: https://docs.djangoproject.com/en/4.0/topics/http/urls/#overview

An instance of the :class:`~cv.views.CVListView` will use the template ``cv/lists/cv_list.html`` to render the HTML *unless* the template ``cv/lists/<<model_name>>.html`` exists. If the latter does exist, then the section list will be rendered using that template instead. 

By default, the ``cv/lists/cv_list.html`` uses the same template files to render lists of items that :class:`~cv.views.CVView` uses (i.e., those stored in the ``cv/sections/`` directory). 


.. _views-detail:

Detail View
^^^^^^^^^^^

The :class:`~cv.views.CVDetailView` returns information about a single item. The view is rendered at URLs ``/<<model_name>>/<<slug>>/`` using the ``cv:detail_view`` URLconf name. 

An HTML page describing the item will be rendered using the template 
``cv/details/cv_detail.html`` to render the HTML *unless* the template ``cv/details/<<model_name>>.html`` exists. If the latter does exist, then the section list will be rendered using that template instead. 

.. note::

    At present, detail views are hard-coded to be limited to the :class:`~cv.models.Article`, :class:`~cv.models.Book`, :class:`~cv.models.Chapter`, :class:`~cv.models.Report`, :class:`~cv.models.Talk`, and :class:`~cv.models.Dataset` models. In the future, users may be able to set these using :mod:`settings`. 

.. _views-citation:

Citation Views
^^^^^^^^^^^^^^

The :meth:`~cv.views.citation_view` returns citations for a given item based on either the `Reference Manager`_ (``.ris``) or `BibTeX` (``.bib``) formats. Both return plain-text files containing a single citation for the specified item. The views are available at the URL ``/<<model_name>>/<<slug>>/cite/<<format>>`` where format is either ``ris`` or ``bib`` using the ``cv:citation`` URLconf name. 

.. _Reference Manager: https://en.wikipedia.org/wiki/RIS_(file_format)
.. _BibTeX: http://www.bibtex.org/Format/

The templates for citation styles are saved in the ``cv/citations/`` directory.

