import urllib
import urllib2
import re
import string
import cookielib
import time
from urlparse import urlsplit
import os.path
import getpass

#This module needs to be installed. See README.txt for details
import lxml.html

#These modules need to be present in the folder. See text file for details.
import pdfkit
from bs4 import BeautifulSoup

#This determines whether or not the statistics are printed (such as percent done, number to print, number of results, depth, link name, and times)
beQuiet = False

#This determines whether the links on the pdf are active or not
killLinks = True

#This determines whether or not user profiles are printed. Set to false to prevent them from being printed. User names are still currently printed on the pdfs.
getUsers = False

#This determines whether or not students names appear on forums
getStudents = False

#This determines whether or not the extra resources get saved.
getResources = False

#This determines whther or not forums get saved.
getForums = False

#This determines whether or not to get workshop pages
#IMPORTANT: This program is unable to remove students' names from workshop pages
getWorkshops = False

#This determines whether or not to show questionnaires
getQuestionnaires = False

#This determines whether or not to get feedback pages
getFeedback = False

#This determines whether or not to show the scheduler pages
getScheduler = False

#This lets you determine whether to get html versions of the webpages as well
saveHTML = True

#Change this to whatever level of depth you want to go to. This has only been rigorously tested on 1 and 2.
		#1 = mainpage and links 	2 = mainpage, mainpage links, links on the mainpage links
goToDepth = 1

#This is the page that you have to login from. Change it to change the version of Moodle used.
loginPage = 'https://moodle2013-14.carleton.edu/login/index.php'

#This is the domain that will be used. Change it to change the version of Moodle used.
moodleDomain = 'https://moodle2013-14.carleton.edu/'

#These are the options that can be set for the printed pdfs. Quiet just decreases the text printed to the terminal window.
options = {
	'page-size': 'Letter',
	'margin-top': '0.75in',
	'margin-right': '0.75in',
	'margin-bottom': '0.75in',
	'margin-left': '0.75in',
	#Do not change these three options
	'encoding': "UTF-8",
	'no-outline': None,
	'quiet':'',
	'--javascript-delay':'100'
}

#This adds the link disabling option to options if needed.
if killLinks:
	options['--disable-external-links'] = None


#These are global variables that get defined later.
folderName = ''
courseFolder = ''
courseName = ''
website = ""
viewedLinks = []
totalFiles = []
num = 0
tempnum = 0
restyleCourse = False

#This creates cookies so that you only have to login once.
cookieJar = cookielib.LWPCookieJar()
opener = urllib2.build_opener(
	urllib2.HTTPCookieProcessor(cookieJar),
	urllib2.HTTPRedirectHandler(),
	urllib2.HTTPHandler(debuglevel=0))
#Currenly set to look at the webpages as Safari
# opener.addheaders = [('User-agent', "Safari/536.28.10")]
opener.addheaders = [('User-agent', "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36")] 

#This gets the user information and logs in to Moodle.
username = raw_input("username:")
password = getpass.getpass("password:")
forms = {"username": username ,
		 "password": password
		}
data = urllib.urlencode(forms)
req1 = urllib2.Request(loginPage,data)
opener.open(req1)

#This section removes all empty folders from all levels of the directory that is entered.
def cleanUp(folder):
	list = os.listdir(folder)
	#This checks all the files in the entered directory.
	for item in list:
		next = os.path.join(folder,item)
		#Checks all of the subdirectories in the main directory.
		if os.path.isdir(next):
			#Removes the subdirectory if it is empty.
			if os.listdir(next) == []:
				os.rmdir(next)
				if not beQuiet:
					print "Removing empty directory:",next
			#If it was not empty, this runs cleanUp() recursively on the subdirectory.
			else:
				cleanUp(next)
	#This checks to see if the folder is empty now that all of its subdirectories have been checked.
	if os.listdir(folder)==[]:
		os.rmdir(folder)
		if not beQuiet:
			print "Removing empty directory:",folder

#This gets the title based on the webpage.
def parseTitle(htmlString,url):
	regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
	try:
		title =  regex.search(htmlString).group(1)
	except:
		regex = re.compile('TITLE (.*)\n')
		try:
			title = regex.search(htmlString).group(1)
		except:
			#This sets the title to be the url if there is no title set by the page itself.
			title = '*'+url.replace("/","-")
			title = title.replace("--","-")
	title = title.replace('.','')
	for c in string.punctuation:
		title = title.replace(c,'')
	title = title.replace(" ","-")+'.pdf'
	return title

def printLink(sectionName, url,depth, localFileName=None):
	global viewedLinks
	if url in viewedLinks:
		return
	else:
		viewedLinks.append(url)
	#This prevents replying or deleting posts on forums.
	if "forum/post.php?reply=" in url or "forum/post.php?delete" in url or 'delete' in url:
		return
	#This cleans up the link address to prevent redundant domain names.
	url2 = url.replace(website,"")
	if not beQuiet: print '\t'*depth,url2
	req = urllib2.Request(website+url2,data)
	#This block either opens the webpage or throws an error if there is an issue opening the page.
	try:
		res = opener.open(req)
	except:
		print "opener error"
		print website+url2
		return
	html = res.read()
	try:
		original = html
		#This if statement checks if this is a resource to download, then saves it as the original format.
		if res.info().has_key('Content-Disposition'):
			if not getResources:
				return
			# If the response has a Content-Disposition, we take the file name from it.
			localName = res.info()['Content-Disposition'].split('filename=')[1]
			if localName[0] == '"' or localName[0] == "'":
				localName = localName[1:-1]
			elif res.url != url: 
				# If we were redirected, the real file name we take from the final URL.
				localName = os.path.basename(urlsplit(res.url)[2])
			if localFileName: 
				# If the user added a localFileName argument when calling printLink(), this uses that instead of the innate name.
				localName = localFileName
			#If the resource has been downloaded elsewhere, skip it
			if os.path.isfile(os.path.join(sectionName, localName)):
				return
			localName = '('+courseName+') '+localName
			localName = os.path.join(sectionName, localName)
			f = open(localName, 'wb')
			f.write(original)
			f.close()
			return
		#Saves the page pointed to by the link as a pdf file.
		else:
			title = parseTitle(html,url2)
			title = '('+courseName+') '+title
			x = 2;
			temp = ''
			#Checks to see if there are other files of the same name, then adds a number at the end of the title to differentiate.
			while os.path.isfile(os.path.join(sectionName, title)):
				if x!=2: temp = "("+str(x-1)+")"
				title = title.replace(temp+".pdf","("+str(x)+").pdf")
				x+=1
			#This prevents printing of news forums.
			if "News-forum" in title:
				return

			#Takes out students names and links and replaces them with "Student Name" that links to the moodle homepage.
			#Note: This only works with names generated by Moodle. If a professor entered the students name as part of other text,
			#this will not be able to see it.
			html2 = html
			if restyleCourse == True:
				styleFinder = '(<link rel="stylesheet")(.*)'
				html = re.sub(styleFinder,'<link rel="stylesheet" type="text/css" href="https://moodle2013-14.carleton.edu/theme/yui_combo.php?3.7.3/build/cssreset/reset-min.css&amp;3.7.3/build/cssfonts/fonts-min.css&amp;3.7.3/build/cssgrids/grids-min.css&amp;3.7.3/build/cssbase/base-min.css" /><script type="text/javascript" src="https://moodle2013-14.carleton.edu/theme/yui_combo.php?3.7.3/build/simpleyui/simpleyui-min.js&amp;3.7.3/build/loader/loader-min.js"></script><script id="firstthemesheet" type="text/css">/** Required in order to fix style inclusion problems in IE with YUI **/</script><link rel="stylesheet" type="text/css" href="https://moodle2013-14.carleton.edu/theme/styles.php/formal_white_carleton/1396903531/all" />',html)

			if not getStudents:
				reDomain = moodleDomain.replace(".","\.")
				replaceString = '(<a href="'+reDomain+'user/view\.php\?id=)(\d+)(&amp;course=)(\d+)(">)([A-Za-z\'\-]+?\s?[A-Za-z\'\-]+?)(</a>)'
				replaceString2 = '(<a href="'+reDomain+'user/profile.php\?id=)(\d+)" title="View profile">([A-Za-z\'\-]+?\s?[A-Za-z\'\-]+?)</a>'
				html = re.sub(replaceString,'<a href="https://moodle.carleton.edu/">User Name</a>',html)
				html = re.sub(replaceString2,'<a href="https://moodle.carleton.edu" title="View profile">User Name</a>',html)
			#writes html to a file, then uses a wkhtmltopdf module to print the file as a pdf
			#-->english--> Prints the page pointed to by the link as a pdf file using a file as an intermediary to maintain unicode.
			if saveHTML:
				global tempnum
				tempnum+=1
				htmlname = title.replace(".pdf","")
				htmlname = htmlname+'.html'
				tempFile2 = open(os.path.join(sectionName, htmlname),'wb')
				tempFile2.write(html2)
				tempFile2.close()
			tempname = "temp"
			tempFile = open(os.path.join(sectionName, tempname),'wb')
			tempFile.write(html)
			tempFile.close()
			tempFile = open(os.path.join(sectionName, tempname),'r')
			title = os.path.join(sectionName, title)
			pdfkit.from_file(tempFile,title,options=options)
			tempFile.close()
			os.remove(os.path.join(sectionName, "temp"))

			return title

	except:
		if len(html)==0:
			#This throws an error if there is no content to the page.
			print "Blank Page Error on",
		else:
			#This is a generic error that occurs if any issues arise in the printing process. 
			#This gets thrown if there are embedded videos in the page.
			print "Issue found on page:",
		print url

def getLinks(sectionName, link, depth):
	# This prints the first link.
	depth = depth+1
	newSectionName = printLink(sectionName,link,depth)
	i=2
	if newSectionName == None:
		return

	# splitUp = newSectionName.split('/')
	# print '('+courseName+')'+'-'+splitUp[len(splitUp)-1]
	# splitUp[len(splitUp)-1] = '('+courseName+')'+'-'+splitUp[len(splitUp)-1]
	# print '/'.join(splitUp)
	# newSectionName = '/'.join(splitUp)
	
	newSectionName = os.path.splitext(newSectionName)[0]
	while os.path.exists(newSectionName):
		if i==2: 
			newSectionName = newSectionName+"("+str(i)+")"
		else:
			newSectionName = newSectionName[:-3]+"("+str(i)+")"
		i+=1
	request = urllib2.Request(link)

	try:
		connection = opener.open(request)
	except:
		print "Opener error"
		print link
		return
	html = connection.read()
	soup = BeautifulSoup(html)
	div = soup.find('div',class_="region-content")
	if div == None:
		return
	if len(div.findAll('a',href=True))==0:
		print len(div.findAll('a',href=True))
		return
	os.makedirs(newSectionName)
	for tag in div.findAll('a', href=True):
			link = tag['href']
			#This prevents using a reply or delete link and messing up a forum, logging out the current session, opening redundant forum links, or
			#opening links to other pages disguised as moodle links. 
			if '/url/' in link or '&' in link or 'action=grading' in link or "forum/post.php?reply=" in link or "forum/post.php?delete" in link or 'logout' in link or 'parent' in link or "edit" in link or "/subscribe" in link or '/message/' in link:
				continue
			if '/scheduler/' in link and not getScheduler:
				continue;
			if '/feedback/' in link and not getFeedback:
				continue
			if '/questionnaire/' in link and not getQuestionnaires:
				continue
			if '/workshop/' in link and not getWorkshops:
				continue;
			if "/forum/" in link and not getForums:
				continue
			#This skips links to other domains that aren't Moodle. 
			#This will also prevent going between versions of Moodle. So if you start on a moodle2013-14 page, you won't get links leading to a moodle2012-13 page.
			if (link[0]!='/' and website not in link):
				continue
			#This skips links that have already been stored in viewed links.
			if link in viewedLinks or link+'/' in viewedLinks:
				continue
			#Some forums were linked to several times with only a # and a 6 digit code differentiating them. This prevents that.
			if '#p' in link:
				continue
			if not getUsers:
				if 'user/view' in link or '/user/' in link:
					continue
			if goToDepth>depth:
				getLinks(newSectionName,link, depth)
			else:
				printLink(newSectionName,link,depth)
	

			
	


def getCourse(courseName):
	#This sets up first page and creates a directory to store the results.
	global folderName
	folderName = os.path.join(courseFolder,courseName)
	i = 2
	#This prevents redundant folder names.
	while os.path.exists(folderName):
		if i==2: 
			folderName = folderName+"("+str(i)+")"
		else:
			folderName = folderName[:-3]+"("+str(i)+")"
		i+=1
	os.makedirs(folderName)
	#This uses the moodle shortcut to get the starting page.
	startingPage = moodleDomain+'go/'+courseName
	#This pulls the domain name out of the starting page. This syntax does not need to change if you change the starting page.
	siteParse = re.compile('(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*')
	m = re.search(siteParse,startingPage)
	global website
	website = startingPage[:m.span(1)[1]]
	firstLink =  startingPage[m.span(1)[1]:]

	#This adds the starting page to the list of links to print later.
	global viewedLinks
	viewedLinks.append(firstLink)

	if not beQuiet:
		print website+firstLink

	request = urllib2.Request(website+firstLink,data)

	try:
		connection = opener.open(request)
	except:
		print "Opener error"
		print website+url
		return
	html = connection.read()
	soup = BeautifulSoup(html)

	div = soup.find('div',class_="region-content")
	sectionSplit = div.findAll('li',class_="section main clearfix")
	
	totalLinks = len(div.findAll('a',href=True))
	linkCounter = 0.0
	if not beQuiet:
		print "To Print:",totalLinks
	t = time.time()
	printLink(folderName,website+firstLink,0)
	sectionNumber = 1
	for section in sectionSplit:
		titleHTML = section.find('h3',class_="sectionname")
		if titleHTML==None:
			title = "Top Section"
		else:
			try:
				title = titleHTML.string
			except:
				title = section+str(sectionNumber)
		title = '('+courseName+') '+title
		sectionNumber+=1
		if not beQuiet:
			print '\n\n',courseName,"  ",title,"\n*******************************************"

		#This section gets the links from the week section.
		sectionName = os.path.join(folderName,title)
		i = 2
		#This prevents redundant folder names.
		while os.path.exists(sectionName):
			if i==2: 
				sectionName = sectionName+"("+str(i)+")"
			else:
				sectionName = sectionName[:-3]+"("+str(i)+")"
			i+=1
		os.makedirs(sectionName)
		for tag in section.findAll('a', href=True):
			link = tag['href']
			#This prevents using a reply or delete link and messing up a forum, logging out the current session, opening redundant forum links, or
			#opening links to other pages disguised as moodle links. 
			if '/url/' in link or '&' in link or 'action=grading' in link or "forum/post.php?reply=" in link or "forum/post.php?delete" in link or 'logout' in link or 'parent' in link or "edit" in link or "/subscribe" in link or '/message/' in link:
				continue
			if '/scheduler/' in link and not getScheduler:
				continue;
			if '/feedback/' in link and not getFeedback:
				continue
			if '/questionnaire/' in link and not getQuestionnaires:
				continue
			if '/workshop/' in link and not getWorkshops:
				continue;
			if "/forum/" in link and not getForums:
				continue
			#This skips links to other domains that aren't Moodle. 
			#This will also prevent going between versions of Moodle. So if you start on a moodle2013-14 page, you won't get links leading to a moodle2012-13 page.
			if (link[0]!='/' and website not in link):
				continue
			#This skips links that have already been stored in viewed links.
			if link in viewedLinks or link+'/' in viewedLinks:
				continue
			#Some forums were linked to several times with only a # and a 6 digit code differentiating them. This prevents that.
			if '#p' in link:
				continue
			if not getUsers:
				if 'user/view' in link or '/user/' in link:
					continue
			if goToDepth>1:
				getLinks(sectionName,link, 0)
			else:
				printLink(sectionName,link,0)
				linkCounter+=1.0
				if not beQuiet:
					print ("%.2f%% completed " % ((linkCounter/totalLinks)*100)),link
	total = int(time.time()-t)
	seconds = total%60
	minutes = total/60
	if not beQuiet:
		print 'Time to Print Links:',minutes,"min",seconds,"sec"
			

def main():
	courses = []
	#If there is a file called "courses.txt" in the WebToPDF folder, this will get each course listed in there.
	#If there is no such file, this will ask for user input for a course.
	global courseName
	try:
		courses = [line.strip() for line in open('courses.txt')]
	except:
		courseName = raw_input("Short course name:")
		courses.append(courseName)
	global courseFolder
	courseFolder = 'courses'
	i = 2
	while os.path.exists(courseFolder):
		if i==2: 
			courseFolder = courseFolder+"("+str(i)+")"
		else:
			if i<11:
				courseFolder = courseFolder[:-3]+"("+str(i)+")"
			else:
				courseFolder = courseFolder[:-4]+'('+str(i)+')'
		i+=1
	os.makedirs(courseFolder)
	for item in courses:
		if item[:2]=="**":
			# print 'Skipping '+item[2:]
			continue
		global restyleCourse
		if item[:2]=="!!":
			restyleCourse = True
			item = item[2:]
		courseName = item
		getCourse(item)
		restyleCourse = False
timer = time.time()
main()
cleanUp(courseFolder)
if not beQuiet:
	os.system("say 'Courses Printed'")
	total = int(time.time()-timer)
	seconds = total%60
	minutes = total/60
	hours = total/3600
	print 'Total time for courses:',hours,'hr',minutes,"min",seconds,"sec"
