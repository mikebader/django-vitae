=========
django-cv
=========

Django-CV is a CV generator that can be used with the `Django`_ web framework.

.. _Django: https://docs.djangoproject.com/

Many academics have trouble keeping CVs up to date. Django-CV was created to streamline this process. Django-CV allows users to make highly customizable curricula vitae for use on their websites. The application provides models for common entries on curricula vitae such as education, employment, publications, teaching, and service. Django-CV eliminates many of the repetitive tasks related to producing curricula vitae. The included templates provide a complete CV "out of the box", but allows researchers who might be interested to customize the format using Django templating language. 

Django-CV uses `semantic versioning`_. Though it aims to provide a complete suite to create a CV, the project does not been tested extensively (and **you** can contribute to that effort!) and pieces might still throw errors. See notes below for quirks and errors in usage that must be resolved. 

.. _semantic versioning: http://semver.org/


Requirements
------------

Django-CV is developed and tested in Python 3. It depends on several external packages (other than Django): 

* `Markdown <https://pypi.org/project/Markdown/>`_ (makes pretty HTML with simple text entries)
* `Nose`_ & `django-nose`_ (used for testing suite)
* `Coverage`_ (used to document testing coverage)
* `citeproc-py <https://pypi.org/project/citeproc-py/>`_ (creates citations formatted according to desired `CSL`_ styles [not yet implemented])
* `citeproc-py-styles <https://pypi.org/project/citeproc-py-styles/>`_ (adds library of `CSL`_ styles)

.. _CSL: http://citationstyles.org/
.. _Nose: https://pypi.org/project/nose/
.. _django-nose: https://pypi.org/project/nose/
.. _Coverage: https://pypi.org/project/coverage/

Testing
-------
An incomplete test suite can be found in the ``tests/`` directory. With `Nose`_ and `Coverage`_ installed, you may run the tests with ``runtests.py``.


Use Issues
----------

At present, you will have the best luck editing model instances in the ``admin`` interface. You should be able to edit some models in interface implemented in the default templates, but many do not work or are not fully implemented. 

You may find limited documentation in the ``docs/`` directory. 

