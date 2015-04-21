#!/usr/bin/env python

'''
Keith Murray
Read in a list of cities from file
for each city, find country, Latitude, Longitude
save data into new file

on URL: it will take the top result and only top result

Example for search omaha:
<tr>
 <td>
  <small>1
  </small> 
  <a href="http://www.geonames.org/5074472/omaha.html">
     <img src="/maps/markers/m10-WHITE-P.png" 
     border="0" alt="P"></a>
  </td><td>
   <a href="/maps/google_41.259_-95.938.html">Omaha</a>
   &nbsp;&nbsp;
   <a href="http://en.wikipedia.org/wiki/Omaha%2C_Nebraska">
   <img src="/img/20px-Wikipedia-logo.png" width="15" border="0" alt="wikipedia article"></a>
   <br>

     <span class="latitude">41.2586096</span>
     <span class="longitude">-95.937792</span>
     </span></td><td>
     <a href="/countries/US/united-states.html">United States</a>
     , Nebraska<br><small>Douglas County</small>





'''
import urllib2 


def checkNCBI(geneID):
    target_url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + str(geneID) + "&report=docsum&format=text"
    geneInfo = []
    for line in urllib2.urlopen(target_url):
	if (line[0] != "<"):
	    #print line.strip()
	    geneInfo.append(line.strip())
    #print len(geneInfo)
    #print geneInfo
    return geneInfo

def parseHit(line):
    line = line.split("<")
    hrefStuff = []
    locStuff = []

    fullData = []
    city = ''
    nation = ''
    wiki = ''
    latitude = ''
    longitude = ''

    for i in range(len(line)):
	if line[i][0:7] =="a href=" :
	    hrefStuff.append(line[i])
	    #print str(line[i])
	if line[i][0:11] == "span class=":
	    locStuff.append(line[i])
	    #print str(line[i])

    #print hrefStuff
    for i in range(len(hrefStuff)):
	# href has City, Nation, and Wiki
	dat = hrefStuff[i].split('/')
	if dat[1] =="":
	    # it's a url to geonames or wiki
	    if dat[2] == 'en.wikipedia.org':
		wiki = hrefStuff[i].split('"')
		wiki = wiki[1]
	elif dat[1] == 'maps':
	    # it's the city name
	    city = hrefStuff[i].split('>')
	    city = city[1]
	elif dat[1] == 'countries':
	    # it's the city name
	    nation = hrefStuff[i].split('>')
	    nation = nation[1]
	#print (dat)

    for i in range(len(locStuff)):
	# locStuff has Lat and Long
	dat = locStuff[i].split('"')
	if dat[1] == "latitude":
	    latitude = locStuff[i].split('>')
	    latitude = latitude[1]
	elif dat[1] == "longitude":
	    longitude = locStuff[i].split('>')
	    longitude = longitude[1]
	#print dat

    #print city, nation, wiki, latitude, longitude
    return [city.strip(), nation.strip(), wiki.strip(), latitude.strip(), longitude.strip()]

def geonamesParse(city):
    target_url = "http://www.geonames.org/search.html?q=" + str(city)
    target_string = '<tr><th></th><th>Name</th><th>Country</th><th>Feature class</th><th>Latitude</th><th>Longitude</th></tr>'
    brace = False
    for line in urllib2.urlopen(target_url):
	if brace == True:
	    #print "hi"
	    #print line
	    dbInfo = parseHit(line)
	    brace = False 
	if line[0:30] == target_string[0:30]:
	    brace = True
	#print line
    



    return dbInfo#[city="", country="", latitude="", longitude="", wikiURL]

def main(infile, outfile):
    inf = open(infile, 'r')
    ouf = open(outfile, 'w')
    err = open("FailedCities.txt", 'w')
    #log = open("RUNLOG.txt", 'w')
    for line in inf:
	city = line.split('\t')
	city = city[0]
	city = city.strip()
	city = city.replace(' ', '+')
	dbInfo = []
	try:
	    dbInfo = geonamesParse(city)
	except:
	    err.write(str(city))
	    err.write('\n')
	    print "\tERRROR:\t", city
        if len(dbInfo) > 0:
	    for i in range(len(dbInfo)):
		ouf.write(str(dbInfo[i]))
		ouf.write('\t')
	    ouf.write('\n')
    inf.close()
    ouf.close()
    err.close()
    return

def getSpaceCount(cityfile):
    inf = open(cityfile, 'r')
    maxSpace = 0
    for line in inf:
	city = line.split('\t')
	city = city[0]
	spaces = len(city.split(' '))
	if spaces > maxSpace:
	    maxSpace = spaces
	    thatCity = city
	    print city

    print maxSpace, thatCity
    return
    

infile = "listOfCities100000PlusPeople.txt"
outfile = "extendedCityDatabase.txt"
#main(infile, outfile)

getSpaceCount(outfile)

#geonamesParse('Zhengzhou')





