WebToPDF
-A python program made by Sean Mullan to archive courses off of the Carleton College Moodle site


Contents:
	The WebToPDF folder must contain these items in order to function: 
		WebToPDF.py
		README.txt
		bs4
		pdfkit
		pdfkit-0.4.1-py2.7.egg-info
		wkhtmltox-0.12.1_osx-carbon-i386.pkg
		[NOTE: wkhtml version from 6-27-2014, updates available at http://wkhtmltopdf.org/downloads.html]

Set-Up Instructions (For Mac OSX):
	[NOTE: Python should come installed on OSX]
	[NOTE: These instructions only need to be followed once on a machine.]
	Install wkhtml using the .pkg included in the WebToPDF file.
	Open Terminal
	Type in these instructions one line at a time:
		sudo easy_install pip
		export CFLAGS=-Qunused-arguments
		export CPPFLAGS=-Qunused-arguments
		sudo -E pip install lxml
		[IF THIS FAILS: type in: export ARCHFLAGS='-arch i386 -arch x86_64' and try again]
	[NOTE: These commands install pip (an installer) and lxml (a python module)]
	[NOTE: you need to be on the admin account and have the password to use the sudo commands]
	
How To Use (Single Course):
	Go to Terminal and type in “cd “, drag the WebToPDF folder into the Terminal window and hit enter.
	[NOTE: The space after cd is important]
	Type in “python WebToPDF.py” and hit enter
	Type in your username and then password when prompted.
	When prompted, type in the short form of the class to scrape.
	[NOTE: That is the format class-section-term ie. cs257-00-s14 for spring 2014 software design]
	Do not delete the file “temp” that appears while the program is running. It will remove itself.
	[NOTE: The option to type in a course name will not be presented if there is a file called courses.txt
	in the same folder.]

How To Use (Multiple Courses):
	Make a new .txt file called “courses.txt” in the WebToPDF folder with all of the courses’ short names that
	you want to save on separate lines with no punctuation.
	Follow the above steps for a single course.
	[NOTE:If the program still asks for the short name of the class, make sure that the file is saved in the
	right location and is saved as “courses.txt”]
	[NOTE:The program runs through one class at a time, so the percentages reflect only the current class.]
	[NOTE:You can make the program skip a course by adding two asterisks before it in the courses.txt
	folder. (ie. **cs257-00-s14 will be skipped)]
	[NOTE:For courses that end up with strange errors (squished headers, etc.) add !! in front of the course
	name in the courses.txt file to use the standard Moodle css]
	
Output:
	The files will be stored into a subdirectory of the WebToPDF folder titled “courses”.
	Inside of the “courses” folder, each course will get its own self-titled folder.
	[NOTE: Titled using the short form of the course name.]
	Inside of these, the pdf of the main page will be in the main folder.
	Links that were on the page will be printed into folders titled with the name of the section in the main page
	that they were on.
	At depths higher than 1, further links will be in folders with the same title as the link that was followed to
	find the deeper links.
	[NOTE: If multiple items have the same title in the same folder, later versions will get a number after to identify them.]
	When looking at the output, use either the “Date Added” or “Date Modified” sorters in the Finder view window.
	Output files/folders are sorted in order they were in on the page.
	[NOTE: folders will immediately follow the related file.]	
	If multiple resources have the same name, the program assumes that they are the same resource, and only prints
	the first one.

Options:
	There are several options near the top of the WebToPDF.py file that can be changed:
		[NOTE: Capitalization is needed for False and True]
		beQuiet: Determines whether or not statistics are printed as the program runs.
		(such as percent done, number to print, number of results, depth, link name, and times).
		[NOTE: The times displayed are the times from the start, not the lengths of each process.]
		killLinks: This determines whether or not links on the pdf are active. Change to 
			False to enable the links.
		[NOTE: When active, the links will point to the moodle server, not to the other pdfs.]
		getUsers: Determines whether or not student/user profiles are printed.	
		getStudents: If this is false, it changes all of the students’ names in forums to
			“Student Name” and changes the link to the Moodle home page.
		[NOTE: This only works for names that Moodle generates. If the professor types in the student's name, the
		program will not be able to remove it.]
		getResources: Determines whether or not resources (.docx, .pdf, .pptx, etc.) are printed.
		getForums: Determines whether or not forums are included.
		getWorkshops: Currently set to False. Change to True to get workshop pages.
		[NOTE: The program is unable to remove student names from workshop pages, and these pages often show grades.]
		getQuestionnaires: Determines whether or not questionnaire pages are printed.
		getFeedback: Determines whether or not feedback pages are printed.
		getScheduler: Determines whether or not scheduler pages are printed.
		goToDepth: This defines how deep the program goes into the site.
			1 = Course Main Page and Links from the Main Page
			2 = Course Main Page, Links from the Main Page, and Links from those Links
		loginPage: Currently set to 'https://moodle2013-14.carleton.edu/login/index.php'. This is the page the 
			program goes to to login. This needs to be set to the same year as the moodleDomain.
		moodleDomain: Currently set to ‘https://moodle2013-14.carleton.edu/'. This is the domain that the
			program uses to determine the validity of links.

	There is also an array called options that has multiple values that determine the page layout of the printed pdf’s.
	The first five can be changed to alter the size and margins of the printed pdf’s, but the last three should be left
	alone.