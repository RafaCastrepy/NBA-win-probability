from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.endpoints import franchisehistory
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playbyplayv2
import pandas as pd
import re

pattern = r"^(\d{4})-(\d{2})$"

import re
from nba_api.stats.library.parameters import SeasonAll

def valid_seasons(season_str):
    match = re.match(pattern, season_str)
    if not match:
        return False

    start_year = int(match.group(1))
    end_year = int(match.group(2))
    expected_end = (start_year + 1) % 100
    if end_year != expected_end:
        return False

    # Use SeasonAll.all for the list of valid seasons
    return season_str in SeasonAll.all




franchises = franchisehistory.FranchiseHistory().get_data_frames()[0]
franchises['START_YEAR'] = pd.to_numeric(franchises['START_YEAR'])
franchises['END_YEAR'] = pd.to_numeric(franchises['END_YEAR'])


filtered = franchises[franchises['END_YEAR'] >= 1996]


nba_teams = pd.DataFrame(teams.get_teams())


merged = filtered.merge(nba_teams, left_on="TEAM_ID", right_on="id", how="left")


team_abbrs = merged['abbreviation'].dropna().unique().tolist()
team_abbrs.sort()

print(f"Teams from 1996-97 to present ({len(team_abbrs)} teams):")
print(team_abbrs)




year = input("Enter a season (e.g., 2022-23): ")

print(f"You picked {year}")
teams = []

games = leaguegamefinder.LeagueGameFinder(season_nullable=year).get_data_frames()[0]
for i in range (2):
    print("Choose a team:")
    for i, t in enumerate(team_abbrs, start=1):
        print(f"{i}. {t}")

    
    choice = int(input("Enter number: "))

    team = team_abbrs[choice-1]
    teams.append(team)

    print(f"You picked {team}")

team1 = "GSW"  # Golden State Warriors
team2 = "BOS"  # Boston Celtics

matchups = games[games['MATCHUP'].str.contains(teams[0]) & games['MATCHUP'].str.contains(teams[1])]

pd.set_option("display.max_columns", None)
print(matchups[['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL']])


game_id = matchups.iloc[0]['GAME_ID']  # for example, first one
pbp = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]
