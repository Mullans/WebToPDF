import urllib
import urllib2
import re
import string
import cookielib
import time
from urlparse import urlsplit
import os.path
from os import remove
import getpass

#These modules need to be installed. See text file for details.
import pdfkit
import lxml.html
from bs4 import BeautifulSoup


#This determines whether or not the statistics are printed (such as percent done, number to print, number of results, depth, link name, and times)
beQuiet = False

#This determines whether the links on the pdf are active or not
killLinks = True

#This determines whether or not user profiles are printed. Set to false to prevent them from being printed. User names are still currently printed on the pdfs.
getUsers = True

#This determines whether or not students names appear on forums
getStudents = True

#This determines whether or not the extra resources get saved.
getResources = True

#This determines whther or not forums get saved.
getForums = True

#This determines whether or not to get workshop pages
#IMPORTANT: This program is unable to remove students' names from workshop pages
getWorkshops = True

#This determines whether or not to show questionnaires
getQuestionnaires = True

#This determines whether or not to get feedback pages
getFeedback = True

#This determines whether or not to show the scheduler pages
getScheduler = True

#Change this to whatever level of depth you want to go to. This has only been rigorously tested on 1 and 2.
		#1 = mainpage and links 	2 = mainpage, mainpage links, links on the mainpage links
goToDepth = 2

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
    'quiet':''
}

#This adds the link disabling option to options if needed.
if killLinks:
	options['--disable-external-links'] = None
	# options['--load-error-handline ignore'] = None

#These are global variables that get defined later.
folderName = ''
website = ""
viewedLinks = []


#This creates cookies so that you only have to login once.
cookieJar = cookielib.LWPCookieJar()
opener = urllib2.build_opener(
	urllib2.HTTPCookieProcessor(cookieJar),
	urllib2.HTTPRedirectHandler(),
	urllib2.HTTPHandler(debuglevel=0))
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


#This gets the name of the resource (such as the page name or file name).
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

#Either prints the page as a pdf or downloads the resource pointed to by the link.
def printLink(url, localFileName=None):
	#This prevents replying or deleting posts on forums.
	if "forum/post.php?reply=" in url or "forum/post.php?delete" in url:
		return
	#This cleans up the link address to prevent redundant domain names.
	url2 = url.replace(website,"")
	req = urllib2.Request(website+url2,data)
	#This block either opens the webpage or throws an error if there is an issue opening the page.
	try:
		res = opener.open(req)
	except:
		print "opener error"
		print website+url2
		quit()
	html = res.read()
	title = parseTitle(html,url2)
	# try:
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
		if os.path.isfile(os.path.join(folderName, localName)):
			return
		localName = os.path.join(folderName, localName)
		f = open(localName, 'wb')
		f.write(original)
		f.close()
	#Saves the page pointed to by the link as a pdf file.
	else:
		x = 2;
		temp = ''
		#Checks to see if there are other files of the same name, then adds a number at the end of the title to differentiate.
		while os.path.isfile(os.path.join(folderName, title)):
			if x!=2: temp = "("+str(x-1)+")"
			title = title.replace(temp+".pdf","("+str(x)+").pdf")
			x+=1
		#This prevents printing of news forums.
		if "News-forum" in title:
			return

		#Takes out students names and links and replaces them with "Student Name" that links to the moodle homepage.
		if not getStudents:
			reDomain = moodleDomain.replace(".","\.")
			replaceString = '(<a href="'+reDomain+'user/view\.php\?id=)(\d+)(&amp;course=)(\d+)(">)([A-Za-z\'\-]+?\s?[A-Za-z\'\-]+?)(</a>)'
			replaceString2 = '(<a href="'+reDomain+'user/profile.php\?id=)(\d+)" title="View profile">([A-Za-z\'\-]+?\s?[A-Za-z\'\-]+?)</a>'
			html = re.sub(replaceString,'<a href="https://moodle.carleton.edu/">User Name</a>',html)
			html = re.sub(replaceString2,'<a href="https://moodle.carleton.edu" title="View profile">User Name</a>',html)
		
		#writes html to a file, then uses a wkhtmltopdf module to print the file as a pdf
		#-->english--> Prints the page pointed to by the link as a pdf file using a file as an intermediary to maintain unicode.

		tempFile = open(os.path.join(folderName, "temp"),'wb')
		tempFile.write(html)
		tempFile.close()
		tempFile = open(os.path.join(folderName, "temp"),'r')
		title = os.path.join(folderName, title)
		pdfkit.from_file(tempFile,title,options=options)
		tempFile.close()
	# except:

	# 	if len(html)==0:
	# 		#This throws an error if there is no content to the page.
	# 		print "Blank Page Error on",
	# 	else:
	# 		#This is a generic error that occurs if any issues arise in the printing process. 
	# 		#This gets thrown if there are embedded videos in the page.
	# 		print "Issue found on page:",
	# 	print url

#This gets all of the links from the given webpage.
def getLinks(url):
	global viewedLinks
	newList = []
	#This cleans up the web address to prevent redundant domain names. (ie. https://www.carleton.edu/https://www.carleton.edu/~~~~)
	url = url.replace(website,"")
	request = urllib2.Request(website+url,data)
	#This either opens the page or throws an error if there was an issue opening it.
	try:
		connection = opener.open(request)
	except:
		print "Opener error"
		print website+url
		quit()
	html = connection.read()
	#This tries to find links in the page, but fails if the page is not html (ie. is a resource file)
	try:
		soup = BeautifulSoup(html)

		#This line sets it so that only the main section of moodle is looked at. To change it, find the portion of html that you want
		#that looks like <div class="~~~~~"> and replace the "region-content" below with whatever "~~~~~" is in your selection. Using chrome,
		#when you right click on a page and choose inspect element, mousing over portions of the html will highlight the section contained by
		#the div wrapper.
		div = soup.find('div', class_="region-content")
	
		#This iterates through every link that is on the page and appends it to the list.
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
			newList.append(link)
			viewedLinks.append(link)
		return newList
	except:
		return

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

	t = time.time()

	#This pulls the domain name out of the starting page. This syntax does not need to change if you change the starting page.
	siteParse = re.compile('(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*')
	m = re.search(siteParse,startingPage)
	global website
	website = startingPage[:m.span(1)[1]]
	firstLink =  startingPage[m.span(1)[1]:]

	#This adds the starting page to the list of links to print later.
	global viewedLinks
	viewedLinks.append(firstLink)

	urlList = []
	tempList = []
	urlList.append(firstLink)
	#This loops through each level of links, adding more links to the list to print as it goes.
	depth = 0
	while True:
		if not beQuiet:
			print "Depth",depth," Results:",len(urlList)
		for item in urlList:
			try:
				tempList = tempList+getLinks(item)
			except:
				continue
		# This prints how long it took to get the most recent level of links.
		if not beQuiet:
			total = int(time.time()-t)
			t = time.time()
			seconds = total%60
			minutes = total/60
			print "Time to get links:",minutes,"min",seconds,"sec"
		urlList = tempList
		depth+=1
		#This breaks out of the loop is the scraper has reached the desired depth.
		if depth == goToDepth:
			break
		#This breaks out of the loop if there are no more links to open.
		if len(tempList)==0:
			break
		tempList = []
	if not beQuiet:
		print 'To Print:',len(viewedLinks)
	x = 0.0
	y = len(viewedLinks)
	#This iterates through all viewed links and prints them.
	for item in viewedLinks:
		if x>y:
			break
		if not beQuiet:
			print ("%.2f%% completed " % ((x/y)*100)),item
		x+=1
		printLink(item)
	#This prints how long it took to print all of the links.
	if not beQuiet:
		total = int(time.time()-t)
		seconds = total%60
		minutes = total/60
		print "Time to print:",minutes,"min",seconds,"sec"
	x = 0
	#This removes the file that was used to bypass strings.
	try:
		remove('temp')
	except:
		print "couldn't remove temp"
def main():
	courses = []
	#If there is a file called "courses.txt" in the WebToPDF folder, this will get each course listed in there.
	#If there is no such file, this will ask for user input for a course.
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
			courseFolder = courseFolder[:-3]+"("+str(i)+")"
		i+=1
	os.makedirs(courseFolder)
	for item in courses:
		if item[:2]=="**":
			print 'Skipping '+item[2:]
			continue
		global viewedLinks
		viewedLinks = []
		getCourse(item)
main()


