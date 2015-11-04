__author__ = 'sakhar'

from bs4 import BeautifulSoup
import urllib

url = 'http://www.fifa.com/'
html = urllib.urlopen(url).read()
soup = BeautifulSoup(html,"html.parser")

# Remove scripts
for script in soup(["script", "style"]):
    script.extract()
text = soup.get_text()

print text