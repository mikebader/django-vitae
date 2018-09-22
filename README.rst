==============
django-vitae
==============

Django-Vitae is a CV generator that can be used with the `Django`_ web framework.

.. _Django: https://docs.djangoproject.com/

Many academics have trouble keeping CVs up to date. Django-Vitae was created to streamline this process. Django-Vitae allows users to make highly customizable curricula vitae for use on their websites. The application provides models for common entries on curricula vitae such as education, employment, publications, teaching, and service. Django-Vitae eliminates many of the repetitive tasks related to producing curricula vitae. The included templates provide a complete CV "out of the box", but allows researchers who might be interested in customizing the format using Django templating language. 

Django-Vitae uses `semantic versioning`_. Though it aims to provide a complete suite to create a CV, the project does not been tested extensively (and **you** can contribute to that effort!) and pieces might still throw errors. See notes below for quirks and errors in usage that must be resolved. 

.. _semantic versioning: http://semver.org/


Requirements
------------

Django-Vitae is developed and tested in Python 3. It depends on several external packages (other than Django): 

* `Markdown <https://pypi.org/project/Markdown/>`_ (makes pretty HTML with simple text entries)
* `citeproc-py <https://pypi.org/project/citeproc-py/>`_ (creates citations formatted according to desired `CSL`_ styles [not yet implemented])
* `citeproc-py-styles <https://pypi.org/project/citeproc-py-styles/>`_ (adds library of `CSL`_ styles)

.. _CSL: http://citationstyles.org/

Installation
------------
From `PyPI <https://pypi.org/>`_::

    pip install django-vitae

For the latest development version: 

::

    git clone https://github.com/mikebader/django-vitae
    cd django-vitae
    python setup.py install

If you are new to Django_, you may want to visit the `Getting Started`_ guide in the documentation. 

.. _`Getting Started`: https://djangocv.readthedocs.io/en/latest/getting_started.html

Documentation
-------------

Incomplete documentation can be found in the ``docs/`` directory and at http://djangocv.readthedocs.io/.

Testing
-------
To test, you need to install the following packages: 

* `Nose`_ & `django-nose`_ (used for testing suite)
* `Coverage`_ (used to document testing coverage)

.. _Nose: https://pypi.org/project/nose/
.. _django-nose: https://pypi.org/project/nose/
.. _Coverage: https://pypi.org/project/coverage/

:: 

    pip install nose
    pip install django-nose
    pip install coverage

A test suite can be found in the ``tests/`` directory. With `Nose`_ and `Coverage`_ installed, you may run the tests with ``runtests.py``. From the ``django-vitae`` root directory: 

::

    ./runtests.py


To test only a single model, you may use the flag ``--attr=<model_name>`` for the model (not implemented for all models). For example, to test books, you would use:

::

    ./runtests.py --attr=book



Known Issues
------------

At present, you will have the best luck editing model instances in the ``admin`` interface. You should be able to edit some models in interface implemented in the default templates, but many do not work or are not fully implemented. 
