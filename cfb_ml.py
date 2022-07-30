# -*- coding: utf-8 -*-
"""
College football game predictor
"""
from html_parse_cfb import html_to_df_web_scrape
import argparse
from sportsipy.ncaaf.teams import Teams
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier,RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import time
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform
class cfb:
    def __init__(self):
        print('initialize class cfb')
    def input_arg(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t1", "--team1", help = "team 1 input")
        parser.add_argument("-t2", "--team2", help = "team 2 input")
        parser.add_argument("-g", "--games", help = "number of games for test data")
        self.args = parser.parse_args()
    def get_teams(self, year):
        #TODO: put an if statement in here to use the all_data.csv as input data
        # instead of the webscraping process
        all_teams = Teams(year)
        team_names = all_teams.dataframes.abbreviation
        print(team_names)
        final_list = []
        self.year_store = year
        for abv in team_names:
            print(f'current team: {abv}')
            team = all_teams(abv)
            str_combine = 'https://www.sports-reference.com/cfb/schools/' + abv.lower() + '/' + str(self.year_store) + '/gamelog/'
            df_inst = html_to_df_web_scrape(str_combine)
            final_list.append(df_inst)
        output = pd.concat(final_list)
        output['game_result'].loc[output['game_result'].str.contains('W')] = 'W'
        output['game_result'].loc[output['game_result'].str.contains('L')] = 'L'
        output['game_result'] = output['game_result'].replace({'W': 1, 'L': 0})
        final_data = output.replace(r'^\s*$', np.NaN, regex=True) #replace empty string with NAN
        self.all_data = final_data.dropna()
        print('len data: ', len(self.all_data))
        self.all_data.to_csv('all_data.csv')
    def split(self):
        self.y = self.all_data['game_result']
        self.x = self.all_data.drop(columns=['game_result'])
        self.correlate_analysis()
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x,self.y, train_size=0.8)

    def correlate_analysis(self):
        corr_matrix = np.abs(self.x.astype(float).corr())
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
        # Find features with correlation greater than 0.88
        to_drop = [column for column in upper.columns if any(upper[column] >= 0.88)]
        print('drop these:', to_drop)
        self.drop_cols = to_drop
        self.x_no_corr = self.x.drop(columns=to_drop)

        #Create new scaled data - DO I REMOVE THE VARIABLES THAT ARE HIGHLY 
        # CORRELATED BEFORE I STANDARDIZE THEM OR STANDARDIZE AND THEN REMOVE
        # HIGHLY CORRELATED
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(self.x_no_corr)
        cols = self.x_no_corr.columns
        self.x = pd.DataFrame(scaled_data, columns = cols)
        
        top_corr_features = corr_matrix.index
        plt.figure(figsize=(20,20))
        #plot heat map
        g=sns.heatmap(corr_matrix[top_corr_features],annot=True,cmap="RdYlGn")
        plt.savefig('correlations.png')
        plt.close()

    def machine(self):
        Gradclass = GradientBoostingClassifier()
        Gradclass.fit(self.x_train,self.y_train)
        
        RandForclass = RandomForestClassifier()
        RandForclass.fit(self.x_train,self.y_train)
        
        DecTreeclass = DecisionTreeClassifier()
        DecTreeclass.fit(self.x_train,self.y_train)
        
        SVCclass = SVC()
        SVCclass.fit(self.x_train,self.y_train)
        
        LogReg = LogisticRegression(max_iter=5000)
        distributions = dict(C=uniform(loc=0, scale=4),penalty=['l2', 'l1'])
        clf = RandomizedSearchCV(LogReg, distributions, random_state=0)
        search = clf.fit(self.x_train,self.y_train)
        print(search.best_params_)
        
        MLPClass = MLPClassifier()
        MLPClass.fit(self.x_train,self.y_train)
        
        KClass = KNeighborsClassifier()
        KClass.fit(self.x_train,self.y_train)
        
        PerClass = Perceptron()
        PerClass.fit(self.x_train,self.y_train)
        
        Gradclass_err = accuracy_score(self.y_test, Gradclass.predict(self.x_test))
        RandForclass_err = accuracy_score(self.y_test, RandForclass.predict(self.x_test))
        DecTreeclass_err = accuracy_score(self.y_test, DecTreeclass.predict(self.x_test))
        SVCclass_err = accuracy_score(self.y_test, SVCclass.predict(self.x_test))
        LogReg_err = accuracy_score(self.y_test, search.predict(self.x_test))
        MLPClass_err = accuracy_score(self.y_test, MLPClass.predict(self.x_test))
        KClass_err = accuracy_score(self.y_test, KClass.predict(self.x_test))
        PerClass_err = accuracy_score(self.y_test, PerClass.predict(self.x_test))

        print('Gradclass',Gradclass_err)
        print('RandForclass',RandForclass_err)
        print('DecTreeclass',DecTreeclass_err)
        print('SVCclass',SVCclass_err)
        print('LogReg',LogReg_err)
        print('MLPClass',MLPClass_err)
        print('KClass',KClass_err)
        print('PerClass',PerClass_err)


def main():
    start_time = time.time()
    cfb_class = cfb()
    cfb_class.input_arg()
    cfb_class.get_teams(2021)
    cfb_class.split()
    cfb_class.machine()
    print("--- %s seconds ---" % (time.time() - start_time))
if __name__ == '__main__':
    main()
    
