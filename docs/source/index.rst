.. Django-Vitae documentation master file, created by
   sphinx-quickstart on Sat Jul 22 22:51:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django-Vitae Documentation
==========================

.. _overview:

Overview
--------

Django-Vitae allows users to make highly customizable curricula vitae for use on their websites. The application provides models for common entries on curricula vitae such as education, employment, publications, teaching, and service. Django-Vitae eliminates many of the repetitive tasks related to producing curricula vitae. The included templates provide a complete CV "out of the box", but allows researchers who might be interested to customize the format using Django templating language. 

Installation
------------

A stable version of Django-Vitae is available in the `Python Package Index`_ and can be installed using ``pip``::

    $ pip install django-vitae

.. _`Python Package Index`: https://pypi.org/project/django-vitae/

The latest development version can be obtained from `GitHub`_::

    $ git clone https://github.com/mikebader/django-vitae
    $ cd django-vitae
    $ python setup.py install

.. _GitHub: https://github.com/mikebader/django-vitae/tree/dev

If you do not have experience with Django_, you might be interested in the :ref:`Getting Started <getting-started>` guide. 

.. _Django: https://www.djangoproject.com

.. _contributing: 

Contributing to Django-Vitae
----------------------------
It's quite possible that Django-Vitae does not include all types of publications necessary. 
You may open an issue, or--even better--contribute code for other common types of 
publications not already incorporated into Django-Vitae. 



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 3
   :name: fronttoc
   
   about
   getting_started
   views
   topics/index
   shortcuts
   settings
   reference/index

