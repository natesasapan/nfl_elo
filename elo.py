import pandas as pd
import math


# Function to calculate probability of a team winning based on differences in their elo
def probability(rating1, rating2):
    return 1.0 / (1 + math.pow(10, (rating1 - rating2) / 400))

# Function to calculate Elo rating
# K is a constant.
# outcome determines the outcome: 1 for Player A win, 0 for Player B win, 0.5 for draw.
def elo_rating(hometeam, awayteam, outcome, playoff, neutral):

    # Constant, can update to change elo changes
    # Higher means more elo gain/loss
    # Less means less elo gain/loss
    K = 60

    # Calculate the Winning Probability of Home Team
    # Home teams historically win 57% of the time
    # A boost of 150 during calculations considers this
    home_field_adv = 150
    # During playoffs however, this value is much less
    # During the super bowl, it's played at a neutral site
    if playoff:
        home_field_adv /= 2
    if neutral:
        home_field_adv = 0
    Pb = probability(hometeam + home_field_adv, awayteam)
    Pa = 1 - Pb

    # Update the Elo Ratings
    # Playoff games are worth 1.5 times more
    hometeam = round(hometeam + K * math.pow(1.5, playoff) * (outcome - Pa), 2)
    awayteam = round(awayteam + K * math.pow(1.5, playoff) * ((1 - outcome) - Pb), 2)

    return hometeam, awayteam

# Read the csv file, create a dataframe
# Remove data we aren't going to use
df = pd.read_csv(r"nfl_games.csv")
df.pop('elo1')
df.pop('elo2')
df.pop('elo_prob1')

# Remove all seasons before AFL and NFL merger
df = df.drop(df[df.season < 1966].index)

# Get all the team names and create a dictionary
# Start all teams at 2000 rating
teams = df['team1'].unique()
elodict = {}
for team in teams:
    elodict[team] = 2000

yearlydict = {}

# Set the current year to 1965
currentyear = 1965

# Set a variable for min/max elo during calculations
max_elo, min_elo = 0,10000
max_team_name, min_team_name = '',''
max_team_season, min_team_season = '',''
max_team_date, min_team_date = '',''
date = ''

# Iterate through all rows in the Dataframe to calculate elo for each team, game by game
for index, row in df.iterrows():

    # Every time the year changes, add all teams current elo ratings to the yearly dictionary 
    if (row['season'] > currentyear or currentyear == 2020):
        tempdict = elodict.copy()
        yearlydict[currentyear] = tempdict
        currentyear += 1

    # Get current teams names, date, and ratings
    team1name = row['team1']
    team2name = row['team2']
    date = row['date']
    team1elo = elodict.get(team1name)
    team2elo = elodict.get(team2name)

    # Get outcome of game, 
    outcome = row['result1']
    playoff = row['playoff']
    neutral = row['neutral']

    # Get elo ratings after calculations
    team1elo, team2elo = elo_rating(team1elo, team2elo, outcome, playoff, neutral)

    # Update max/min elos if they exist
    if team1elo > max_elo:
        max_elo = team1elo
        max_team_name = team1name
        max_team_season = row['season']
        max_team_date = date
    if team2elo > max_elo:
        max_elo = team2elo
        max_team_name = team2name
        max_team_season = row['season']
        max_team_date = date
    if team1elo < min_elo:
        min_elo = team1elo
        min_team_name = team1name
        min_team_season = row['season']
        min_team_date = date
    if team2elo < min_elo:
        min_elo = team2elo
        min_team_name = team2name
        min_team_season = row['season']
        min_team_date = date

    # Update elo ratings in dictionary for each team
    elodict.update({team1name: team1elo})
    elodict.update({team2name: team2elo})

# Print the max/min elo reached by a team
print(f'The maximum elo reached ({max_elo}) during calculations was by {max_team_name} on {max_team_date} in {max_team_season}.')
print(f'The minimum elo reached ({min_elo}) during calculations was by {min_team_name} on {min_team_date} in {min_team_season}.')

# Save the yearly results to a new csv file
yearbyyear = pd.DataFrame(yearlydict)
yearbyyear.index.name="Year"
yearbyyear.to_csv('nfl_elo_by_year.csv')