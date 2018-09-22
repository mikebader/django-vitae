.. _topics-works-datasets:

Datasets
========

Django-Vitae includes a model to describe datasets produced by the author. The :class:`~cv.models.works.Dataset` class stores instances of these datasets. 

The :class:`~cv.models.works.Dataset` model has three required fields: 

* :attr:`title`

* :attr:`short_title`

* :attr:`slug`

The :class:`Dataset` model also includes an :attr:`authorship` field that allows for authorships of the :class:`Dataset`. The authorships are related to the :class:`Dataset` through a foreign-key relationship to the :class:`~cv.models.works.DatasetAuthorship` model. This model works the same way that the :ref:`authorship sets <topics-pubs-collaboration-sets>` on publications. 

A full description of fields can be found in the :class:`~cv.models.works.Dataset` field reference. 
