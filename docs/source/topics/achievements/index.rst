Achievements
============

The first sections of CVs list one's achievements. The models below allow CV authors to record these achievements. 


.. _topics-achievements-degrees:

Degrees
-------

The :class:`~cv.models.achievements.Degree` model stores instances of degrees earnned and has three required fields:

* :attr:`degree`

* :attr:`date_earned`

* :attr:`institution` that granted the degree

The :class:`Degree` model inherits from :class:`~cv.models.base.DisplayableModel` and therefore has an :attr:`extra` field that can be used to enter information about the degree. For the special case of honors, the :class:`Degree` model has a field, :attr:`honors`, that allows information such as whether a degree was attained *cum laude*. 

Model instances are sorted in reverse chronological order using the :attr:`date_earned` values. 


.. _topics-achievements-positions:

Positions
---------

The :class:`~cv.models.achievements.Position` model stores instances of jobs or research experience and has three required fields

* :attr:`title`

* :attr:`start_date`

* :attr:`institution`

The model also contains fields that allow the user to specify the :attr:`department` in which the user worked, as well as a :attr:`project` within the department. 

Model instances are sorted in reverse chronological order by the :attr:`end_date` field first and the :attr:`start_date` second. 

The model also has a Boolean field :attr:`primary_position` that allows the user to indicate if the position represents the primary title. The :attr:`primary_position` field is used, for example, in the heading of the :ref:`HTML <views-html>` and :ref:`PDF <views-pdf>` views. The model also comes with a :attr:`primary_position` manager that accesses the :class:`~cv.models.managers.PrimaryPositionManager` that returns only :class:`Position` instances marked as being primary positions. 


.. _topics-achievements-awards:

Awards
------

The :class:`~cv.models.achievements.Award` model stores instances of honors or awards that the user has received. The model has three required fields: 

* :attr:`name` of the award

* :attr:`organization` that grants the award

* :attr:`date` of award

The model also has a :attr:`description` field that can be used to provide more information about the award. 
