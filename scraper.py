########################################
# Scraper for play-by-play NCAA men's basketball data from ESPN.
# Downloads game data and formats it to be dumped into a
# database elsewhere.
#
# Author: jesse.gunsch@gmail.com
#

import urllib
from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select

# Download game data.
soup = Soup(urllib.urlopen('http://espn.go.com/ncb/playbyplay?gameId=323600012'))

game_data = []

########################
# HTML scraping here. Hopefully they don't change their format too much.
rows = select(soup, '.mod-content tr')

# Increments as we go. 0 = first half, 1 = second half, 2+ = overtime periods
game_segment = 0
previous_remaining_time = 100000

# Split up meaningful parts of HTML rows. Get into a representation independent
# of artifacts of being on the page.
for row in rows:
  cells = select(row, 'td[valign=top]')
  if len(cells) == 4:
    remaining_time, away_action, score, home_action = [
      cell.text.replace('&nbsp;', ' ').strip() for cell in cells
    ]
    minutes, seconds = remaining_time.split(':')
    remaining_time = int(minutes) * 60 + int(seconds)

    if remaining_time > previous_remaining_time: 
      game_segment = game_segment + 1

    away_score, home_score = map(int, score.split('-'))

    game_data.append({
      'time': remaining_time,
      'segment': game_segment,
      'away_action': away_action,
      'away_score': away_score,
      'home_action': home_action,
      'home_score': home_score,
    })

    previous_remaining_time = remaining_time

# TODO Actual processing.
for data in game_data:
  print data
