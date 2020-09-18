from src.Chat.StateManager import State, StateManager
import pandas as pd


class ChatManager:

    def __init__(self, models):
        # Define properties
        self.models = models

        # Define preferences
        pref = {
            'pricerange': '',
            'area': '',
            'food': ''
        }
        self.pref_df = pd.DataFrame(pref, index=[0])

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
            user_input = input('-----> ')

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(user_input)
            new_state = self.__state_manager.processState(self.state, utterance)

            # Update preferences and state
            new_preferences = self.models.extractPreference(user_input)

            # TODO: for now basic talking stuff

            # Change preferences where necessary
            if new_preferences['food'] != '':
                self.pref_df.at[0, 'food'] = new_preferences['food']

            if new_preferences['area'] != '':
                self.pref_df.at[0, 'area'] = new_preferences['area']

            if new_preferences['pricerange'] != '':
                self.pref_df.at[0, 'pricerange'] = new_preferences['pricerange']

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


    def SystemStateUtterance(self):
        # Check whether the preferences are filled
        food = True if self.pref_df['food'].tolist()[0] == '' else False
        area = True if self.pref_df['area'].tolist()[0] == '' else False
        price = True if self.pref_df['pricerange'].tolist()[0] == '' else False

        # Check the state
        if self.state == State.S1:
            print(self.sys_utter['state1'])
            return

        if self.state == State.S2 and food:
            print(self.sys_utter['askfood'])
            return

        if self.state == State.S2 and area:
            print(self.sys_utter['askarea'])
            return

        if self.state == State.S2 and price:
            print(self.sys_utter['askprice'])
            return
