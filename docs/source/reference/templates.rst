==================
Template Structure
==================

Complete CV HTML view
---------------------

..
	Text from docs/reference/views.rst:

The
``cv/cv.html`` template inherits from the ``cv/base.html`` template that
renders each of the sections into a Django template block. The order of the
sections should be defined in ``cv/cv.html`` by using those block names and
then using the ``{{block.super}}`` context to render each section from the
definitions in ``cv/base.html``. 

.. note::

    The ``cv/base.html`` template may be removed in future versions in favor
    of rendering the sections directly in ``cv/cv.html``. 

``django-vitae`` is designed to work "out of the box" so that someone could
simply enter their information and have a CV rendered. The
``cv/skeleton.html`` template contains all of the formatting, JavaScript, and
CSS. The default template uses CSS styles and Javascript from `Bootstrap`_
and icons from `Font Awesome`_ icons, using their respective `CDNs`_. 

.. _Bootstrap: https://getbootstrap.com/ 
.. _Font Awesome: https://fontawesome.com/
.. _CDNs: https://en.wikipedia.org/wiki/Content_delivery_network/


Custom theming (e.g., to fit with the rest of a website) can be accomplished
by including a local ``cv/skeleton.html`` template. Simply be sure to include
a block named ``centerbar`` where you would like the content to render. 

Complete CV PDF View
--------------------

..
	Text from docs/reference/views.rst:

**Template Structure**::

  cv/ pdf/ pdf_list.json <model name>.html

Creating PDFs requires that much of the style be controlled internally in the
code. The internal coding makes it difficult to customize the *style* of the
PDF version of the CV. The *content* can be customized, however, by using
templates. 

The content of the PDF, including the order, is controlled by the template
``cv/pdf/pdf_list.json`` `JSON`_ file. The JSON file is structured as a list
of dictionaries. Each dictionary **must** have a ``model_name`` key that is
the model name in lowercase. In addtion, the dictionary **may** have the
following keys: 

   ``display_name`` A string of the section heading (including any
   capitalization that you desire)

   ``date_field`` May either be a string representing the name of the field
   that you would like to use to display as the date in each entry for that
   section **or** a list of two strings, the field names to be used to render
   the start and end dates. 

   ``subsections`` A list of lists; each of the sub-lists should include two
   string values: the first contains the heading for the subsection and the
   second is a string representing the method of the :attr:`displayable`
   manager to use to get the queryset for that subsection. 

The ``templates/cv/pdf/`` also contains an XML file for each section of the
PDF. The XML files use the intra-paragraph markup described in the ReportLab
`User Guide`_ (subsection 6.3) that include the ``<i>`` tag for italics,
``<b>`` for boldface, and ``<a>`` for links (among others). 

.. _JSON: https://en.wikipedia.org/wiki/JSON
.. _User Guide: https://www.reportlab.com/docs/reportlab-userguide.pdf