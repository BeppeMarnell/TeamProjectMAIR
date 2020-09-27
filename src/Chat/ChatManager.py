from Chat.StateManager import State, StateManager
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
        #with open('sys_utterances.txt', 'r') as inf:
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

            self.SystemStateUtterance()

            if self.state == State.S1:
                # Define preferences
                pref = {
                    'pricerange': '',
                    'area': '',
                    'food': ''
                }
                self.pref_df = pd.DataFrame(pref, index=[0])
            
            # S5 is the end state, therefore terminate the program
            if self.state == State.S5:
                break

            # Ask user for input
            user_input = input('-----> ')

            #check restaurant recommendation 

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(user_input)
            print(utterance)

            self.react_to_utterance(utterance, user_input)

            new_state = self.__state_manager.processState(self.state, utterance, self.pref_df)


            # if new state is S3, look up possible restaurants, that will be recommended in self.SystemStateUtterance()
            # ensure that current state is either S3 or the utterance asks for another result
            # otherwise, it would recommend a different restaurant even though the user just asked for confirmation
            if new_state == State.S2 and self.state == State.S3 and utterance == 'deny' and user_input == 'wrong':
                print('-----> We can restart if it is wrong')
            
            elif new_state == State.S2 and self.state == State.S3 and utterance == 'deny':
                print('-----> Okay then we will take that into account')

            if new_state == State.S3 and (self.state != State.S3 or utterance == 'reqmore' or utterance == 'reqalts'):
                self.models.recommend(self.pref_df)

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

            self.models.lookup_in_restaurant_info(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)
            
            else:
                self.print_text = self.sys_utter['askfood']
                print(self.print_text)
                return

        if self.state == State.S2 and not area:

            self.models.lookup_in_restaurant_info(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)
            
            else: 
                self.print_text = self.sys_utter['askarea']
                print(self.print_text)
                return

        if self.state == State.S2 and not price:

            self.models.lookup_in_restaurant_info(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)


            # If the length of the restaurant recommendations is >1, continue normally 
            else:
                self.print_text = self.sys_utter['askprice']
                print(self.print_text)
                return

        # Recommend until the recommendationlist is empty
        if self.state == State.S3:
            if len(self.models.recommendation) == 0:
                # Suggest alternative options if there are no options
                self.Suggest_Res(self.pref_df)
                
            elif len(self.models.recommendation) == 1 and self.models.recommendation[0] == -1:
                self.print_text = self.sys_utter['nomoreresults']
                print(self.print_text)
            else:
                self.print_text = self.sys_utter['suggestrest'].replace('restaurant_name',
                                                                        self.models.recommendation['restaurantname'])
                print(self.print_text)
            return

        if self.state == State.S5:
            self.print_text = self.sys_utter['bye']
            print(self.print_text)
            return

    def react_to_utterance(self, utterance, user_input):
        if utterance == 'ack':
            # same as affirm
            if self.state == State.S3:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                   self.models.recommendation['restaurantname'])
                print(self.print_text)
                return

        if utterance == 'affirm':
            # same as ack
            if self.state == State.S3:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                   self.models.recommendation['restaurantname'])
                print(self.print_text)
                return

        if utterance == 'bye':
            # don't need to do anything as it will automatically move to state S5 and print goodbye message
            return

        if utterance == 'confirm':
            food_pref = self.pref_df['food'].tolist()[0]
            area_pref = self.pref_df['area'].tolist()[0]
            price_pref = self.pref_df['pricerange'].tolist()[0]
            confirmtrue = 'confirmtrue'
            confirmfalse = 'confirmfalse'
            recommend = False

            if (self.state == State.S3 or self.state == State.S4) and len(self.models.recommendation) != 0 \
                    and self.models.recommendation[0] != -1:
                # if user has restaurant recommended, use the info from that place rather than the search preference
                food_pref = self.models.recommendation['food']
                area_pref = self.models.recommendation['area']
                price_pref = self.models.recommendation['pricerange']
                confirmtrue = 'confirmtruerest'
                confirmfalse = 'confirmfalserest'
                # set recommend to true if there is currently a recommended restaurant
                recommend = True

            # Update preferences and state
            new_preferences = self.models.extractPreference(user_input)
            # check what preference to confirm
            food = True if new_preferences['food'] != '' else False
            area = True if new_preferences['area'] != '' else False
            price = True if new_preferences['pricerange'] != '' else False

            # check if the preference is correct
            food_correct = True if food_pref == new_preferences['food'] else False
            area_correct = True if area_pref == new_preferences['area'] else False
            price_correct = True if price_pref == new_preferences['pricerange'] else False

            # check that preference is not empty
            food_given = True if food_pref != '' else False
            area_given = True if area_pref != '' else False
            price_given = True if price_pref != '' else False

            if food:
                if food_correct:
                    text = self.sys_utter[confirmtrue].replace('preference_name', 'type')\
                        .replace('preference_value', food_pref)
                elif food_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'type')\
                        .replace('preference_value', food_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'type of restaurant')\
                        .replace('preference_value', 'not specified')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])
                print(text)

            if area:
                if area_correct:
                    text = self.sys_utter[confirmtrue].replace('preference_name', 'area')\
                        .replace('preference_value', area_pref)
                elif area_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'area')\
                        .replace('preference_value', area_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'area')\
                        .replace('preference_value', 'not specified')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])
                print(text)

            if price:
                if price_correct:
                    text = self.sys_utter[confirmtrue].replace('preference_name', 'price')\
                        .replace('preference_value', price_pref)
                elif price_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'price')\
                        .replace('preference_value', price_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'price')\
                        .replace('preference_value', 'not specified')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])
                print(text)
            return

        if utterance == 'deny':
            user_input_split = user_input.split()
            for i in user_input_split: 
                if i == 'dont':
                    for preferences in ['food', 'area', 'pricerange']:
                        if self.pref_df[preferences].tolist()[0] in user_input:
                            self.pref_df[preferences] = ''
                            self.models.restaurants = []
                            return

                if i == 'wrong':
                    for preferences in ['food', 'area', 'pricerange']:
                        self.pref_df[preferences] = ''
                        self.models.restaurants = []
                        return 

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

            # When 'not' is mentioned 
            if 'not' in user_input:
                for preferences in self.pref_df:
                    if preferences in user_input:
                        self.pref_df[preferences] = ''
                        self.models.restaurant = []

            # no in any area or no i want korean food
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
            # don't need to do anything, as it is already updated in the run method (if new state == S3)
            return

        if utterance == 'request':
            # evaluate the utterance if the user asks for more information (phone number, address, ...)
            if self.state == State.S4:
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

    # Function to suggest alternatives 
    def Suggest_Res(self, preferences):

        # If a preference is filled, choose one preference to suggest alternatives. Set to other two at 'any'. 
        if preferences.loc[0]['food'] != 'any' or preferences.loc[0]['food'] != '':
            self.pref_df['area'] = 'any'
            self.pref_df['pricerange'] = 'any'
            self.models.lookup_in_restaurant_info(self.pref_df)
            self.models.recommend(self.pref_df)

        elif preferences.loc[0]['area'] != 'any' or preferences.loc[0]['area'] != '':
            self.pref_df['food'] = 'any'
            self.pref_df['pricerange'] = 'any'
            self.models.lookup_in_restaurant_info(self.pref_df)
            self.models.recommend(self.pref_df)
        
        elif preferences.loc[0]['pricerange'] != 'any' or preferences.loc[0]['pricerange'] != '':
            self.pref_df['area'] = 'any'
            self.pref_df['food'] = 'any'
            self.models.lookup_in_restaurant_info(self.pref_df)
            self.models.recommend(self.pref_df)

        # Suggest start over or the alternative 
        print('-----> There are no results for your preferences. You can type start over or look at the following alternative')

        alt_1 = self.sys_utter['alternatives'].replace('restaurant_name', self.models.recommendation['restaurantname'])\
                        .replace('food_name', self.models.recommendation['food']).replace('area_name', self.models.recommendation['area']).replace('price_range', self.models.recommendation['pricerange'])
        
        #self.models.recommend(self.pref_df)
        print(alt_1)
        print('-----> If you would like more alternatives, request more options. Otherwise, confirm the alternative please!')

