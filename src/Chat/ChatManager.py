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
        index = 0
        while True:

            # Check system state and preferences
            self.SystemStateUtterance()

            # S6 is the end state, therefore terminate the program
            if self.state == State.S6:
                break

            # Ask user for input
            user_input = input('-----> ')

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(user_input)

            # Update preferences and state
            new_preferences = self.models.extractPreference(user_input)

            # TODO: for now basic talking stuff
            # Change preferences where necessary
            if new_preferences['food'] != '':
                self.pref_df.at[0, 'food'] = new_preferences['food']
                self.models.restaurants = []

            if new_preferences['area'] != '':
                self.pref_df.at[0, 'area'] = new_preferences['area']
                self.models.restaurants = []

            if new_preferences['pricerange'] != '':
                self.pref_df.at[0, 'pricerange'] = new_preferences['pricerange']
                self.models.restaurants = []

            # evaluate the utterance if the user asks for more information (phone number, address, ...)
            if utterance == 'request' and self.state == State.S5:
                details = self.models.extract_details(user_input)
                for element in details:
                    print(self.sys_utter['details'].replace('detail_type', element[0])
                          .replace('detail_info', element[1]))
            # Update the system state
            # if new_state == State.S4 and self.state == State.S3 and

            new_state = self.__state_manager.processState(self.state, utterance, self.pref_df)

            # if new state is S4, look up possible restaurants, that will be recommended in self.SystemStateUtterance()
            # ensure that current state is either S4 or the utterance asks for another result
            # otherwise, it would recommend a different restaurant even though the user just asked for confirmation
            if new_state == State.S4 and (self.state != State.S4 or utterance == 'reqmore' or utterance == 'reqalts'):
                self.models.recommend(self.pref_df)

            print('')
            print('utterance: ')
            print(utterance)
            print(new_preferences)
            print('preference: ')
            print(self.pref_df.loc[0])
            print('current state: ')
            print(self.state)
            print('new state: ')
            print(new_state)

            self.state = new_state

    def SystemStateUtterance(self):
        # Check whether the preferences are filled
        food = True if self.pref_df['food'].tolist()[0] != '' else False
        area = True if self.pref_df['area'].tolist()[0] != '' else False
        price = True if self.pref_df['pricerange'].tolist()[0] != '' else False

        # Check the state
        if self.state == State.S1:
            print(self.sys_utter['state1'])
            return

        if self.state == State.S2 and not food:
            print(self.sys_utter['askfood'])
            return

        if self.state == State.S2 and not area:
            print(self.sys_utter['askarea'])
            return

        if self.state == State.S2 and not price:
            print(self.sys_utter['askprice'])
            return

        if self.state == State.S4:
            if len(self.models.recommendation) == 0:
                print(self.sys_utter['noresults'])
            elif len(self.models.recommendation) == 1 and self.models.recommendation[0] == -1:
                print(self.sys_utter['nomoreresults'])
            else:
                print(self.sys_utter['suggestrest'].replace('restaurant_name',
                                                            self.models.recommendation['restaurantname']))
            return

        if self.state == State.S6:
            print(self.sys_utter['bye'])
            return
