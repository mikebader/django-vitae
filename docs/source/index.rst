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

.. _GitHub: https://github.com/mikebader/django-vitae

If you do not have experience with Django_, you might be interested in the :ref:`Getting Started <getting-started>` guide. 

.. _Django: https://www.djangoproject.com

.. _documentation-organization:

Organization of the Documentation
---------------------------------

* :doc:`CV Sections <topics/index>` documents the API to write lines on CV by 
  different sections on a CV
      
      * Education & Employment
      
      * :doc:`Publications <topics/publications/index/>` ( 
        :ref:`Articles <topics-pubs-articles>` |
        :ref:`Books <topics-pubs-books>` |
        :ref:`Chapters <topics-pubs-chapters>` |
        :ref:`Reports <topics-pubs-reports>`)
   
      * :doc:`Other Works <topics/works/index/>` (
        :ref:`Grants <topics-works-grants>` |
        :ref:`Talks <topics-works-talks>` |
        :ref:`Other Writing <topics-works-otherwriting>` |
        :ref:`Datasets <topics-works-datasets>`)
      
      * Teaching
      
      * Service   

* Templates 

   * Template tags & filters
   
   * Template structure
   

* :ref:`Settings <custom_settings>`

* Module Reference


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
   
   getting_started
   topics/index
   shortcuts
   settings
   reference/index

