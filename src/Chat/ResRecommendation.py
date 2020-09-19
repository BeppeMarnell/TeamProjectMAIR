import ChatManager 
import StateManager
import numpy as np 
import pandas as pd

class ResRecommendation :

    def __init__(self, data, preferences):
        
        # Data contains data from datasetloader(), like restaurant_info_df
        self.data = data 

        # Preferences is a dataframe from chatmanager 
        self.preferences = preferences      
        self.rest_recom_df = pd.Dataframe(self.preferences, index=[0])

        # If a preference is filled as 'any', then it becomes 0
        self.rest_recom_df = self.rest_recom_df.replace(['any'], 0)

        # If one column == 0 or any, it returns True, otherwise False if none contains 0
        if self.rest_recom_df.isin([0]).any().any() == False:  #['pricerange'] != 0 & self.rest_recom_df['area'] != 0 & self.rest_recom_df['food'] != 0:
            
            # Create a new dataframe with the preferenced pricerange, area and food 
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange == self.preferences.pricerange and self.data.restaurant_info_df.area == self.preferences.area and self.data.restaurant_info_df.food == self.preferences.food)]
           
            #self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange.isin(self.preferences.pricerange) & self.data.restaurant_info_df.area.isin(self.preferences.area) & self.data.restaurant_info_df.food.isin(self.preferences.food)]

        else:
            self.recommend_list = self.AnyPreference()

    def AnyPreference(self):
        
        # If all preferences are missing 
        if self.rest_recom_df['pricerange'] == 0 and self.rest_recom_df['area'] == 0  and self.rest_recom_df['food'] == 0:
            self.recommend_list = self.data.restaurant_info_df
            return self.recommend_list
        
        # If area and food are missing 
        if self.rest_recom_df['pricerange'] != 0 and self.rest_recom_df['area'] == 0  and self.rest_recom_df['food'] == 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange == self.preferences.pricerange)]
            return self.recommend_list

        # If food is missing 
        if self.rest_recom_df['pricerange'] != 0 and self.rest_recom_df['area'] != 0  and self.rest_recom_df['food'] == 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange == self.preferences.pricerange & self.data.restaurant_info_df.area == self.preferences.area)]
            return self.recommend_list

        # If area is missing 
        if self.rest_recom_df['pricerange'] != 0 and self.rest_recom_df['area'] == 0  and self.rest_recom_df['food'] != 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.pricerange == self.preferences.pricerange & self.data.restaurant_info_df.food == self.preferences.food)]
            return self.recommend_list
        
        # If price and food are missing 
        if self.rest_recom_df['pricerange'] == 0 and self.rest_recom_df['area'] != 0  and self.rest_recom_df['food'] == 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.area == self.preferences.area)]
            return self.recommend_list
        
        # If price  is missing 
        if self.rest_recom_df['pricerange'] == 0 and self.rest_recom_df['area'] != 0  and self.rest_recom_df['food'] != 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.area == self.preferences.area & self.data.restaurant_info_df.food == self.preferences.food)]
            return self.recommend_list
        
        # If food is missing 
        if self.rest_recom_df['pricerange'] == 0 and self.rest_recom_df['area'] == 0  and self.rest_recom_df['food'] != 0:
            self.recommend_list = self.data.restaurant_info_df[(self.data.restaurant_info_df.food == self.preferences.food)]
            return self.recommend_list


        





