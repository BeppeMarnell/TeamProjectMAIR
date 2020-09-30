import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import Levenshtein as lev
import nltk
from nltk.corpus import stopwords
import re


class Models:

    def __init__(self, dataset, baseline1=False, baseline2=False):
        # Get the train and test sets
        self.dataset = dataset

        # Prepare some useful data
        self.price_ranges = self.dataset.restaurant_info_df['pricerange'].unique()
        self.areas = self.dataset.restaurant_info_df['area'].unique()
        self.foods = self.dataset.restaurant_info_df['food'].unique()

        self.restaurants = pd.DataFrame()
        self.recommendation = None
        self.index = -1

        self.further_pref = {
            'busy': '',
            'good food': '',
            'long time': '',
            'children': '',
            'romantic': ''
        }

        # TODO: here you can activate and deactivate the models
        self.models = {
            # 'logReg': LogisticRegression(C=100, random_state=0, max_iter=1000),
            # 'decTree': DecisionTreeClassifier(),
            # 'SVM': SVC(gamma='scale', probability=True, C=1),
            'multiNB': MultinomialNB(),
            # 'kNeigh': KNeighborsClassifier(n_neighbors=3)
        }

        # Set some variables

        # TODO: Here you can activate if you'd like one or multiple models at the same time
        # TODO: From task 1.b on, it is not possible to have multiple models
        self.singleModel = True
        self.singleModelName = 'multiNB'  # Default one

        self.baseline1 = baseline1
        self.baseline2 = baseline2

        self.endLoading = False

        # Train the models
        for model in self.models:
            self.models[model].fit(self.dataset.x_train, self.dataset.y_train)
            print(''.join(['-----> Loading model: ', model]))

        # LOGs
        print('-----> All models have been loaded and trained on BOW \n')
        self.endLoading = True

    def showPerformances(self):
        self.endLoading = False

        if self.baseline2:
            print('-----> baseline 2')
            dialog_act = []
            for example in self.dataset.x_test:
                dialog_act.append(self.baseline2_expressions(example))
            accurate = accuracy_score(self.dataset.y_test, dialog_act)
            print(''.join(['-----> Accuracy: ', str(accurate)]))

        if self.singleModel:
            # Calculate performance for single model
            print(''.join(['-----> Model: ', self.models[self.singleModelName]]))
            acc = self.__accuracy(self.models[self.singleModelName])
            aucroc = self.__AUCROC(self.models[self.singleModelName])
            print(''.join(['----->       Accuracy: ', str(acc)]))
            print(''.join(['----->       AUCROC  : ', str(aucroc)]))
            print(''.join(['----->']))

        else:
            # Calculate performance of each model
            for model in self.models:
                print(''.join(['-----> Model: ', model]))
                acc = self.__accuracy(self.models[model])
                aucroc = self.__AUCROC(self.models[model])
                print(''.join(['----->       Accuracy: ', str(acc)]))
                print(''.join(['----->       AUCROC  : ', str(aucroc)]))
                print(''.join(['----->']))

        print('')
        self.endLoading = True

    def __AUCROC(self, model):
        # AUC - ROC curve is a performance measurement for classification problem at various thresholds settings. ROC
        # is a probability curve and AUC represents degree or measure of separability. It tells how much model is
        # capable of distinguishing between classes. Higher the AUC, better the model is at predicting 0s as 0s and
        # 1s as 1s. By analogy, Higher the AUC, better the model is at distinguishing between patients with disease
        # and no disease.

        # One-vs-One and One-vs-Rest ROC AUC scores averaged between macro and weighted by prevalence
        y_prob = model.predict_proba(self.dataset.x_test)

        macro_roc_auc_ovo = metrics.roc_auc_score(self.dataset.y_test, y_prob, multi_class="ovo", average="macro")
        weighted_roc_auc_ovo = metrics.roc_auc_score(self.dataset.y_test, y_prob, multi_class="ovo", average="weighted")
        macro_roc_auc_ovr = metrics.roc_auc_score(self.dataset.y_test, y_prob, multi_class="ovr", average="macro")
        weighted_roc_auc_ovr = metrics.roc_auc_score(self.dataset.y_test, y_prob, multi_class="ovr", average="weighted")

        return (macro_roc_auc_ovo + weighted_roc_auc_ovo + macro_roc_auc_ovr + weighted_roc_auc_ovr) / 4

    def __accuracy(self, model):
        predicted = model.predict(self.dataset.x_test)
        return np.mean(predicted == self.dataset.y_test)

    def setSingleModel(self, singleModel=True, name='multiNB'):
        self.singleModel = singleModel
        self.singleModelName = name

    def evalueNewUtterance(self, utterance):
        # TODO: Implement other baselines in a more thoughtful way
        # Implement baseline
        if self.baseline1:
            return 'inform'

        # Second baseline
        if self.baseline2:
            return self.baseline2_expressions(utterance)

        # Evaluate the new utterance
        if self.singleModel:
            test = self.dataset.count_vect.transform([utterance])
            predicted = self.models[self.singleModelName].predict(test)
            return predicted[0]

        else:
            for model in self.models:
                print(''.join(['-----> Model: ', model]))
                print(''.join(['----->       New utterance: ', utterance]))
                test = self.dataset.count_vect.transform([utterance])
                predicted = self.models[self.singleModelName].predict(test)
                print(''.join(['----->       Evaluated as: ', str(predicted)]))
                print(''.join(['----->']))

        print('')

    def baseline2_expressions(self, utterance):
        # Use regular expressions or key-words to classify the dialog act in baseline 2
        ack = re.search("okay|um|ok|umh|ah", utterance)
        affirm = re.search("yes|right|alright|yeah|perfect|correct|cool|nice|awesome|great|sounds", utterance)
        bye = re.search("good bye|bye|darling|dear|goodb|[a-z]*bye", utterance)
        confirm = re.search("is it|said|yea", utterance)
        deny = re.search("alternative|dont|not|cannot|doesnt|shitty|suck|sucks|hate|wrong|fuck", utterance)
        hello = re.search("^hello|^hi|^hey|^halo", utterance)
        inform = re.search("food|christmas|asian|west|north|east|south|thai[a-z]*|austra[a_z]*|chin[a-z]+|want[a-z]*|ita[a-z]*|exp[a-z]+|veg[e\-i]tarian|recommend|french|information|downtown|looking|searching|help|serve[a-z]+|rest[a-z][a-z]+|viet[a-z]*|seafood|food|turki[a-z]+|cheap|pizza|moder[a-z]+|kitchen|oriental|mexican|child|european", utterance)
        negate = re.search("not|any", utterance)
        null = re.search("hm|sil|mmhmm|ringing|laugh[a-z]*|huh|sigh|missing|inaudible|cough|oh|noise|yawning|tv_noise|uh|background_speech|breath", utterance)
        repeat = re.search("sorry|repeat|again|answer", utterance)
        reqalts = re.search("anything|how about|what about|alternative|different|asian", utterance)
        reqmore = re.search("more|suggestions", utterance)
        request = re.search("their|may|pri[sc]e|wheres|what is|whats|nu[a-z]*|options|ad[a-z]*|post[a-z]*|locat[a-z]+|range|venue", utterance)
        restart = re.search("start over|nevermind|restart", utterance)
        thankyou = re.search("thank you|welcome|thank|thanks|day|good[a-z]*|afternoon", utterance)


        if affirm !=None:
            return 'affirm'

        if ack != None:
            return 'ack'

        if bye !=None:
            return 'bye'

        if confirm != None:
            return 'confirm'

        if deny != None:
            return 'deny'

        if hello != None:
            return 'hello'

        if inform != None:
            return 'inform'

        if negate != None:
            return 'negate'

        if null != None:
            return 'null'

        if repeat != None:
            return 'repeat'

        if reqalts != None:
            return 'reqalts'

        if reqmore != None:
            return 'reqmore'

        if request != None:
            return 'request'

        if restart != None:
            return 'restart'

        if thankyou != None:
            return 'thankyou'

        return 'not found'

    def extractPreference(self, string, sys_utter):
        # Lower the string in input
        string = string.lower()

        # Preference extraction by pricerange, area and food
        pref = {
            'pricerange': '',
            'area': '',
            'food': ''
        }

        # Look for the pricerange in the text
        for price in self.price_ranges:
            if price in string:
                pref['pricerange'] = price
                break

        # Look for the area in the text
        for area in self.areas:
            if area in string:
                pref['area'] = area
                break

        # Look for the food in the text
        for food in self.foods:
            if food in string:
                pref['food'] = food
                break

        # In case the food is not found, use some keyword matching,
        # maybe there is a spelling error

        # keywords matching here

        track_replaced = []

        for missing_pref in ['food', 'area', 'pricerange']:

            if pref[missing_pref] == '':
                keywords = {'food': [['food'], ['restaurant']], 'area': [['in', 'the'], ['area']],
                            'pricerange': [['priced'], ['restaurant'], ['price'], ['pricerange']]}
                keyword_selection = {'food': self.foods, 'area': self.areas, 'pricerange': self.price_ranges}

                # Extract variable before relevant keyword
                words = string.split(" ")

                for poss_keyword in keywords[missing_pref]:
                    if set(poss_keyword).issubset(set(words)):
                        miss_word = ''
                        if missing_pref != 'area':
                            for indx in range(0, len(words)):
                                # if the keyword matches a word in the sentence and doesn't occur
                                # in the set of keywords, it's a match
                                if words[indx] == poss_keyword[0]:
                                    if not any([words[indx - 1]] in sublist for sublist in keywords.values()):
                                        miss_word = words[indx - 1]
                        else:
                            for indx in range(0, len(words)):
                                # for matching 'in' 'the'
                                if indx != 0 and [words[indx-1], words[indx]] == keywords[missing_pref][0]:
                                    if not any([words[indx + 1]] in sublist for sublist in keywords.values()):
                                        miss_word = words[indx + 1]
                                # for matching the other keywords
                                elif words[indx] == keywords[missing_pref][1][0]:
                                    if not any([words[indx - 1]] in sublist for sublist in keywords.values()):
                                        miss_word = words[indx - 1]

                        # rudimentary any preference detection
                        if miss_word == 'any':
                            pref[missing_pref] = 'any'
                            break

                        # possible matches should be at least three characters
                        if len(miss_word) < 3:
                            break

                        # since food and pricerange share the 'restaurant' keyword, check if matching preference
                        # not overlap
                        if missing_pref != 'food' and (pref['food'] == miss_word or miss_word in track_replaced):
                            break

                        if missing_pref != 'pricerange' and \
                                (pref['pricerange'] == miss_word or miss_word in track_replaced):
                            break

                        # Check for matching with Levenshtein distance
                        # more than distance 3 it will fail
                        dst = {
                            '1': [],
                            '2': [],
                            '3': []
                        }

                        # let's check if every misspelled word before the keyword
                        # can be similar to something in the dataset
                        for stuff in keyword_selection[missing_pref]:
                            if lev.distance(stuff, miss_word) <= 3:
                                dst[str(lev.distance(stuff, miss_word))].append(stuff)

                        # finally let's set the preference giving priority to the one with less distance
                        change_check = 0
                        if len(dst['1']):
                            for entry in dst['1']:
                                utterance = self.__patternMatchingRequest(miss_word, entry, sys_utter)
                                if utterance == 'affirm':
                                    pref[missing_pref] = entry
                                    change_check = 1
                                    break

                        elif len(dst['2']):
                            for entry in dst['2']:
                                utterance = self.__patternMatchingRequest(miss_word, entry, sys_utter)
                                if utterance == 'affirm':
                                    pref[missing_pref] = entry
                                    change_check = 1
                                    break

                        elif len(dst['3']):
                            for entry in dst['3']:
                                utterance = self.__patternMatchingRequest(miss_word, entry, sys_utter)
                                if utterance == 'affirm':
                                    change_check = 1
                                    pref[missing_pref] = entry
                                    break

                        # Add something to say that in case the word does not exist the user need to specify it
                        if not change_check:
                            print(sys_utter['word_not_exist'].replace('miss_word', miss_word)
                                  .replace('MISS_WORD', miss_word))
                            print(sys_utter['apologize'])
        return pref

    def __patternMatchingRequest(self, miss_word, entry, sys_utter):
        # If the user writes something that could resemble a word in the dataset,
        # it is asked if the matched word is what the user meant

        print(sys_utter['clarify'].replace('miss_word', miss_word).replace('entry', entry)
              .replace('MISS_WORD', miss_word).replace('ENTRY', entry))
        user_input = input("-----> ")
        utterance = self.evalueNewUtterance(user_input)

        while utterance != 'affirm' and utterance != 'negate':
            if utterance != 'repeat':
                print(sys_utter['repeat_ask'])
            print(sys_utter['clarify'].replace('miss_word', miss_word).replace('entry', entry)
                  .replace('MISS_WORD', miss_word).replace('ENTRY', entry))
            user_input = input("-----> ")
            utterance = self.evalueNewUtterance(user_input)
            print(utterance)

        return utterance

    def get_levenshtein_items(self, miss_words, possible_words):
        # Check for matching with Levenshtein distance
        # more than distance 3 it will fail
        # remove all stopwords to not get a close distance to words like 'the'
        stop_words = set(stopwords.words('english'))
        miss_words = [w for w in miss_words if w not in stop_words]

        dst = {
            '1': [],
            '2': [],
            '3': []
        }
        for miss_word in miss_words:
            # let's check if every misspelled word before food can be similar to something in the dataset
            for word in possible_words:
                if lev.distance(word, miss_word) <= 3:
                    dst[str(lev.distance(word, miss_word))].append(word)
        pref = []
        # finally let's set the preference giving priority to the one with less distance
        if len(dst['1']) >= 1:
            pref = dst['1'][0]
        else:
            if len(dst['2']) >= 1:
                pref = dst['2'][0]
            else:
                if len(dst['3']) >= 1:
                    pref = dst['3'][0]
                else:
                    return ''
                    # TODO set state to request more info (set string saying name is not recognized)
        return pref

    def lookup_in_restaurant_info(self, preferences):
        # Preference is true if it is not filled, so restaurants can already be looked up
        if preferences.loc[0]['food'] == 'any' or preferences.loc[0]['food'] == '':
            food = True
        else:
            food = self.dataset.restaurant_info_df['food'] == preferences.loc[0]['food']
        if preferences.loc[0]['area'] == 'any' or preferences.loc[0]['area'] == '':
            area = True
        else:
            area = self.dataset.restaurant_info_df['area'] == preferences.loc[0]['area']
        if preferences.loc[0]['pricerange'] == 'any' or preferences.loc[0]['pricerange'] == '':
            pricerange = True
        else:
            pricerange = self.dataset.restaurant_info_df['pricerange'] == preferences.loc[0]['pricerange']

        #print("Price", pricerange)

        # prevent from crashing due to all no preferences
        if isinstance(food, bool) and isinstance(area, bool) and isinstance(pricerange, bool) \
                and food and area and pricerange:
            restaurants = self.dataset.restaurant_info_df
        else:
            restaurants = self.dataset.restaurant_info_df.loc[food & area & pricerange]
        #print("Restaurants",restaurants)
        self.restaurants = restaurants.reset_index()

    def recommend_restaurant(self):
        if len(self.restaurants) == 0:
            self.index = -1
            return []
        if len(self.restaurants) <= self.index:
            # set to -1, as it will be increased by one in method below
            self.index = -1
            # return here to execute utterance saying that no more restaurants were found.
            # if another is requested, start over
            return [-1]
        return self.restaurants.loc[self.index]

    def recommend(self, preferences):
        self.index += 1
        if not set(self.restaurants):
            #print(preferences['pricerange'])
            self.lookup_in_restaurant_info(preferences)
        self.recommendation = self.recommend_restaurant()

    def extract_details(self, string):
        string = string.lower()
        requested = []
        details = {"restaurantname": ["name", "restaurantname", "restaurant"],
                   "pricerange": ["price", "pricerange", "cost", "how much"],
                   "area": ["area", "city", "part", "region"],
                   "food": ["food", "type", "category"],
                   "phone": ["phone number", "phone", "number"],
                   "addr": ["address", "street", "where"],
                   "postcode": ["postcode", "post code"]}

        for element in details.keys():
            names = details.get(element)
            for item in names:
                if item in string:
                    requested.append((details.get(element)[0], self.recommendation[element]))
                    break
        return requested

    def implication_rules(self, further_pref):
        restaurants = self.restaurants
        # TODO do iterations
        # TODO fix same consequent for different rules (using just and is not possible)
        #   need iterations and use lower level?
        print(restaurants['foodquality'])

        for column in further_pref:
            # Select column contents by column name using [] operator
            columnSeriesObj = further_pref[column]

            print('Colunm Name : ', column)
            print('Column Contents : ', columnSeriesObj.values)
            if columnSeriesObj.values[0]:
                print(True)
                # while self.further_pref[column] == '':
                # self.rules(restaurants)
        print(restaurants)
        # return restaurants
