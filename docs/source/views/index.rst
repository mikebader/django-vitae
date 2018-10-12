Complete Vitae Views
====================

.. toctree::
   :name: viewstoc
   :maxdepth: 1
   :caption: Contents:

.. _views-html:

Django Vitae provides two primary views that represent the entire CV 
document: HTML and PDF. 

HTML
^^^^

The primary view provided by Django Vitae represents a CV as a webpage. 
This is the view made available at the application's root URL, that is 
``/``. The URL retrieves the view :class:`cv.views.CVView` that gathers 
the data from individual models and presents them in appropriate sections. 

**Template Structure**::

  cv/
    sections/
        <plural model name>.html
    base.html
    cv.html
    skeleton.html


The HTML views use a series of templates layered on top of one 
another. At the lowest level, ``cv/skeleton.html`` **defines the 
main structure for the page**. The default template uses CSS styles 
and Javascript from `Bootstrap` and icons from `Font Awesome`_ 
icons, using their respective `CDNs`_. 

.. _Bootstrap: https://getbootstrap.com/ 
.. _Font Awesome: https://fontawesome.com/
.. _CDNs: https://en.wikipedia.org/wiki/Content_delivery_network/

At the next layer, the ``cv/base.html`` template inherits from 
``cv/skeleton.html`` and **defines the order of sections** as a 
series of Django template blocks. This is done by using `blocks`_ 
from Django templates. The name of each block corresponds to the 
the plural of the model name, except the blocks for 
:class:`~cv.models.works.OtherWriting` and 
:class:`~cv.models.base.Service` are named ``otherwriting`` and 
``service``. 

.. _blocks: https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#block

The template ``cv/cv.html`` inherits from the ``cv/base.html`` 
template and **defines the style for each section**. In the default 
template, each block consists of a ``<div>`` block and then 
`includes`_ the section template in the ``templates/cv/sections`` 
directory. The section template is an html file named for the 
plural form of the section name (except for :class:`OtherWriting` 
and :class:`Service`, as above); for example, the section template 
for articles would be the file 
``templates/cv/sections/articles.html``. If you would like to 
customize the look of an individual section, you should save a 
file with that name in the ``cv/sections/`` subdirectory of the
template directory of your own project. 

.. _includes: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include

.. _views-pdf: 

PDF
^^^

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
template ``pdf_list.json`` `JSON`_ file. The JSON file is 
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



