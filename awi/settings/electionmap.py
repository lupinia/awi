#	Lupinia Studios
#	By Natasha L.
#	www.lupinia.net | github.com/lupinia
#	
#	=================
#	Django Settings File - Election Map
#	Settings for the SL election map supporting infrastructure
#	=================

ELECTION_PARTIES = (
	('I', 'Other/Independent'),
	('D', 'Democratic'),
	('R', 'Republican'),
	('d', 'Ind. (Dem Caucus)'),
	('r', 'Ind. (GOP Caucus)'),
	('X', 'Runoff'),
)

SENATE_CLASSES = (
	(0, 'None'),
	(1, 'Class 1'),
	(2, 'Class 2'),
	(3, 'Class 3'),
)
