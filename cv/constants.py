## Tuple of publication status choices
INPREP_STATUS = 0
WORKING_STATUS = 1
SUBMITTED_STATUS = 20
REVISE_STATUS = 30
RESUBMITTED_STATUS = 35
CONDACCEPT_STATUS = 40
FORTHCOMING_STATUS = 50
INPRESS_STATUS = 55
PUBLISHED_STATUS = 60
RESTING_STATUS = 99
PUBLICATION_STATUS = (
		(INPREP_STATUS,'In preparation'),
		(WORKING_STATUS,'Working paper'),
		(SUBMITTED_STATUS,'Submitted'),
		(REVISE_STATUS,'Revise'),
		(RESUBMITTED_STATUS,'Resubmitted'),
		(CONDACCEPT_STATUS, 'Conditionally accepted'),
		(FORTHCOMING_STATUS,'Forthcoming'),
		(INPRESS_STATUS, 'In press'),
		(PUBLISHED_STATUS,'Published'),
		(RESTING_STATUS,'Resting')
		)

## Tuple of student level choices
UNDERGRAD = 0
MASTERS = 10
DOCTORAL = 20
STUDENT_LEVELS =(
	(UNDERGRAD, 'Undergraduate student'),
	(MASTERS,   'Masters student'),
	(DOCTORAL,  'Doctoral student')
	)

## Tuple of different types of services performed
DEPARTMENT_SERVICE = 10
SCHOOL_SERVICE     = 20
UNIVERSITY_SERVICE = 30
DISCIPLINE_SERVICE = 40
COMMUNITY_SERVICE  = 60
OTHER_SERVICE      = 90
SERVICE_TYPES = (
	(DEPARTMENT_SERVICE,'Department'),
	(SCHOOL_SERVICE, 'School or College'),
	(UNIVERSITY_SERVICE,'University-wide'),
	(DISCIPLINE_SERVICE,'Discipline'),
	(COMMUNITY_SERVICE,'Community'),
	(OTHER_SERVICE,'Other')
	)

