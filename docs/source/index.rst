.. Django-CV documentation master file, created by
   sphinx-quickstart on Sat Jul 22 22:51:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django-CV Documentation
=======================

.. _overview:

Overview
--------

Django-CV allows users to make highly customizable curricula vitae for use on their websites. The application provides models for common entries on curricula vitae such as education, employment, publications, teaching, and service. Django-CV eliminates many of the repetitive tasks related to producing curricula vitae. The included templates provide a complete CV "out of the box", but allows researchers who might be interested to customize the format using Django templating language. 

.. _documentation-organization:

Organization of the Documentation
---------------------------------

* :doc:`CV Sections <topics/index>` documents the API to write lines on CV by 
  different sections on a CV
      
      * Education & Employment
      
      * :doc:`Publications <topics/publications/>` ( 
        :ref:`Articles <topics-pubs-articles>` |
        :ref:`Books <topics-pubs-books>` |
        :ref:`Chapters <topics-pubs-chapters>` |
        :ref:`Reports <topics-pubs-reports>`)
   
      * Grants
      
      * :doc:`Talks <topics/talks/>`
      
      * Public writing
      
      * Teaching
      
      * Service   

* Templates 

   * Template tags & filters
   
   * Template structure
   

* :ref:`Settings <custom_settings>`

* Module Reference


.. _contributing: 

Contributing to Django-CV
-------------------------
It's quite possible that Django-CV does not include all types of publications necessary. 
You may open an issue, or--even better--contribute code for other common types of 
publications not already incorporated into Django-CV. 



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 4
   :name: fronttoc
   
   topics/index
   shortcuts
   settings
   reference/index

