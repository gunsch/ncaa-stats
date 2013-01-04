########################################
# Scraper for play-by-play NCAA men's basketball data from ESPN.
# Downloads game data and formats it to be dumped into a
# database elsewhere.
#
# Author: jesse.gunsch@gmail.com
#

from BeautifulSoup import BeautifulSoup as Soup
from collections import defaultdict
from soupselect import select
import difflib
import re
import urllib

re_flags = re.I

def get_seconds(time_string):
  minutes, seconds = remaining_time.split(':')
  return int(minutes) * 60 + int(seconds)

def closest(word_list, word):
  return difflib.get_close_matches(word, word_list, 1, 0.3)[0]

# Download game data.
soup = Soup(urllib.urlopen('http://espn.go.com/ncb/playbyplay?gameId=330030012'))

game_data = []

########################
# HTML scraping here. Hopefully they don't change their format too much.
title = select(soup, 'title')[0].text

away_team, home_team, date = re.search(r'^(.*?) vs\. (.*?) - Play by Play - (.*?) -', title).groups()
team_names = [away_team, home_team]

rows = select(soup, '.mod-content tr')

# Increments as we go. 0 = first half, 1 = second half, 2+ = overtime periods
game_segment = 0
previous_remaining_time = 100000

# Split up meaningful parts of HTML rows. Get into a representation independent
# of artifacts of being on the page.
for row in rows:
  cells = select(row, 'td')
  if len(cells) == 4:
    remaining_time, away_action, score, home_action = [
      cell.text.replace('&nbsp;', ' ').strip() for cell in cells
    ]
    remaining_time = get_seconds(remaining_time)

    away_score, home_score = map(int, score.split('-'))

    if not away_action and not home_action:
      continue

    game_data.append({
      'time': remaining_time,
      'segment': game_segment,
      'away_action': away_action,
      'away_score': away_score,
      'home_action': home_action,
      'home_score': home_score,
    })

  elif len(cells) == 2:
    remaining_time, action = [
      cell.text.replace('&nbsp;', '').strip() for cell in cells
    ]
    remaining_time = get_seconds(remaining_time)

    if 'End of' in action:
      game_segment = game_segment + 1

    timeout = re.search('^(.*) full timeout\.$', action, re_flags)
    if timeout:
      team = closest(team_names, timeout.groups()[0])
      timeout_event = {
        'time': remaining_time,
        'segment': game_segment,
        'away_action': '',
        'home_action': '',
      }
      if team == away_team:
        timeout_event['away_action'] = 'Full Timeout'
      else:
        timeout_event['home_action'] = 'Full Timeout'

      game_data.append(timeout_event)


############################################################
# Turn game events into a more structured representation.

# This should mirror the player-game table structure.
players = defaultdict(lambda: {
  '2pa': 0,
  '2pm': 0,
  '3pa': 0,
  '3pm': 0,
  'fta': 0,
  'ftm': 0,
  'oreb': 0,
  'dreb': 0,
  'points': 0,
  'fouls': 0,
  'turnovers': 0,
  'steals': 0,
  'assists': 0,
  'blocks': 0,
})

def inc(player, stat, amt=1):
  players[player][stat] = players[player][stat] + amt

for event in game_data:
  action = event['home_action'] or event['away_action']

  free_throw = re.search(r'^(.*) (missed|made) free throw\.$', action, re_flags)
  three_point = re.search(r'^(.*) (missed|made) three point jumper\.', action, re_flags)
  two_point = re.search(r'^(.*) (missed|made) (?:jumper|layup|tip shot|dunk)\.', action, re_flags)
  rebound = re.search(r'^(.*) (defensive|offensive) rebound\.$', action, re_flags)
  foul = re.search(r'^foul on (.*)$', action, re_flags)
  block = re.search(r'^(.*) block\.$', action, re_flags)
  steal = re.search(r'^(.*) steal\.$', action, re_flags)
  turnover = re.search(r'^(.*) turnover\.$', action, re_flags)

  if free_throw:
    player, missed_or_made = free_throw.groups()
    inc(player, 'fta')
    if missed_or_made == 'made':
      inc(player, 'ftm')
      inc(player, 'points')
    continue

  if three_point:
    player, missed_or_made = three_point.groups()
    inc(player, '3pa')
    if missed_or_made == 'made':
      inc(player, '3pm')
      inc(player, 'points', 3)
    continue

  if two_point:
    player, missed_or_made = two_point.groups()
    inc(player, '2pa')
    if missed_or_made == 'made':
      inc(player, '2pm')
      inc(player, 'points', 2)
    continue

  if rebound:
    player, offensive_or_defensive = rebound.groups()
    if offensive_or_defensive == 'Offensive':
      inc(player, 'oreb')
    else:
      inc(player, 'dreb')
    continue

  if foul:
    inc(foul.groups()[0], 'fouls')
    continue

  if steal:
    inc(steal.groups()[0], 'steals')
    continue

  if turnover:
    inc(turnover.groups()[0], 'turnovers')
    continue

  if block:
    inc(block.groups()[0], 'blocks')
    continue

  # At this point, we haven't handled it yet.
  print action


# TODO more processing.

# TODO Dump data into database.
for player in players:
  print player, players[player]['2pm'], '-', players[player]['2pa']


