import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time as t
import random
from itertools import compress 
from itertools import chain

from sportsbooks import cleanMoneylineData
from sportsbooks import getJuice
from sportsbooks import getCasinoProfit
from sportsbooks import getImpliedOdds
from sportsbooks import is_number
from sportsbooks import getCutoffMoneyLine
from sportsbooks import getKellyBet



#draftkings
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://sportsbook.draftkings.com/leagues/mma/ufc')
draftkings_odds_html = driver.find_elements(By.CSS_SELECTOR, '.default-color')
draftkings_odds_raw = [x.text for x in draftkings_odds_html]
draftkings_odds = [int(str(x.replace("−", "-"))) if x[0] == "−" else int(x) for x in draftkings_odds_raw]
draftkings_names_html = driver.find_elements(By.CSS_SELECTOR, '.sportsbook-outcome-cell__label')
draftkings_names = [x.text for x in draftkings_names_html]
draftkings_df = cleanMoneylineData(draftkings_names, draftkings_odds, "draftkings")


#bet-mgm
try:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://sports.co.betmgm.com/en/sports/mma-45/betting/usa-9")
    t.sleep(random.randint(10, 20))
    betmgm_odds_html = driver.find_elements(By.CSS_SELECTOR,'.option-indicator')
    betmgm_names_html = driver.find_elements(By.CSS_SELECTOR,'.participants-pair-game')
    length_of_bet_mgm_odds = len([x.text for x in betmgm_odds_html])
    betmgm_odds = [x.text for x in betmgm_odds_html if x != ''][(length_of_bet_mgm_odds- (len(betmgm_names_html) * 2)):]
    betmgm_names = [x.text.split('\n') for x in betmgm_names_html]
    betmgm_names = list(chain(*[[x[0], x[1]] for x in betmgm_names]))
    betmgm_names = [x[:-3] for x in betmgm_names if x != '']
    betmgm_df = cleanMoneylineData(betmgm_names, betmgm_odds, "betmgm") 

except: 
    try: 
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://sports.co.betmgm.com/en/sports/mma-45/betting/usa-9")
        t.sleep(random.randint(10, 20))
        betmgm_odds_html = driver.find_elements(By.CSS_SELECTOR,'.option-indicator')
        betmgm_names_html = driver.find_elements(By.CSS_SELECTOR,'.participants-pair-game')
        length_of_bet_mgm_odds = len([x.text for x in betmgm_odds_html])
        betmgm_odds = [x.text for x in betmgm_odds_html if x != ''][(length_of_bet_mgm_odds- (len(betmgm_names_html) * 2)):]
        betmgm_names = [x.text.split('\n') for x in betmgm_names_html]
        betmgm_names = list(chain(*[[x[0], x[1]] for x in betmgm_names]))
        betmgm_names = [x[:-3] for x in betmgm_names if x != '']
        betmgm_df = cleanMoneylineData(betmgm_names, betmgm_odds, "betmgm") 
    except: 
        betmgm_df = pd.DataFrame()   


#fanduel
try: 
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://sportsbook.fanduel.com/mma?tab=ufc-fights")
    t.sleep(random.randint(10, 20))
    fanduel_odds_html = driver.find_elements(By.CSS_SELECTOR, '.n')
    fanduel_names_html = driver.find_elements(By.CSS_SELECTOR, '.ib')
    fanduel_odds = [x.text for x in fanduel_odds_html if is_number(x.text)]
    fanduel_names = [x.text for x in fanduel_names_html]
    fanduel_df = cleanMoneylineData(fanduel_names, fanduel_odds, "fanduel") 
except: 
    fanduel_df = pd.DataFrame()


#betonline
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://classic.betonline.ag/sportsbook/martial-arts/mma")
t.sleep(random.randint(10, 20))
betonline_data_html = driver.find_elements(By.CSS_SELECTOR, '.bdevtt')
betonline_data = np.array([x.text for x in betonline_data_html])
indices_to_remove = []
for i in range(0, len(betonline_data)):
    if pd.Series(betonline_data[i]).isin(["Un", "Ov"])[0]:
        indices_to_remove.append([i, i+1, i+2, i+3])

betonline_data = np.delete(betonline_data, indices_to_remove)
betonline_odds = [x for x in betonline_data if bool(re.search("^\\+", x)) or bool(re.search("^\\-", x))]
betonline_names = [x for x in betonline_data if re.sub('[\s+]', '', re.sub('-', '', (re.sub('\.', '', re.sub('\'', '', x))))).isalpha()
                  and len(x) > 1 
                  and x != "\no\n"
                  and not bool(re.search("\\:", x))]

betonline_df = cleanMoneylineData(betonline_names, betonline_odds, "betonline") 

#bovada
try:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.bovada.lv/sports/ufc-mma")
    t.sleep(random.randint(30, 40))
    bovada_odds_html = driver.find_elements(By.CSS_SELECTOR, '.bet-btn')
    bovada_names_html = driver.find_elements(By.CSS_SELECTOR, '.competitor-name')
    bovada_odds = [100 if x.text == 'EVEN' else x.text for x in bovada_odds_html]
    bovada_names = [x.text for x in bovada_names_html]
    bovada_df = cleanMoneylineData(bovada_names, bovada_odds, "bovada") 

except: 
    try: 
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://www.bovada.lv/sports/ufc-mma")
        t.sleep(random.randint(30, 40))
        bovada_odds_html = driver.find_elements(By.CSS_SELECTOR, '.bet-btn')
        bovada_names_html = driver.find_elements(By.CSS_SELECTOR, '.competitor-name')
        bovada_odds = [100 if x.text == 'EVEN' else x.text for x in bovada_odds_html]
        bovada_names = [x.text for x in bovada_names_html]
        bovada_df = cleanMoneylineData(bovada_names, bovada_odds, "bovada") 
    except: 
        bovada_df = pd.DataFrame()   

#mybookie
try: 
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://mybookie.ag/sportsbook/ufc/')
    t.sleep(random.randint(10, 20))

    mybookie_odds_html = driver.find_elements(By.CSS_SELECTOR, ".lines-odds")
    mybookie_odds = np.array([x.text for x in mybookie_odds_html])
    mybookie_odds = mybookie_odds[[is_number(x) for x in mybookie_odds]]

    mybookie_html = driver.find_elements(By.CSS_SELECTOR, ".justify-content-around")
    mybookie_html_cleaned = np.array([x.text for x in mybookie_html])
    mybookie_names = []
    i = 0
    while i < len(mybookie_html_cleaned): 
        if i == 1 or ((i-1)%4==0): 
            mybookie_names.append(mybookie_html_cleaned[i])
        i += 1
    mybookie_names = [x.split('\n') for x in mybookie_names]
    mybookie_names = sum(mybookie_names, [])
    mybookie_df = cleanMoneylineData(mybookie_names, mybookie_odds, "mybookie")

except: 
    try: 
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://mybookie.ag/sportsbook/ufc/')
        t.sleep(random.randint(10, 20))

        mybookie_odds_html = driver.find_elements(By.CSS_SELECTOR, ".lines-odds")
        mybookie_odds = np.array([x.text for x in mybookie_odds_html])
        mybookie_odds = mybookie_odds[[is_number(x) for x in mybookie_odds]]

        mybookie_html = driver.find_elements(By.CSS_SELECTOR, ".justify-content-around")
        mybookie_html_cleaned = np.array([x.text for x in mybookie_html])
        mybookie_names = []
        i = 0
        while i < len(mybookie_html_cleaned): 
            if i == 1 or ((i-1)%4==0): 
                mybookie_names.append(mybookie_html_cleaned[i])
            i += 1
        mybookie_names = [x.split('\n') for x in mybookie_names]
        mybookie_names = sum(mybookie_names, [])
        mybookie_df = cleanMoneylineData(mybookie_names, mybookie_odds, "mybookie")
    except: 
        mybookie_df = pd.DataFrame() 

#caesars
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.williamhill.com/us/nj/bet/ufcmma/events/all")
t.sleep(random.randint(10, 20))
buttons_to_expand = driver.find_elements(By.CSS_SELECTOR, '.unexpanded') 
[x.click() for x in buttons_to_expand]
betcaesars_names_html = driver.find_elements(By.CSS_SELECTOR, '.eventInfo') 
betcaesars_odds_html = driver.find_elements(By.CSS_SELECTOR, '.SelectionOption')
betcaesars_odds = [x.text for x in betcaesars_odds_html]
betcaesars_names = [x.text for x in betcaesars_names_html]
caesars_df = cleanMoneylineData(betcaesars_names, betcaesars_odds, "caesars") 

#pointsbet
try:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://nj.pointsbet.com/sports/mma/UFC")
    t.sleep(random.randint(10, 20))
    pointsbet_data_html = driver.find_elements(By.CSS_SELECTOR, '.faxe22p')
    pointsbet_relevant_data = [x.text.split('\n') for x in pointsbet_data_html]
    pointsbet_names = list(chain(*[[x[0], x[2]] for x in pointsbet_relevant_data]))
    pointsbet_odds = list(chain(*[[x[1], x[3]] for x in pointsbet_relevant_data]))
    pointsbet_df = cleanMoneylineData(pointsbet_names, pointsbet_odds, "pointsbet") 

except: 
    try: 
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://nj.pointsbet.com/sports/mma/UFC")
        t.sleep(random.randint(10, 20))
        pointsbet_data_html = driver.find_elements(By.CSS_SELECTOR, '.faxe22p')
        pointsbet_relevant_data = [x.text.split('\n') for x in pointsbet_data_html]
        pointsbet_names = list(chain(*[[x[0], x[2]] for x in pointsbet_relevant_data]))
        pointsbet_odds = list(chain(*[[x[1], x[3]] for x in pointsbet_relevant_data]))
        pointsbet_df = cleanMoneylineData(pointsbet_names, pointsbet_odds, "pointsbet") 
    except: 
        pointsbet_df = pd.DataFrame()



#merging data 
merged_data = pd.concat([draftkings_df, fanduel_df, betonline_df, mybookie_df, betmgm_df, bovada_df, caesars_df, pointsbet_df])

num_unique_sportsbooks = pd.DataFrame(merged_data.groupby(['team1', 'team2']).sportsbook.nunique())

best_team1_ml_df = pd.DataFrame() 
best_team2_ml_df = pd.DataFrame() 


best_team1_ml_df['bestTeam1MoneyLine'] = merged_data.groupby(['team1', 'team2'])['team1MoneyLine'].apply(lambda x: max(x))
best_team2_ml_df['bestTeam2MoneyLine'] = merged_data.groupby(['team1', 'team2'])['team2MoneyLine'].apply(lambda x: max(x))


best_team1_ml_df['bestTeam1ImpliedOdds'] = best_team1_ml_df['bestTeam1MoneyLine'].apply(lambda x: getImpliedOdds(x))
best_team2_ml_df['bestTeam2ImpliedOdds'] = best_team2_ml_df['bestTeam2MoneyLine'].apply(lambda x: getImpliedOdds(x))

consensus_team1_prob = pd.DataFrame() 
consensus_team2_prob = pd.DataFrame() 

consensus_team1_prob['consensusTeam1Probability'] = merged_data.groupby(['team1', 'team2'])['true_probability_team1_wins'].apply(lambda x: np.mean(x))
consensus_team2_prob['consensusTeam2Probability'] = merged_data.groupby(['team1', 'team2'])['true_probability_team2_wins'].apply(lambda x: np.mean(x))

consensus_team1_prob['cutOffMLTeam1'] = [getCutoffMoneyLine(x) for x in consensus_team1_prob['consensusTeam1Probability']]
consensus_team2_prob['cutOffMLTeam2'] = [getCutoffMoneyLine(x) for x in consensus_team2_prob['consensusTeam2Probability']]

consensus_data = pd.merge(consensus_team1_prob, consensus_team2_prob, on=['team1', 'team2'], how='outer')
consensus_data = pd.merge(consensus_data, num_unique_sportsbooks, on=['team1', 'team2'], how='outer')


avg_team1_ml = pd.DataFrame() 
avg_team2_ml = pd.DataFrame() 

avg_team1_ml['average_team1_ml'] = merged_data.groupby(['team1', 'team2'])['team1MoneyLine'].apply(lambda x: np.mean(x))
avg_team2_ml['average_team2_ml'] = merged_data.groupby(['team1', 'team2'])['team2MoneyLine'].apply(lambda x: np.mean(x))

merged_data = pd.merge(merged_data, best_team1_ml_df, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, num_unique_sportsbooks, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, best_team2_ml_df, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, consensus_team1_prob, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, consensus_team2_prob, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, avg_team1_ml, on=['team1', 'team2'], how='outer')
merged_data = pd.merge(merged_data, avg_team2_ml, on=['team1', 'team2'], how='outer')

merged_data['bestJuice'] = getJuice(np.array(merged_data['bestTeam1MoneyLine']), np.array(merged_data['bestTeam2MoneyLine']))

merged_data['isBestTeam1MoneyLine'] = merged_data['bestTeam1MoneyLine'] == merged_data['team1MoneyLine']
merged_data['isBestTeam2MoneyLine'] = merged_data['bestTeam2MoneyLine'] == merged_data['team2MoneyLine'] 
merged_data['providesValue'] = [x or y for x,y in zip(merged_data['isBestTeam1MoneyLine'], merged_data['isBestTeam2MoneyLine'])]
merged_data['bestDeviationTeam1'] = [x - y for x,y in zip(merged_data['consensusTeam1Probability'], merged_data['bestTeam1ImpliedOdds'])]
merged_data['bestDeviationTeam2'] = [x - y for x,y in zip(merged_data['consensusTeam2Probability'], merged_data['bestTeam2ImpliedOdds'])]
merged_data['kellyBetTeam2'] = [getKellyBet(x, y, 300) for x,y in zip(merged_data['bestTeam2MoneyLine'], merged_data['consensusTeam2Probability'])]
merged_data['kellyBetTeam1'] = [getKellyBet(x, y, 300) for x,y in zip(merged_data['bestTeam1MoneyLine'], merged_data['consensusTeam1Probability'])]

merged_data = merged_data.reset_index()

for x in range(0, len(merged_data)):
    if merged_data["bestDeviationTeam1"][x] > 0.005 and merged_data["bestDeviationTeam1"][x] > merged_data["bestDeviationTeam2"][x] and merged_data["team1MoneyLine"][x] == merged_data["bestTeam1MoneyLine"][x]: 
        print("Bet " + str(merged_data["kellyBetTeam1"][x]) +  " on " + np.array(merged_data["team1"])[x] + " at " + str(np.array(merged_data["bestTeam1MoneyLine"])[x]) + " at " + np.array(merged_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(merged_data["bestDeviationTeam1"])[x]) + ' while average moneyline is ' +  str(np.array(merged_data["average_team1_ml"])[x]) + ' as determiined by ' + str(merged_data['sportsbook_y'][x]) + ' sportsbooks') 

    if merged_data["bestDeviationTeam2"][x] > 0.005 and merged_data["bestDeviationTeam2"][x] > merged_data["bestDeviationTeam1"][x] and merged_data["team2MoneyLine"][x] == merged_data["bestTeam2MoneyLine"][x]: 
        print("Bet " + str(merged_data["kellyBetTeam2"][x]) +  " on " + np.array(merged_data["team2"])[x] + " at " + str(np.array(merged_data["bestTeam2MoneyLine"])[x]) + " at " + np.array(merged_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(merged_data["bestDeviationTeam2"])[x]) + ' while average moneyline is ' +  str(np.array(merged_data["average_team2_ml"])[x]) + ' as determiined by ' + str(merged_data['sportsbook_y'][x]) + ' sportsbooks') 

        
print("")
print("")
print("")
print("")
print("")
print("")
print("End of betting recommendations.. Here are the best bets for a given fight.")
print("")
print("")
print("")
print("")
print("")
print("")      
        
for x in range(0, len(merged_data)):
    if merged_data["team1MoneyLine"][x] == merged_data["bestTeam1MoneyLine"][x]: 
        print("Bet on " + np.array(merged_data["team1"])[x] + " at " + str(np.array(merged_data["bestTeam1MoneyLine"])[x]) + " at " + np.array(merged_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(merged_data["bestDeviationTeam1"])[x]) + ' while average moneyline is ' +  str(np.array(merged_data["average_team1_ml"])[x]) + ' as determiined by ' + str(merged_data['sportsbook_y'][x]) + ' sportsbooks') 

    if merged_data["team2MoneyLine"][x] == merged_data["bestTeam2MoneyLine"][x]: 
        print("Bet on " + np.array(merged_data["team2"])[x] + " at " + str(np.array(merged_data["bestTeam2MoneyLine"])[x]) + " at " + np.array(merged_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(merged_data["bestDeviationTeam2"])[x]) + ' while average moneyline is ' +  str(np.array(merged_data["average_team2_ml"])[x]) + ' as determiined by ' + str(merged_data['sportsbook_y'][x]) + ' sportsbooks') 


draftkings_index = draftkings_df.index
draftkings_number_of_rows = len(draftkings_index)

fanduel_index = fanduel_df.index
fanduel_number_of_rows = len(fanduel_index)

betonline_index = betonline_df.index
betonline_number_of_rows = len(betonline_index)

mybookie_index = mybookie_df.index
mybookie_number_of_rows = len(mybookie_index)

betmgm_index = betmgm_df.index
betmgm_number_of_rows = len(betmgm_index)

bovada_index = bovada_df.index
bovada_number_of_rows = len(bovada_index)

caesars_index = caesars_df.index
caesars_number_of_rows = len(caesars_index)

pointsbet_index = pointsbet_df.index
pointsbet_number_of_rows = len(pointsbet_index)

print("Draftkings has " + str(draftkings_number_of_rows) + " rows")
print("Fanduel has " + str(fanduel_number_of_rows) + " rows")
print("Betonline has " + str(betonline_number_of_rows) + " rows")
print("Mybookie has " + str(mybookie_number_of_rows) + " rows")
print("Betmgm has " + str(betmgm_number_of_rows) + " rows")
print("Bovada has " + str(bovada_number_of_rows) + " rows")
print("Caesars has " + str(caesars_number_of_rows) + " rows")
print("Pointsbet has " + str(pointsbet_number_of_rows) + " rows")




