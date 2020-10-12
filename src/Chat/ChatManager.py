try:
    from Chat.StateManager import State, StateManager
    from Rules import Rules
except ImportError:
    from src.Chat.StateManager import State, StateManager
    from src.Rules import Rules
import pandas as pd
import time


class ChatManager:

    def __init__(self, models, group, phrase_style="", mess_caps=""):
        # Define properties
        self.models = models
        self.rules = Rules()

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

        # Save last printed text for repeat utterance
        self.print_text = ""

        # Load the System utterances
        self.sys_utter = {}

        if phrase_style == "informal":
            file_name = "assets/inf_sys_utterances.txt"
        else:
            file_name = 'assets/sys_utterances.txt'

        with open(file_name, 'r') as inf:
            for line in inf:
                line = line.replace('\n', '')
                keys = line.split(' ')
                if mess_caps == "caps":
                    self.sys_utter[keys[0]] = ' '.join(keys[1:]).upper()
                else:
                    self.sys_utter[keys[0]] = ' '.join(keys[1:])
        if group:
            self.delay = True
            self.delay_time = 0
            self.delay_mess = False
            if group[0] == "G1NOM":
                if group[1] == "1":
                    self.delay_time = 0.1
                    self.delay_mess = False
                elif group[1] == "2":
                    self.delay_time = 0.1
                    self.delay_mess = True
                else:
                    print("Warning: task number not defined")
            if group[0] == "G1MNO":
                if group[1] == "1":
                    self.delay_time = 0.1
                    self.delay_mess = True
                elif group[1] == "2":
                    self.delay_time = 0.1
                    self.delay_mess = False
                else:
                    print("Warning: task number not defined")
            if group[0] == "G2NOM":
                if group[1] == "1":
                    self.delay_time = 1.0
                    self.delay_mess = False
                elif group[1] == "2":
                    self.delay_time = 1.0
                    self.delay_mess = True
                else:
                    print("Warning: task number not defined")
            if group[0] == "G2MNO":
                if group[1] == "1":
                    self.delay_time = 1.0
                    self.delay_mess = True
                elif group[1] == "2":
                    self.delay_time = 1.0
                    self.delay_mess = False
                else:
                    print("Warning: task number not defined")
            if group[0] == "G3NOM":
                if group[1] == "1":
                    self.delay_time = 10.0
                    self.delay_mess = False
                elif group[1] == "2":
                    self.delay_time = 10.0
                    self.delay_mess = True
                else:
                    print("Warning: task number not defined")
            if group[0] == "G3MNO":
                if group[1] == "1":
                    self.delay_time = 10.0
                    self.delay_mess = True
                elif group[1] == "2":
                    self.delay_time = 10.0
                    self.delay_mess = False
                else:
                    print("Warning: task number not defined")
        else:
            print("Warning: No group has been given.")
            self.delay = False

        # Print the first system message
        print(self.sys_utter['welcome'])

    def run(self):
        # Start the chat loop
        while True:

            if self.delay:
                if self.delay_mess:
                    print(self.sys_utter['loading'])
                time.sleep(self.delay_time)

            # Check system state and preferences
            self.systemStateUtterance()

            if self.state == State.S1:
                # Define preferences
                # necessary if user wants to start from beginning again
                pref = {
                    'pricerange': '',
                    'area': '',
                    'food': ''
                }
                self.pref_df = pd.DataFrame(pref, index=[0])
                self.models.index = -1

            # S5 is the end state, therefore terminate the program
            if self.state == State.S5:
                break

            # Ask user for input
            user_input = input('-----> ')

            # Evaluate inputted utterance and check the next state
            utterance = self.models.evalueNewUtterance(user_input)
            # print(utterance)

            # React based on what utterance
            self.reactToUtterance(utterance, user_input)

            # Use state manager to set new state
            new_state = self.__state_manager.processState(self.state, utterance, self.pref_df)

            # Print extra message to inform user that deny utterance was understood.
            if new_state == State.S2 and self.state == State.S3 and utterance == 'deny' and user_input == 'wrong':
                print('-----> We will restart because it is wrong')

            elif new_state == State.S2 and self.state == State.S3 and utterance == 'deny':
                print('-----> Okay then we will take that into account')

            # if new state is S3, look up possible restaurants, that will be recommended in self.SystemStateUtterance()
            # ensure that current state is either not S3 or the utterance asks for another result
            # otherwise, it would recommend a different restaurant even though the user just asked for confirmation
            if new_state == State.S3 and (self.state != State.S3 or utterance == 'reqmore' or utterance == 'reqalts'
                                          or utterance == 'negate'):
                self.models.recommend(self.pref_df)

            # Prints that can be uncommented for debugging (show utterance, state, preferences, new state)
            # print('')
            # print('utterance: ')
            # print(utterance)
            # print('preference: ')
            # print(self.pref_df.loc[0])
            # print('current state: ')
            # print(self.state)
            # print('new state: ')
            # print(new_state)

            self.state = new_state

    def systemStateUtterance(self):
        # Function that prints a message to the user at the beginning of each state to either ask a question
        # or inform user about the thing he requested in the previous iteration

        # Check whether the preferences are filled
        food = True if self.pref_df['food'].tolist()[0] != '' else False
        area = True if self.pref_df['area'].tolist()[0] != '' else False
        price = True if self.pref_df['pricerange'].tolist()[0] != '' else False

        if self.state == State.S1:
            self.print_text = self.sys_utter['state1']
            print(self.print_text)
            return

        # ask for food if preference is not set and multiple restaurants apply for other preferences
        if self.state == State.S2 and not food:

            self.models.lookupInRestaurantInfo(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)

            # If the length of the restaurant recommendations is >1, continue normally
            else:
                self.print_text = self.sys_utter['askfood']
                print(self.print_text)
                return

        # ask for area if preference is not set and multiple restaurants apply for other preferences
        if self.state == State.S2 and not area:

            self.models.lookupInRestaurantInfo(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)

            # If the length of the restaurant recommendations is >1, continue normally
            else:
                self.print_text = self.sys_utter['askarea']
                print(self.print_text)
                return

        # ask for price if preference is not set and multiple restaurants apply for other preferences
        if self.state == State.S2 and not price:

            self.models.lookupInRestaurantInfo(self.pref_df)

            # If there are 0 or 1 restaurants for the preferences, go to state 3
            if len(self.models.restaurants) <= 1:
                self.state = State.S3
                self.models.recommend(self.pref_df)

            # If the length of the restaurant recommendations is >1, continue normally
            else:
                self.print_text = self.sys_utter['askprice']
                print(self.print_text)
                return

        if self.state == State.S2 and food and area and price:
            # when changing a preference in state 3, the user gets send back to state 2.
            # If however, all preferences are set again,
            # the user gets asked this irrelevant question to avoid an empty line, where user has to press enter
            # ask user to either confirm their choice for food, area or price
            if self.pref_df['food'].tolist()[0] != 'any':
                self.print_text = self.sys_utter['confirmquestion'].replace('preference_name', 'food')\
                    .replace('preference_value', self.pref_df['food'].tolist()[0])
                print(self.print_text)
            elif self.pref_df['area'].tolist()[0] != 'any':
                self.print_text = self.sys_utter['confirmquestion'].replace('preference_name', 'area') \
                    .replace('preference_value', self.pref_df['area'].tolist()[0])
                print(self.print_text)
            elif self.pref_df['pricerange'].tolist()[0] != 'any':
                self.print_text = self.sys_utter['confirmquestion'].replace('preference_name', 'pricerange') \
                    .replace('preference_value', self.pref_df['pricerange'].tolist()[0])
                print(self.print_text)
            return

        # recommend restaurant
        if self.state == State.S3:
            if len(self.models.recommendation) == 0:
                # Suggest alternative options if there are no options
                self.suggestRes(self.pref_df)
                print(self.print_text)

            elif len(self.models.recommendation) == 1 and self.models.recommendation[0] == -1:
                # recommendation is set to -1 if the user looped through all recommended restaurants.
                # Warning will be printed to make user aware of this
                self.print_text = self.sys_utter['nomoreresults']
                print(self.print_text)
            else:
                # suggest possible restaurant
                self.print_text = self.sys_utter['suggestrest']\
                    .replace('restaurant_name', self.models.recommendation['restaurantname'])\
                    .replace('RESTAURANT_NAME',self.models.recommendation['restaurantname'])

                # Compute implications
                consequents, reason = self.rules.solveRule(self.models.recommendation)

                # Inform about the implications
                for cons in consequents:
                    if consequents[cons] is not None:
                        self.print_text += '\n'
                        text = 'not '
                        if str(cons) == 'children' or str(cons) == 'long time':
                            text = 'not for '

                        if consequents[cons]:
                            self.print_text += self.sys_utter['askforimplication'].replace('qualities', cons)\
                                .replace('QUALITIES', cons)
                        else:
                            self.print_text += self.sys_utter['askforimplication']\
                                .replace('qualities', ''.join([text, cons])).replace('QUALITIES', ''.join([text, cons]))

                # "What about ....
                print(self.print_text)
            return

        if self.state == State.S5:
            self.print_text = self.sys_utter['bye']
            print(self.print_text)
            return

    def reactToUtterance(self, utterance, user_input):
        # Function that calls the correct function or prints the correct system utterance
        # based on the classified utterance.

        if utterance == 'ack':
            # same as affirm, kept separate to ease expandability in future, if the usage of one utterance changes
            if self.state == State.S2:
                # obligatory question will be asked to user, if he responds yes, go to state 3
                # necessary, if user changes one preference in state 3 and goes back to state 2,
                # even though all preferences are set again
                return
            if self.state == State.S3 and len(self.models.recommendation) != 0 and self.models.recommendation[0] != -1:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                        self.models.recommendation['restaurantname'])\
                                                                        .replace('RESTAURANT_NAME', self.models
                                                                                 .recommendation['restaurantname'])
                print(self.print_text)
                return

        if utterance == 'affirm':
            # same as ack, kept separate to ease expandability in future, if the usage of one utterance changes
            if self.state == State.S2:
                # obligatory question will be asked to user, if he responds yes, go to state 3
                # necessary, if user changes one preference in state 3 and goes back to state 2,
                # even though all preferences are set again
                return
            if self.state == State.S3 and len(self.models.recommendation) != 0 and self.models.recommendation[0] != -1:
                self.print_text = self.sys_utter['affirm'].replace('restaurant_name',
                                                                        self.models.recommendation['restaurantname'])\
                                                                        .replace('RESTAURANT_NAME', self.models
                                                                                 .recommendation['restaurantname'])
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

            # Extract preference to confirm
            new_preferences = self.models.extractPreference(user_input, self.sys_utter)

            # check what preference did the user ask for
            # example input: is the restaurant expensive?
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
                        .replace('preference_value', food_pref).replace('PREFERENCE_NAME', 'TYPE')\
                        .replace('PREFERENCE_VALUE', food_pref)
                elif food_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'type')\
                        .replace('preference_value', food_pref).replace('PREFERENCE_NAME', 'TYPE')\
                        .replace('PREFERENCE_VALUE', food_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'type of restaurant')\
                        .replace('preference_value', 'not specified').replace('PREFERENCE_NAME', 'TYPE OF RESTAURANT')\
                        .replace('PREFERENCE_VALUE', 'NOT SPECIFIED')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])\
                               .replace('RESTAURANT_NAME', self.models.recommendation['restaurantname'])
                print(text)

            if area:
                if area_correct:
                    text = self.sys_utter[confirmtrue].replace('preference_name', 'area')\
                        .replace('preference_value', area_pref).replace('PREFERENCE_NAME', 'AREA')\
                        .replace('PREFERENCE_VALUE', area_pref)
                elif area_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'area')\
                        .replace('preference_value', area_pref).replace('PREFERENCE_NAME', 'AREA')\
                        .replace('PREFERENCE_VALUE', area_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'area')\
                        .replace('preference_value', 'not specified').replace('PREFERENCE_NAME', 'AREA')\
                        .replace('PREFERENCE_VALUE', 'NOT SPECIFIED')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])\
                               .replace('RESTAURANT_NAME', self.models.recommendation['restaurantname'])
                print(text)

            if price:
                if price_correct:
                    text = self.sys_utter[confirmtrue].replace('preference_name', 'price')\
                        .replace('preference_value', price_pref).replace('PREFERENCE_NAME', 'PRICE')\
                        .replace('PREFERENCE_VALUE', price_pref)
                elif price_given:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'price')\
                        .replace('preference_value', price_pref).replace('PREFERENCE_NAME', 'PRICE')\
                        .replace('PREFERENCE_VALUE', price_pref)
                else:
                    text = self.sys_utter[confirmfalse].replace('preference_name', 'price')\
                        .replace('preference_value', 'not specified').replace('PREFERENCE_NAME', 'PRICE')\
                        .replace('PREFERENCE_VALUE', 'NOT SPECIFIED')
                if recommend:
                    text = text.replace('restaurant_name', self.models.recommendation['restaurantname'])\
                           .replace('RESTAURANT_NAME', self.models.recommendation['restaurantname'])
                print(text)
            return

        if utterance == 'deny':
            # Wrong
            # I dont want
            user_input_split = user_input.split()
            for i in user_input_split:
                if i == 'dont':
                    for preferences in ['food', 'area', 'pricerange']:
                        if self.pref_df[preferences].tolist()[0] in user_input:
                            # remove preference that was not wanted and reset list of recommended restaurants
                            self.pref_df[preferences] = ''
                            self.models.restaurants = []
                            return

                if i == 'wrong':
                    for preferences in ['food', 'area', 'pricerange']:
                        # remove all preferences and reset list of recommended restaurants
                        self.pref_df[preferences] = ''
                        self.models.restaurants = []
                        return

        if utterance == 'hello':
            # don't need to do anything, will automatically restart the conversation
            return

        if utterance == 'inform':
            # Extract preferences of user
            new_preferences = self.models.extractPreference(user_input, self.sys_utter)

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
            # Extract preferences of user
            new_preferences = self.models.extractPreference(user_input, self.sys_utter)

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

        if utterance == 'null':
            # don't need to do anything, as the text for misunderstanding will be printed if command was not understood
            # important: use pass not return here to let it print sys_utter['misunderstanding']
            pass

        if utterance == 'repeat':
            print(self.print_text)
            return

        if utterance == 'reqalts':
            # same as inform
            new_preferences = self.models.extractPreference(user_input, self.sys_utter)

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
                details = self.models.extractDetails(user_input)
                for element in details:
                    print(self.sys_utter['details'].replace('detail_type', element[0])
                          .replace('detail_info', element[1]).replace('DETAIL_TYPE', element[0])
                          .replace('DETAIL_INFO', element[1]))
                return

        if utterance == 'restart':
            self.print_text = self.sys_utter['restart']
            print(self.print_text)
            return

        if utterance == 'thankyou':
            # don't need to do anything, as it will automatically move to final state and print bye utterance
            return

        # if utterance was not handled above, print message that input was not understood
        # can for example happen, because it is not defined for the current state
        self.print_text = self.sys_utter['misunderstanding']
        print(self.print_text)
        return

    def suggestRes(self, preferences):
        # Function to suggest alternatives for the restaurant

        # If a preference is filled, choose one preference to suggest alternatives. Set the other two to 'any'.
        if preferences.loc[0]['food'] != 'any' or preferences.loc[0]['food'] != '':
            self.pref_df['area'] = 'any'
            self.pref_df['pricerange'] = 'any'
            self.models.lookupInRestaurantInfo(self.pref_df)
            self.models.recommend(self.pref_df)

        elif preferences.loc[0]['area'] != 'any' or preferences.loc[0]['area'] != '':
            self.pref_df['food'] = 'any'
            self.pref_df['pricerange'] = 'any'
            self.models.lookupInRestaurantInfo(self.pref_df)
            self.models.recommend(self.pref_df)

        elif preferences.loc[0]['pricerange'] != 'any' or preferences.loc[0]['pricerange'] != '':
            self.pref_df['area'] = 'any'
            self.pref_df['food'] = 'any'
            self.models.lookupInRestaurantInfo(self.pref_df)
            self.models.recommend(self.pref_df)

        # Suggest start over or the alternative
        self.print_text = self.sys_utter['alt1'] + '\n'

        alt_1 = self.sys_utter['alternatives'].replace('restaurant_name', self.models.recommendation['restaurantname'])\
            .replace('food_name', self.models.recommendation['food'])\
            .replace('area_name', self.models.recommendation['area'])\
            .replace('price_range', self.models.recommendation['pricerange'])\
            .replace('RESTAURANT_NAME', self.models.recommendation['restaurantname']) \
            .replace('FOOD_NAME', self.models.recommendation['food']) \
            .replace('AREA_NAME', self.models.recommendation['area']) \
            .replace('PRICE_RANGE', self.models.recommendation['pricerange'])

        self.print_text += alt_1 + '\n'
        self.print_text += self.sys_utter['alt2']
