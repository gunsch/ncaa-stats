import urllib
from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select

soup = Soup(urllib.urlopen('http://espn.go.com/ncb/playbyplay?gameId=323600012'))
rows = select(soup, '.mod-content tr')

gamedata = []

for row in rows:
	cells = select(row, 'td[valign=top]')
	if len(cells) == 4:
		gamedata.append([cell.text for cell in cells])

print gamedata