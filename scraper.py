########################################
# Scraper for play-by-play NCAA men's basketball data from ESPN.
# Downloads game data and formats it to be dumped into a
# database elsewhere.
#
# Author: jesse.gunsch@gmail.com
#

# TODO figure out where Arizona/Colorado player entries are coming from
# TODO add team name to players (boxscore)
# TODO allow specifying games.
# TODO count assists from play-by-play.
# TODO databases.
# TODO this file has become a little long. Linear is okay but add a main/split
#      into smaller functions, especially since each section is well-contained

from BeautifulSoup import BeautifulSoup as Soup
from collections import defaultdict
from soupselect import select
import difflib
import re
import urllib

re_flags = re.I

def ensure(condition, message = 'Condition failed'):
  assert condition, message

def ensure_equals(expected, actual, message = 'Values not equal'):
  ensure(expected == actual, message + '(expected %s, actual %s)' % (str(expected), str(actual)))

def get_seconds(time_string):
  minutes, seconds = remaining_time.split(':')
  return int(minutes) * 60 + int(seconds)

def closest(word_list, word):
  matches = difflib.get_close_matches(word, word_list, 1, 0.6)
  if len(matches) > 0:
    return matches[0]
  return word

# Download game data.
game_id = '330030012'

pbp_soup = Soup(urllib.urlopen('http://espn.go.com/ncb/playbyplay?gameId=' + game_id))

boxscore_soup = Soup(urllib.urlopen('http://espn.go.com/ncb/boxscore?gameId=' + game_id))

game_data = []

########################
# HTML scraping here. Hopefully they don't change their format too much.
title = select(pbp_soup, 'title')[0].text

away_team, home_team, date = re.search(r'^(.*?) vs\. (.*?) - Play by Play - (.*?) -', title).groups()
team_names = [away_team, home_team]

pbp_rows = select(pbp_soup, '.mod-content tr')

# Increments as we go. 0 = first half, 1 = second half, 2+ = overtime periods
game_segment = 0
previous_remaining_time = 100000

# Split up meaningful parts of HTML rows. Get into a representation independent
# of artifacts of being on the page.
for play in pbp_rows:
  cells = select(play, 'td')
  if len(cells) == 4:
    remaining_time, away_action, score, home_action = [
      cell.text.replace('&nbsp;', ' ').strip() for cell in cells
    ]
    remaining_time = get_seconds(remaining_time)

    away_score, home_score = map(int, score.split('-'))

    if not away_action and not home_action:
      continue

    # This should mirror the game-event table structure
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
        timeout_event['away_action'] = action
      else:
        timeout_event['home_action'] = action

      game_data.append(timeout_event)

# Load boxscore data. No logic here, just splitting from HTML into more
# processable data.
boxscore_data = []
boxscore_rows = select(boxscore_soup, '#my-players-table tbody tr')
for player_data in boxscore_rows:
  cells = select(player_data, 'td')
  if len(cells) == 13:
    # This order should match the boxscore table on espn
    player_name, minutes, fgma, tpma, ftma, oreb, reb, ast, stl, blk, to, pf, pts = [
      cell.text for cell in cells
    ]

    if not player_name:
      continue

    fgm, fga = fgma.split('-')
    tpm, tpa = tpma.split('-')
    ftm, fta = ftma.split('-')

    minutes, fgm, fga, tpm, tpa, ftm, fta, oreb, reb, ast, stl, blk, to, pf, pts = map(int, [
      minutes, fgm, fga, tpm, tpa, ftm, fta, oreb, reb, ast, stl, blk, to, pf, pts
    ])

    boxscore_data.append({
      'name': player_name,
      'minutes': minutes,
      'fgm': fgm,
      'fga': fga,
      'tpm': tpm,
      'tpa': tpa,
      'ftm': ftm,
      'fta': fta,
      'oreb': oreb,
      'reb': reb,
      'ast': ast,
      'stl': stl,
      'blk': blk,
      'to': to,
      'pf': pf,
      'pts': pts,
    })


############################################################
# Turn game events into a more structured representation.

# This should mirror the player-game table structure.
players = defaultdict(lambda: {
  'team': '',
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
  'minutes': 0,
})

def inc(player, stat, amt=1):
  players[player][stat] = players[player][stat] + amt

for event in game_data:
  action = event['home_action'] or event['away_action']

  # Events added to player
  free_throw = re.search(r'^(.*) (missed|made) free throw\.$', action, re_flags)
  three_point = re.search(r'^(.*) (missed|made) three point jumper\.', action, re_flags)
  two_point = re.search(r'^(.*) (missed|made) (?:jumper|layup|tip shot|dunk)\.', action, re_flags)
  rebound = re.search(r'^(.*) (defensive|offensive) rebound\.$', action, re_flags)
  foul = re.search(r'^foul on (.*)$', action, re_flags)
  block = re.search(r'^(.*) block\.$', action, re_flags)
  steal = re.search(r'^(.*) steal\.$', action, re_flags)
  turnover = re.search(r'^(.*) turnover\.$', action, re_flags)

  # Ignored events
  timeout = re.search(r'^(.*) full timeout\.$', action, re_flags)
  jump_ball = re.search(r'^jump ball won by (.*)\.$', action, re_flags)

  # TODO count assists!

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

  if timeout or jump_ball:
    continue

  # At this point, we haven't handled it yet.
  print action


# Full player names seem to be more reliable from the play-by-play than
# from the boxscore.
player_names = players.keys()

for player_data in boxscore_data:
  player_name = closest(player_names, player_data['name'])
  player = players[player_name]

  player['minutes'] = player_data['minutes']

  ensure_equals(player['points'], player_data['pts'], 'Point discrepancy for %s' % player_name)
  ensure_equals(player['3pa'], player_data['tpa'], '3pa discrepancy for %s' % player_name)
  ensure_equals(player['3pm'], player_data['tpm'], '3pm discrepancy for %s' % player_name)
  ensure_equals(player['fta'], player_data['fta'], 'FTa discrepancy for %s' % player_name)
  ensure_equals(player['ftm'], player_data['ftm'], 'FTm discrepancy for %s' % player_name)
  ensure_equals(player['2pa'], player_data['fga'] - player_data['tpa'], '2pa discrepancy for %s' % player_name)
  ensure_equals(player['2pm'], player_data['fgm'] - player_data['tpm'], '2pm discrepancy for %s' % player_name)
  ensure_equals(player['blocks'], player_data['blk'], 'blocks discrepancy for %s' % player_name)
  ensure_equals(player['fouls'], player_data['pf'], 'fouls discrepancy for %s' % player_name)
  ensure_equals(player['steals'], player_data['stl'], 'steals discrepancy for %s' % player_name)
  #[ensure_equals(player['assists'], player_data['ast'], 'assists discrepancy for %s' % player_name)
  ensure_equals(player['oreb'], player_data['oreb'], 'oreb discrepancy for %s' % player_name)
  ensure_equals(player['dreb'], player_data['reb'] - player_data['oreb'], 'dreb discrepancy for %s' % player_name)



#################################################
# TODO Dump data into database.

#################################################
# Print our nicely formatted box-score table.
for player in players:
  print "%25s\t(2p %2d-%2d)\t(3p %2d-%2d)\t(FT %2d-%2d)\tast %2d\tstl %2d\tblk %2d\tto %2d\tpf %2d\tmin %2d" % (
      player,
      players[player]['2pm'], players[player]['2pa'],
      players[player]['3pm'], players[player]['3pa'],
      players[player]['ftm'], players[player]['fta'],
      players[player]['assists'],
      players[player]['steals'],
      players[player]['blocks'],
      players[player]['turnovers'],
      players[player]['fouls'],
      players[player]['minutes'],
  )

















