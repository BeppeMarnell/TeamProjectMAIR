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
        self.print_text = ""

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

            if self.state == State.S1:
                # Define preferences
                pref = {
                    'pricerange': '',
                    'area': '',
                    'food': ''
                }
                self.pref_df = pd.DataFrame(pref, index=[0])

            # S6 is the end state, therefore terminate the program
            if self.state == State.S6:
                break

            # Ask user for input
            user_input = input('-----> ')

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(user_input)

            self.react_to_utterance(utterance, user_input)

            # Update the system state
            # if new_state == State.S4 and self.state == State.S3 and

            new_state = self.__state_manager.processState(self.state, utterance, self.pref_df)

            # if new state is S4, look up possible restaurants, that will be recommended in self.SystemStateUtterance()
            # ensure that current state is either S4 or the utterance asks for another result
            # otherwise, it would recommend a different restaurant even though the user just asked for confirmation
            if new_state == State.S4 and (self.state != State.S4 or utterance == 'reqmore' or utterance == 'reqalts'):
                self.models.recommend(self.pref_df)

            # print('')
            # print('utterance: ')
            # print(utterance)
            # # print(new_preferences)
            # print('preference: ')
            # print(self.pref_df.loc[0])
            # print('current state: ')
            # print(self.state)
            # print('new state: ')
            # print(new_state)

            self.state = new_state

    def SystemStateUtterance(self):
        # Check whether the preferences are filled
        food = True if self.pref_df['food'].tolist()[0] != '' else False
        area = True if self.pref_df['area'].tolist()[0] != '' else False
        price = True if self.pref_df['pricerange'].tolist()[0] != '' else False

        # Check the state
        if self.state == State.S1:
            self.print_text = self.sys_utter['state1']
            print(self.print_text)
            return

        if self.state == State.S2 and not food:
            self.print_text = self.sys_utter['askfood']
            print(self.print_text)
            return

        if self.state == State.S2 and not area:
            self.print_text = self.sys_utter['askarea']
            print(self.print_text)
            return

        if self.state == State.S2 and not price:
            self.print_text = self.sys_utter['askprice']
            print(self.print_text)
            return

        if self.state == State.S4:
            if len(self.models.recommendation) == 0:
                self.print_text = self.sys_utter['noresults']

            elif len(self.models.recommendation) == 1 and self.models.recommendation[0] == -1:
                self.print_text = self.sys_utter['nomoreresults']
            else:
                self.print_text = self.sys_utter['suggestrest'].replace('restaurant_name',
                                                                        self.models.recommendation['restaurantname'])
            print(self.print_text)
            return

        if self.state == State.S6:
            self.print_text = self.sys_utter['bye']
            print(self.print_text)
            return

    def react_to_utterance(self, utterance, user_input):
        if utterance == 'ack':
            # same as affirm
            if self.state == State.S4:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                   self.models.recommendation['restaurantname'])
                print(self.print_text)
                return

        if utterance == 'affirm':
            # same as ack
            if self.state == State.S4:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                   self.models.recommendation['restaurantname'])
                print(self.print_text)
                return

        if utterance == 'bye':
            # don't need to do anything as it will automatically move to state S6 and print goodbye message
            return

        if utterance == 'confirm':
            # Update preferences and state
            new_preferences = self.models.extractPreference(user_input)
            #print(new_preferences)
            # check what preference to confirm
            food = True if new_preferences['food'] != '' else False
            area = True if new_preferences['area'] != '' else False
            price = True if new_preferences['pricerange'] != '' else False

            # check if the preference is correct
            food_correct = True if self.pref_df['food'].tolist()[0] == new_preferences['food'] else False
            area_correct = True if self.pref_df['area'].tolist()[0] == new_preferences['area'] else False
            price_correct = True if self.pref_df['pricerange'].tolist()[0] == new_preferences['pricerange'] else False

            # check that preference is not empty
            food_given = True if self.pref_df['food'].tolist()[0] != '' else False
            area_given = True if self.pref_df['area'].tolist()[0] != '' else False
            price_given = True if self.pref_df['pricerange'].tolist()[0] != '' else False

            if food:
                if food_correct:
                    print(self.sys_utter['confirmtrue'].replace('preference_name', 'restaurant').
                          replace('preference_value', self.pref_df['food'].tolist()[0]))
                elif food_given:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'restaurant').
                          replace('preference_value', self.pref_df['food'].tolist()[0]))
                else:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'type of restaurant').
                          replace('preference_value', 'not specified'))

            if area:
                if area_correct:
                    print(self.sys_utter['confirmtrue'].replace('preference_name', 'area').
                          replace('preference_value', self.pref_df['area'].tolist()[0]))
                elif area_given:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'area').
                          replace('preference_value', self.pref_df['area'].tolist()[0]))
                else:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'area').
                          replace('preference_value', 'not specified'))

            if price:
                if price_correct:
                    print(self.sys_utter['confirmtrue'].replace('preference_name', 'price').
                          replace('preference_value', self.pref_df['pricerange'].tolist()[0]))
                elif price_given:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'price').
                          replace('preference_value', self.pref_df['pricerange'].tolist()[0]))
                else:
                    print(self.sys_utter['confirmfalse'].replace('preference_name', 'price').
                          replace('preference_value', 'not specified'))
            return

        if utterance == 'deny':
            # TODO? This utterance never appears in the dialog_acts
            pass

        if utterance == 'hello':
            # don't need to do anything, will automatically restart the conversation
            return

        if utterance == 'inform':
            # Update preferences and state
            new_preferences = self.models.extractPreference(user_input)
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
            return

        if utterance == 'negate':
            # TODO add possibility to choose "not korean food" or "not in the center"
            # new_preferences = self.models.negative_preferences(user_input)
            return

        if utterance == 'null':
            # don't need to do anything, as the text for misunderstanding will be printed if command was not understood
            # important: use pass not return here to let it print sys_utter['misunderstanding']
            pass

        if utterance == 'repeat':
            print(self.print_text)
            return

        if utterance == 'reqalts':
            # same as inform
            new_preferences = self.models.extractPreference(user_input)
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
            return

        if utterance == 'reqmore':
            # don't need to do anything, as it is already updated in the run method (if new state == S4)
            return

        if utterance == 'request':
            # evaluate the utterance if the user asks for more information (phone number, address, ...)
            if self.state == State.S5:
                details = self.models.extract_details(user_input)
                for element in details:
                    print(self.sys_utter['details'].replace('detail_type', element[0])
                          .replace('detail_info', element[1]))
                return

        if utterance == 'restart':
            self.print_text = self.sys_utter['restart']
            print(self.print_text)
            return

        if utterance == 'thankyou':
            # don't need to do anything, as it will automatically move to final state and print bye utterance
            return

        self.print_text = self.sys_utter['misunderstanding']
        print(self.print_text)
        return
