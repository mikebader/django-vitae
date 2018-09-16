Talks
=====

To list public presentations on CVs, Django-CV uses two models representing two different ideas. A "talk", represented by :class:`cv.models.Talk`, reflects a single idea conveyed with a title. It can optionally also include other other elements related to that talk such as notes and slides. A "presentation", represented by :class:`cv.models.Presentation`, reflects a specific public performance of a talk at a some location and at some time. 

This structure allows multiple presentations of the same talk to be logically 
connected and can prevent multiple listings with the same title, for example, in the 
"Presentations" section of a C.V. 	

Talks
-----

The :class:`~cv.models.Talk` model has three required fields: 

* :attr:`title`

* :attr:`short_title`

* :attr:`slug`

The publication set for a given talk can be accessed with the :attr:`presentations` attribute of a :class:`~cv.models.Talk` instance. 

The :class:`~cv.models.Talk` class contains a foreign key field, :attr:`article_from_talk` that connects a talk to an article. This may be useful to provide a link to the article on a page about the talk to make it clear where visitors can find the publication that resulted.  

The :class:`~cv.models.Talk` model also contains a convenience method, :meth:`~cv.models.Talk.get_latest_presenation` that returns the :class:`~cv.models.Presentation` instance of the talk that was most recently performed (using the :attr:`presentation_date` field). 

.. _topics_talks_views

Talk Views
^^^^^^^^^^

**Talk List**: :class:`~cv.views.TalkListView`

Display a list of all talks given in order of most recent presentation date. 

   ===============  ================================================================   
   Context object   ``{{talk_list}}``
   Template         ``'cv/lists/talk_list.html'``
   URL              ``r'^talks/$'``
   URL name         ``'talk_object_list'``
   MIME type        ``text/html``
   ===============  ================================================================   

**Talk Detail**: :class:`~cv.views.TalkDetailView`

Display detailed information for a particular talk. 

   ===============  ================================================================   
   Context object   ``{{talk}}``
   Template         ``'cv/details/talk_detail.html'``
   URL              ``r'^talks/(?P<slug>[-\w]+)/$'``
   URL name         ``'talk_object_detail'``
   MIME type        ``text/html``
   ===============  ================================================================   

Presentations
-------------

The :class:`~cv.models.Presentation` model instances relate to a :class:`~cv.models.Talk` instance through a foreign key. The :class:`~cv.models.Presentation` model has three required fields in addition to the :class:`~cv.models.Talk` foreign key:

* :attr:`presentation_date` that represents when this presentation was "performed;" presentations are ordered by presentation date with the most recent presentation first

* :attr:`type` represents the form of the presentation; choices are "Invited", "Conference", "Workshop", and "Keynote". 

* :attr:`event` contains the name of event or venue at which the presentation was given. 

Django-CV assumes that presentations will be displayed in conjunction with talks and, therefore, not displayed on their own. 


