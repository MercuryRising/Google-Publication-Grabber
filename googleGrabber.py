from bs4 import BeautifulSoup
import requests
import time
import os

'''
This module will download Google's pdf publications.
Their website is really awesome, and they have tons
of open research, which is great. 
This script only grabs the content that is hosted on
their website, (it looks for links with the pdf-tooltip
class). 

'''


delay = .25 # delay time between downloading articles
totalSize = 0

base = "http://research.google.com"

def downloadArticles(url):
  global totalSize

  link = base + url
  print link

  r = requests.get(link)
  soup = BeautifulSoup(r.text)

  # Text string without quotes of the research area  
  researchArea = url.split("/")[-1].split('.')[0]

  # find the unordered list on the website that contains
  # all the publications
  publicationList = soup.find("ul", {"class":"pub-list"})

  # The publications are segmented in list elements
  # containing the urls, authors, and title.
  for li in publicationList.find_all("li"):
    
    # Sleep a little bit to be nice
    time.sleep(delay)

    # Many links have external sources, and they will fail when
    # trying to access the 'href' of the publication.
    try:
      
      # We look for links in our list with the class 'pdf-icon' and
      # grab the href for it.
      pdfUrl = li.find("a", {"class":"pdf-icon tooltip"})['href']

      # Find the publication title, get text for it and strip the whitespace
      # around the edges (there will still be some on the inside)
      title = li.find("p", {"class":"pub-title"}).get_text().strip()
      
      # Get the PDF itself
      r = requests.get("http://research.google.com"+pdfUrl)
      
      # We will sort the pdfs depending on the research area
      # We will title them the same as on the website
      filePath = "./googlePubs/"+researchArea+"/"+title+".pdf"
      
      # Open a file that we can write to and write the PDF content
      with open(filePath, "wb") as f:
        f.write(r.content)
  
      # See how much data we've downloaded      
      totalSize += int(r.headers['content-length'])

      # Ready for the next one
      print '[X] Done writing ' + title
    
    except:
      # We could do something here where we would log the
      # publications that we couldn't download
      pass


# This is the link where all the paper's categories reside
url = "http://research.google.com/pubs/papers.html"

r = requests.get(url)

# Turn the text of the request into a soup
soup = BeautifulSoup(r.text)

# Look for the list of research areas
researchAreas = soup.find("li", {"id":"ra"})

raLinks = []

try:
  os.mkdir("./googlePubs")
except:
  raise  
  "failed to make directory..."
   
# The first link is a link back to itself (that's why we look from [1:])
for link in researchAreas.find_all('a')[1:]:

    # Link for specific research areas    
    raLink = link['href']
    
    # The research area name is .../AREA.html, we want just AREA
    researchArea = raLink.split("/")[-1].split('.')[0]
    # We'll try to make the directory, if not that means it's there and we can
    # keep going (if the script fails halfway through or something
    try:
      os.mkdir("./googlePubs/"+researchArea)
    except:
      print "Couldn't make directory : ./googlePubs/", researchArea
      pass  
    
    # Call the download articles function with links to different research areas 
    downloadArticles(raLink)

# When we're done, we'll print how much data we downloaded.
print "Total size : %s Mb" %(totalSize/1000)




