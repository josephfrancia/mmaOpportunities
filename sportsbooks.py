import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import time as t

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getImpliedOdds(moneyLine): 
    if moneyLine >= 100:
        impliedOdds = 100 / (100 + moneyLine)
    elif moneyLine <= -100:
        impliedOdds = abs(moneyLine) / (100 + abs(moneyLine))
    else: 
        impliedOdds = None
    return(impliedOdds)

def getCasinoProfit(moneyLines):
    overround = sum(np.array([getImpliedOdds(x) for x in moneyLines])) - 1
    vigorish = overround / (1 + overround)
    return(vigorish)

def getJuice(moneyLines1, moneyLines2):
    juice = np.empty(len(moneyLines1), dtype=object)
    for x in range(0,len(moneyLines1)):
        juice[x] = getCasinoProfit([moneyLines1[x], moneyLines2[x]])
    return(juice)

def cleanMoneylineData(names, odds, sportsbook): 
    team1Names = np.empty(len(names), dtype=object)
    team1MoneyLine = np.empty(len(names), dtype=object)
    team2Names = np.empty(len(names), dtype=object)
    team2MoneyLine = np.empty(len(names), dtype=object)

    for x in range(0, len(names)):
        if x%2 == 0:
            team1Names[x] = names[x]
            team1MoneyLine[x] = odds[x]
        else: 
            team2Names[x] = names[x]
            team2MoneyLine[x] = odds[x]

    team1Names = [str(x).strip().upper() for x in team1Names if x is not None]
    team2Names = [str(x).strip().upper() for x in team2Names if x is not None]
    team1MoneyLine = [int(x) for x in team1MoneyLine if x is not None]
    team2MoneyLine = [int(x) for x in team2MoneyLine if x is not None]
    juice = getJuice(team1MoneyLine, team2MoneyLine)
    true_probability_team1_wins = [getImpliedOdds(x) / (getImpliedOdds(x) + getImpliedOdds(y)) for x, y in zip(team1MoneyLine, team2MoneyLine)]
    true_probability_team2_wins = [getImpliedOdds(x) / (getImpliedOdds(x) + getImpliedOdds(y)) for x, y in zip(team2MoneyLine, team1MoneyLine)]
    
    needs_switching = [x == max(x, y) for x, y in zip(team1Names, team2Names)]

    team1NamesOrdered = [min(x, y) for x, y in zip(team1Names, team2Names)]
    team2NamesOrdered = [max(x, y) for x, y in zip(team1Names, team2Names)]

    team1MoneyLineOrdered = [y if z is True else x for x, y, z in zip(team1MoneyLine,  team2MoneyLine, needs_switching)]

    team2MoneyLineOrdered = [x if z is True else y for x, y, z in zip(team1MoneyLine,  team2MoneyLine, needs_switching)]

    true_probability_team1_wins_ordered = [y if z is True else x for x, y, z in 
                                              zip(true_probability_team1_wins, 
                                                  true_probability_team2_wins, 
                                                  needs_switching)]

    true_probability_team2_wins_ordered = [x if z is True else y for x, y, z in 
                                              zip(true_probability_team1_wins, 
                                                  true_probability_team2_wins, 
                                                  needs_switching)]
    
    dictionary = {'team1': team1NamesOrdered, 
                  'team2': team2NamesOrdered, 
                  'team1MoneyLine': team1MoneyLineOrdered, 
                  'team2MoneyLine': team2MoneyLineOrdered, 
                  'juice': juice, 
                  'true_probability_team1_wins': true_probability_team1_wins_ordered, 
                  'true_probability_team2_wins': true_probability_team2_wins_ordered, 
                  'sportsbook': sportsbook}
    df = pd.DataFrame(dictionary)
    return(df)
    
