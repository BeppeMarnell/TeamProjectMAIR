import ChatManager 
import StateManager
import numpy as np 
import pandas as pd

class ResRecommendation :

    def __init__(self, data, preferences):
        
        #Data contains data from datasetloader(), like restaurant_info_df
        self.data = data 
        # Preferences is a dataframe from chatmanager 
        self.preferences = preferences 
     
        self.rest_recom_df = pd.Dataframe(self.preferences, index=[0])

        if self.rest_recom_df['pricerange'] != 0 & self.rest_recom_df['area'] != 0 & self.rest_recom_df['food'] != 0:

            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange == self.preferences.pricerange & self.data.restaurant_info_df.area == self.preferences.area & self.data.restaurant_info_df.food == self.preferences.food)]

            else:
                if self.rest_recom_df['pricerange'] == 0 :
                    self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.area = self.preferences.area & self.data.restaurant_info_df.food = self.preferences.food)]
                
                if self.rest_recom_df['area']


