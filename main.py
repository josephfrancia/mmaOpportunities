import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import time as t
import random
from itertools import compress 

from sportsbooks import cleanMoneylineData
from sportsbooks import getJuice
from sportsbooks import getCasinoProfit
from sportsbooks import getImpliedOdds
from sportsbooks import is_number
from sportsbooks import getCutoffMoneyLine

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import time as t
import random

from sportsbooks import cleanMoneylineData
from sportsbooks import getJuice
from sportsbooks import getCasinoProfit
from sportsbooks import getImpliedOdds
from sportsbooks import is_number
from sportsbooks import getKellyBet
from sportsbooks import americanOddsToDecimalOdds

#draftkings
draftkings_url = 'https://sportsbook.draftkings.com/leagues/mma/2162?category=fight-lines&subcategory=moneyline'
draftkings_soup_object = BeautifulSoup(requests.get(draftkings_url).text)
draftkings_names_html = draftkings_soup_object.select(".sportsbook-outcome-cell__label")
draftkings_odds_html = draftkings_soup_object.select(".sportsbook-outcome-cell__element")
draftkings_names = [x.text for x in draftkings_names_html]
draftkings_odds = [int(x.text) for x in draftkings_odds_html if x.text != '']

draftkings_df = cleanMoneylineData(draftkings_names, draftkings_odds, "draftkings") 

#fanduel
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://sportsbook.fanduel.com/sports/navigation/7287.1/9886.3")
fanduel_raw_data = driver.find_elements_by_class_name('selection-column')
fanduel_data = [x.text.split('\n') for x in fanduel_raw_data]
valid_indices = [len(x)==2 for x in fanduel_data]
fanduel_data = list(compress(fanduel_data, valid_indices)) 
fanduel_names = [x[0] for x in fanduel_data]
fanduel_odds = [x[1] for x in fanduel_data]

fanduel_df = cleanMoneylineData(fanduel_names, fanduel_odds, "fanduel") 

#betonline
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.betonline.ag/sportsbook/martial-arts/mma")
t.sleep(random.randint(10, 20))
betonline_data_html = driver.find_elements_by_css_selector('.bdevtt')
betonline_data = np.array([x.text for x in betonline_data_html])
indices_to_remove = []
for i in range(0, len(betonline_data)):
    if pd.Series(betonline_data[i]).isin(["Un", "Ov"])[0]:
        indices_to_remove.append([i, i+1, i+2, i+3])

betonline_data = np.delete(betonline_data, indices_to_remove)
betonline_odds = [x for x in betonline_data if bool(re.search("^\\+", x)) or bool(re.search("^\\-", x))]
betonline_names = [x for x in betonline_data if re.sub('[\s+]', '', re.sub('-', '', (re.sub('\.', '', x)))).isalpha()
                  and len(x) > 1 
                  and x != "\no\n"
                  and not bool(re.search("\\:", x))]

betonline_df = cleanMoneylineData(betonline_names, betonline_odds, "betonline") 

#bovada
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.bovada.lv/sports/ufc-mma")
t.sleep(random.randint(30, 40))
bovada_odds_html = driver.find_elements_by_css_selector('.bet-btn')
bovada_names_html = driver.find_elements_by_css_selector('.competitor-name')
bovada_odds = [100 if x.text == 'EVEN' else x.text for x in bovada_odds_html]
bovada_names = [x.text for x in bovada_names_html]

bovada_df = cleanMoneylineData(bovada_names, bovada_odds, "bovada") 

#mybookie
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://mybookie.ag/sportsbook/ufc/')

mybookie_odds_html = driver.find_elements_by_css_selector(".lines-odds")
mybookie_odds = np.array([x.text for x in mybookie_odds_html])
mybookie_odds = mybookie_odds[[is_number(x) for x in mybookie_odds]]

mybookie_html = driver.find_elements_by_css_selector(".justify-content-around")
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

#bookmaker
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.bookmaker.eu/live-lines/martial-arts")
t.sleep(random.randint(10, 20))
bookmaker_data_html = driver.find_elements_by_css_selector('.oddsD')
bookmaker_data = np.array([x.text for x in bookmaker_data_html])
bookmaker_cleaned_data = [x.split('\n') for x in bookmaker_data]
bookmaker_names = [x[0] for x in bookmaker_cleaned_data]
bookmaker_odds = [int(x[3]) for x in bookmaker_cleaned_data]
bookmaker_df = cleanMoneylineData(bookmaker_names, bookmaker_odds, "bookmaker")

#merging data 
merged_data = pd.concat([bovada_df, draftkings_df, fanduel_df, mybookie_df, betonline_df, bookmaker_df])

num_unique_sportsbooks = pd.DataFrame(merged_data.groupby(['team1', 'team2']).sportsbook.nunique())

best_team1_ml_df = pd.DataFrame() 
best_team2_ml_df = pd.DataFrame() 


best_team1_ml_df['bestTeam1MoneyLine'] = merged_data.groupby(['team1', 'team2'])['team1MoneyLine'].apply(lambda x: max(x))
best_team2_ml_df['bestTeam2MoneyLine'] = merged_data.groupby(['team1', 'team2'])['team2MoneyLine'].apply(lambda x: max(x))


best_team1_ml_df['bestTeam1ImpliedOdds'] = best_team1_ml_df['bestTeam1MoneyLine'].apply(lambda x: getImpliedOdds(x))
best_team2_ml_df['bestTeam2ImpliedOdds'] = best_team2_ml_df['bestTeam2MoneyLine'].apply(lambda x: getImpliedOdds(x))

consensus_team1_prob = pd.DataFrame() 
consensus_team2_prob = pd.DataFrame() 

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

valuable_data = merged_data
valuable_data = valuable_data.reset_index()

for x in range(0, len(valuable_data)):
    if valuable_data["bestDeviationTeam1"][x] > 0 and valuable_data["bestDeviationTeam1"][x] > valuable_data["bestDeviationTeam2"][x] and valuable_data["team1MoneyLine"][x] == valuable_data["bestTeam1MoneyLine"][x]: 
        print("Bet " + str(valuable_data["kellyBetTeam1"][x]) +  " on " + np.array(valuable_data["team1"])[x] + " at " + str(np.array(valuable_data["bestTeam1MoneyLine"])[x]) + " at " + np.array(valuable_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(valuable_data["bestDeviationTeam1"])[x]) + ' while average moneyline is ' +  str(np.array(valuable_data["average_team1_ml"])[x]) + ' as determiined by ' + str(valuable_data['sportsbook_y'][x]) + ' sportsbooks') 

    if valuable_data["bestDeviationTeam2"][x] > 0 and valuable_data["bestDeviationTeam2"][x] > valuable_data["bestDeviationTeam1"][x] and valuable_data["team2MoneyLine"][x] == valuable_data["bestTeam2MoneyLine"][x]: 
        print("Bet " + str(valuable_data["kellyBetTeam2"][x]) +  " on " + np.array(valuable_data["team2"])[x] + " at " + str(np.array(valuable_data["bestTeam2MoneyLine"])[x]) + " at " + np.array(valuable_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(valuable_data["bestDeviationTeam2"])[x]) + ' while average moneyline is ' +  str(np.array(valuable_data["average_team2_ml"])[x]) + ' as determiined by ' + str(valuable_data['sportsbook_y'][x]) + ' sportsbooks') 



