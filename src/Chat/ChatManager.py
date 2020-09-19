from StateManager import *
from ResRecommendation import *
import pandas as pd


class ChatManager:

    def __init__(self, models, data):
        # Define properties
        self.models = models

        # Get the data for restaurant recommendations
        self.data = data

        # Define preferences
        pref = {
            'pricerange': '',
            'area': '',
            'food': ''
        }
        self.pref_df = pd.DataFrame(pref, index=[0])

        self.recommendation_list = ResRecommendation(self.data, self.pref_df)
        self.restaurant = self.recommendation_list[0]

        # Manage states
        self.state = State.S1
        self.__state_manager = StateManager()

        # Load the System utterances
        self.sys_utter = {}

        with open('assets/sys_utterances.txt', 'r') as inf:
            for line in inf:
                line = line.replace('\n', '')
                keys = line.split(' ')
                self.sys_utter[keys[0]] = ' '.join(keys[1:])

        # Print the first system message
        print(self.sys_utter['welcome'])

    def run(self):

        # Start the chat loop
        while True:
            # Check system state and preferences
            self.SystemStateUtterance()

            # Ask user for input
            self.user_input = input('-----> ')

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(self.user_input)
            new_state = self.__state_manager.processState(self.state, utterance)

            # TODO: for now basic talking stuff 
            if utterance == 'inform' or 'requalts':
                
                # Update preferences and state
                new_preferences = self.models.extractPreference(self.user_input)

                # if new_preferences

                # Change preferences where necessary
                if new_preferences['food'] != '':
                    self.pref_df.at['0', 'food'] = new_preferences['food']

                if new_preferences['area'] != '':
                    self.pref_df.at['0', 'area'] = new_preferences['area']

                if new_preferences['pricerange'] != '':
                    self.pref_df.at['0', 'pricerange'] = new_preferences['pricerange']

                # Update the system state
                # if new_state == State.S4 and self.state == State.S3 and

            print('')
            print('utterance: ')
            print(utterance)
            print('new preference: ')
            print(new_preferences)
            print('current state: ')
            print(self.state)
            print('new state: ')
            print(new_state)

            self.state = new_state
            self.old_utterance = utterance 
            self.old_input = self.user_input

            if self.state == State.S5:
                print(self.sys_utter['thankyoubye'])
                break


    def SystemStateUtterance(self):
        # Check whether the preferences are filled
        food = True if self.pref_df['food'].tolist()[0] != '' else False
        area = True if self.pref_df['area'].tolist()[0] != '' else False
        price = True if self.pref_df['pricerange'].tolist()[0] != '' else False #if no price preference, then it is true 

        # Check the state
        if self.state == State.S1:
            self.rsp = self.sys_utter['state1']
            print(self.rsp)

        if self.state == State.S2 and food:
            self.rsp = self.sys_utter['askfood']
            print(self.rsp)

        if self.state == State.S2 and area:
            self.rsp = self.sys_utter['askarea']
            print(self.rsp)

        if self.state == State.S2 and price:
            self.rsp = self.sys_utter['askprice']
            print(self.rsp)
                
        if self.old_utterance == 'ack':
            pass
        
        if self.old_utterance == 'affirm':
            if self.state == State.S4:
                if len(self.recommendation_list) == 0:
                    self.rsp = self.sys_utter['noresults']
                    print(self.rsp)
                else:
                    self.rsp = self.sys_utter['suggestrest'].replace('restaurant_name', self.restaurant)
                    print(self.rsp)
        
        if self.old_utterance == 'confirm': 
            if self.state == State.S4:
                if len(self.recommendation_list) == 0:
                    self.rsp = self.sys_utter['noresults']
                    print(self.rsp)
                else:
                    self.rsp = self.sys_utter['suggestrest'].replace('restaurant_name', self.restaurant)
                    print(self.rsp)
        
        if self.old_utterance == 'deny':
            pass
        
        ##if self.old_utterance == 'hello':
        # This will automatically go to state 1

        #if self.old_utterance == 'null':
        # Looking at the data this reponse depends on the previous utterance of the system 

        if self.old_utterance == 'repeat':
            print(self.rsp)
        
        if self.old_utterance == 'requalts':
            if 'anything' in self.user_input:
                self.rsp = self.sys_utter['suggestrest'].replace('restaurant_name', self.restaurant.restaurantname[1])


        
        if self.old_utterance == 'request':
            if self.state == State.S4: 
                if 'phone' in self.user_input:
                    self.rsp = self.sys_utter['reqphone'].replace('phone_number', self.restaurant.phone)
                    print(self.rsp)
                if 'post' in self.user_input:
                    self.rsp = self.sys_utter['reqpost'].replace('post_code', self.restaurant.postcode)
                    print(self.rsp)
                if 'food' in self.user_input:
                    self.rsp = self.sys_utter['reqfood'].replace('food_type', self.restaurant.food)
                    print(self.rsp)
                if 'address' in self.user_input:
                    self.rsp = self.sys_utter['reqphone'].replace('phone_number', self.restaurant.address)
                    print(self.rsp)
        
        
        if self.old_utterance == 'reqmore':
            if self.state == State.S4: 
                if len(self.recommendation_list) == 1:
                    self.rsp = self.sys_utter['noresults']
                    print(self.rsp)
                else:
                    self.restaurant = self.recommendation_list[1]
                    self.rsp = self.sys_utter['suggestrest'].replace('restaurant_name', self.restaurant.restaurantname[1])
                    print(self.rsp)
        
        #if self.old_utterance == 'restart':
        # This will automatically go to state1 again 
            








