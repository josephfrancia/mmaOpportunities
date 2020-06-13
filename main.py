import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import time as t

from sportsbooks import cleanMoneylineData
from sportsbooks import getJuice
from sportsbooks import getCasinoProfit
from sportsbooks import getImpliedOdds

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
fanduel_names = [x[0] for x in fanduel_data]
fanduel_odds = [x[1] for x in fanduel_data]

fanduel_df = cleanMoneylineData(fanduel_names, fanduel_odds, "fanduel") 

#betonline
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.betonline.ag/sportsbook/martial-arts/mma")
t.sleep(10)
betonline_data_html = driver.find_elements_by_css_selector('.bdevtt')
betonline_data = np.array([x.text for x in betonline_data_html])
indices_to_remove = []
for i in range(0, len(betonline_data)):
    if pd.Series(betonline_data[i]).isin(["Un", "Ov"])[0]:
        indices_to_remove.append([i, i+1, i+2, i+3])

betonline_data = np.delete(betonline_data, indices_to_remove)
betonline_odds = [x for x in betonline_data if bool(re.search("^\\+", x)) or bool(re.search("^\\-", x))]
betonline_names = [x for x in betonline_data if re.sub('[\s+]', '', re.sub('-', '', x)).isalpha()
                  and len(x) > 1 
                  and x != "\no\n"
                  and not bool(re.search("\\:", x))]

betonline_df = cleanMoneylineData(betonline_names, betonline_odds, "betonline") 

#bovada
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.bovada.lv/sports/ufc-mma")
t.sleep(30)
bovada_odds_html = driver.find_elements_by_css_selector('.bet-btn')
bovada_names_html = driver.find_elements_by_css_selector('.competitor-name')
bovada_odds = [100 if x.text == 'EVEN' else x.text for x in bovada_odds_html]
bovada_names = [x.text for x in bovada_names_html]

bovada_df = cleanMoneylineData(bovada_names, bovada_odds, "bovada") 

#mybookie
mybookie_url = 'https://mybookie.ag/sportsbook/ufc/'
mybookie_soup_object = BeautifulSoup(requests.get(mybookie_url).text)
mybookie_names_html = mybookie_soup_object.select(".text-truncate")
mybookie_odds_html = mybookie_soup_object.select(".lines-odds")
mybookie_names = np.array([x.text for x in mybookie_names_html])
mybookie_odds = np.array([x.text for x in mybookie_odds_html])
mybookie_odds = mybookie_odds[np.logical_not(pd.Series(mybookie_odds).isin([' - ', ' -  ']))]
listOfOverUnders = ["&" in x for x in mybookie_odds]
listOfOverUnders = [not x for x in listOfOverUnders]
mybookie_odds = mybookie_odds[listOfOverUnders]
mybookie_odds = mybookie_odds[0:76]
mybookie_names = mybookie_names[0:76]

mybookie_df = cleanMoneylineData(mybookie_names, mybookie_odds, "mybookie")

#merging data 
merged_data = pd.concat([bovada_df, draftkings_df, fanduel_df, mybookie_df, betonline_df])

num_unique_sportsbooks = pd.DataFrame(merged_data.groupby(['team1', 'team2']).sportsbook.nunique())

best_team1_ml_df = merged_data.groupby(['team1', 'team2'])['team1MoneyLine'].agg({'bestTeam1MoneyLine':'max'})
best_team2_ml_df = merged_data.groupby(['team1', 'team2'])['team2MoneyLine'].agg({'bestTeam2MoneyLine':'max'})


best_team1_ml_df['bestTeam1ImpliedOdds'] = best_team1_ml_df['bestTeam1MoneyLine'].apply(lambda x: getImpliedOdds(x))
best_team2_ml_df['bestTeam2ImpliedOdds'] = best_team2_ml_df['bestTeam2MoneyLine'].apply(lambda x: getImpliedOdds(x))


consensus_team1_prob = merged_data.groupby(['team1', 'team2'])['true_probability_team1_wins'].agg({'consensusTeam1Probability':'mean'})
consensus_team2_prob = merged_data.groupby(['team1', 'team2'])['true_probability_team2_wins'].agg({'consensusTeam2Probability':'mean'})


avg_team1_ml = merged_data.groupby(['team1', 'team2'])['team1MoneyLine'].agg({'average_team1_ml':'mean'})
avg_team2_ml = merged_data.groupby(['team1', 'team2'])['team2MoneyLine'].agg({'average_team1_m2':'mean'})

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

valuable_data = merged_data[merged_data['sportsbook_y'] >= 4]
valuable_data = valuable_data.reset_index()
for x in range(0, len(valuable_data)):
    if valuable_data["bestDeviationTeam1"][x] > 0 and valuable_data["bestDeviationTeam1"][x] > valuable_data["bestDeviationTeam2"][x] and valuable_data["team1MoneyLine"][x] == valuable_data["bestTeam1MoneyLine"][x]: 
        print("Bet on " + np.array(valuable_data["team1"])[x] + " at " + str(np.array(valuable_data["bestTeam1MoneyLine"])[x]) + " at " + np.array(valuable_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(valuable_data["bestDeviationTeam1"])[x]) + ' while average moneyline is ' +  str(np.array(valuable_data["average_team1_ml"])[x])) 

    if valuable_data["bestDeviationTeam2"][x] > 0 and valuable_data["bestDeviationTeam2"][x] > valuable_data["bestDeviationTeam1"][x] and valuable_data["team2MoneyLine"][x] == valuable_data["bestTeam2MoneyLine"][x]: 
        print("Bet on " + np.array(valuable_data["team2"])[x] + " at " + str(np.array(valuable_data["bestTeam2MoneyLine"])[x]) + " at " + np.array(valuable_data["sportsbook_x"])[x] + " for deviation of " + str(np.array(valuable_data["bestDeviationTeam2"])[x]) + ' while average moneyline is ' +  str(np.array(valuable_data["average_team1_m2"])[x])) 
