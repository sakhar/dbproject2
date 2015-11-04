__author__ = 'sakhar'

from bs4 import BeautifulSoup
import urllib

url = 'http://www.fifa.com/'
html = urllib.urlopen(url).read()

version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

soup = BeautifulSoup(html,"html.parser")

# Remove scripts
for script in soup(["script", "style"]):
    script.extract()
text = soup.get_text()

print text