.. _topics-works-otherwriting:

Other Writing
=============

Django-Vitae comes with a model to describe writing other than presenting research findings. These can be book reviews, op eds, blog posts, or other types of non-academic writing. The :class:`~cv.models.OtherWriting` class stores instances of these writings. 

The :class:`~cv.models.OtherWriting` model has five required fields: 

* :attr:`title`

* :attr:`short_title`

* :attr:`slug`

* :attr:`date`

* :attr:`venue` (e.g., publication where the writing was published)

The :class:`~cv.models.works.OtherWriting` includes a field :attr:`type` that you may use to group different types of writing together on a CV (Django-Vitae does not, however, currently do this by default). 

A full reference of fields included in the ``OtherWriting`` model can be found in the :class:`cv.models.OtherWriting` model reference. 

