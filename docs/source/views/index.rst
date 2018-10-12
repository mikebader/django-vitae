Views
=====

.. toctree::
   :name: viewstoc
   :maxdepth: 1
   :caption: Contents:

.. _views-html:

Django Vitae provides two primary views for a CV: HTML and PDF. 

HTML
^^^^

The primary view provided by Django Vitae represents CVs as webpages. This is the view made available at the application's root URL, that is ``/``. The URL retrieves the view :class:`cv.views.CVView` that gathers the data from individual models and presents them in appropriate sections. 

Template Structure
~~~~~~~~~~~~~~~~~~

Template structure::

  cv/
    sections/
        <plural model name>.html
    base.html
    cv.html
    skeleton.html


The HTML views use a series of templates. At the lowest level, ``cv/skeleton.html`` defines the main structure for the page. The default template uses `Bootstrap`_ CSS styles and JavaScript and `Font Awesome`_ icons from their respective CDNs. 

.. _Bootstrap: https://getbootstrap.com/ 
.. _Font Awesome: https://fontawesome.com/

The next template, ``cv/base.html`` inherits from ``cv/skeleton.html`` and **defines the order of sections** as a series of Django template blocks. The template ``cv/cv.html`` inherits from the ``cv/base.html`` template and defines each section. 

In the default templates included with Django Vitae, ``cv/cv.html`` wraps sections in a ``<div>`` block and then `includes`_ a template for that section. These included templates are found in the ``sections`` directory in the root ``cv`` template directory. If you would like to customize the look of an individual section, you should write your own templates for the section you want to modify. The name of the section template is the plural of the model name; for example, the template for the :class:`~cv.models.base.Degree` model is ``cv/sections/degrees.html`` (the one exception is the template for :class:`~cv.models.works.OtherWriting`, which is simply ``cv/sections/otherwriting.html``). 

.. _includes: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include

.. _views-pdf: 

PDF
^^^