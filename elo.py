import pandas as pd
import math

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
# Start all teams at 2000
teams = df['team1'].unique()
elodict = {}
for team in teams:
    elodict[team] = 2000

yearlydict = {}

# Set the current year to 1965
currentyear = 1965


for index, row in df.iterrows():

    if (row['season'] > currentyear):
        tempdict = elodict.copy()
        yearlydict[currentyear] = tempdict
        currentyear += 1

    team1name = row['team1']
    team2name = row['team2']

    team1elo = elodict.get(team1name)
    team2elo = elodict.get(team2name)
    outcome = row['result1']
    playoff = row['playoff']
    neutral = row['neutral']

    team1elo, team2elo = elo_rating(team1elo, team2elo, outcome, playoff, neutral)

    elodict.update({team1name: team1elo})
    elodict.update({team2name: team2elo})

    # print(f"{team1name}'s elo is now {team1elo}")
    # print(f"{team2name}'s elo is now {team2elo}")
    # print("")

print(elodict)

yearbyyear = pd.DataFrame(yearlydict)
yearbyyear.index.name="Year"
yearbyyear.to_csv('nfl_elo_by_year.csv')