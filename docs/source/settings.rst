.. _custom_settings:

Settings
========
.. setting:: CV_PUBLICATION_STATUS_CHOICES

``CV_PUBLICATION_STATUS_CHOICES``
---------------------------------

Default: 

.. code-block:: python

   (
   	 (0,'INPREP',_('In preparation')),
	 (1,'WORKING',_('Working paper')),
	 (20,'SUBMITTED',_('Submitted')),
	 (30,'REVISE',_('Revise')),
	 (35,'RESUBMITTED',_('Resubmitted')),
	 (40,'CONDACCEPT', _('Conditionally accepted')),
	 (50,'FORTHCOMING',_('Forthcoming')),
	 (55,'INPRESS', _('In press')),
	 (60,'PUBLISHED',_('Published')),
	 (99,'RESTING',_('Resting'))
   )

A list specifying the constants and display values used to create choices
for the ``status`` field of :class:`~cv.models.VitaePublicationModel` proxy
class and which publications :ref:`topics-pubs-common-managers` return

Django-CV managers. Each option must be composed of three elements: 

*  an integer setting the constant used by the database to store values

*  a string indicating what the constant will be be called; these values
   will be used to set a constant with the suffix ``_STATUS`` in the 
   :mod:`cv.settings` module. 

*  value that will be displayed as the choice 

Internally, Django-CV organizes the type of publication based on the value 
of the integer used for the choice. The following table shows the ranges
used for different publication statuses.

===========  ======  =================  ====================================
Values >=    and <   Status             Manager
===========  ======  =================  ====================================
0            10      In preparation  	:class:`~cv.models.InprepManager` 

10           20      Reserved for user  <none>
                     to use as needed 

20           50      In revision		:class:`~cv.models.ReviseManager`

50           90      Published          :class:`~cv.models.PublishedManager`

90                   Reserved for user  <none>
                     to use as needed 
===========  ======  =================  ====================================


.. setting:: CV_FILE_TYPES_CHOICES

``CV_FILE_TYPES_CHOICES``
-------------------------

Default: 

.. code-block:: python

	CV_FILE_TYPES_CHOICES = (
		(10, 'MANUSCRIPT_FILE', _('Manuscript')),
		(20, 'PREPRINT_FILE', _('Preprint')),
		(30, 'DRAFT_FILE', _('Draft')),
		(40, 'SLIDE_FILE', _('Slides')),
		(50, 'CODE_FILE', _('Code')),
		(60, 'TABLE_FILE', _('Table')),
		(70, 'IMAGE_FILE', _('Image')),
		(80, 'SUPPLEMENT_FILE', _('Supplement')),
		(100, 'OTHER_FILE', _('Other'))
	)

A tuple that contains the values, names, and labels of choices to classify 
file types for :class:`~cv.models.CVFile`. The :mod:`cv.settings` module 
stores tuple of values and labels of choices in :attr:`FILE_TYPES_CHOICES` 
and a dictionary of names to access choice values in :attr:`FILE_TYPES`.

.. setting:: CV_STUDENT_LEVELS_CHOICES

.. _cv-student-levels-choices:

``CV_STUDENT_LEVELS_CHOICES``
-----------------------------

Default:

.. code-block:: python

	CV_STUDENT_LEVELS_CHOICES =(
		(0,'UNDERGRAD',_('Undergraduate student')),
		(10,'MASTERS',_('Masters student')),
		(20,'DOCTORAL',_('Doctoral student'))
		)

A tuple of three-tuples that each contain the value, name, and label to 
customize the choices related to the level of student. Used for the 
:class:`cv.models.Student` model for advising and for student collaborations
in publication 
:ref:`authorship sets <topics-pubs-collaboration-sets>`.  

.. setting:: CV_SERVICE_TYPES_CHOICES

``CV_SERVICE_TYPES_CHOICES``
----------------------------

Default:

.. code-block:: python

	CV_SERVICE_TYPES_CHOICES = (
		(10,'DEPARTMENT',_('Department')),
		(20,'SCHOOL', _('School or College')),
		(30,'UNIVERSITY',_('University-wide')),
		(40,'DISCIPLINE',_('Discipline')),
		(50,'COMMUNITY',_('Community')),
		(90,'OTHER',_('Other'))
		)

A tuple of three-tuples that each contain the value, name, and label to 
customize the choices related to the types of service. 

.. setting:: CV_KEY_CONTRIBUTORS_LIST
	
``CV_KEY_CONTRIBUTORS_LIST``
----------------------------

Default: ``[]`` (Empty list)

A list of e-mails identifying contributors that should be highlighted in the CV. 

