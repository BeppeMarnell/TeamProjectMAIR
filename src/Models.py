import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import Levenshtein as lev
import nltk
from nltk.corpus import stopwords


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
        # index if system recommends a category (how about vietnamese food?)
        self.index_category = 0

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

        if self.baseline2 and ('have a nice' in utterance):
            return 'bye'

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

    def extractPreference(self, string):
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

        # TODO keywords matching here
        distances = {
            'pricerange': '',
            'area': '',
            'food': ''
        }

        change_found = 0
        for missing_pref in ['food', 'area', 'pricerange']:

            if pref[missing_pref] == '':
                # TODO: p: expand this
                keywords = {'food': ['food'], 'area': ['in', 'the'], 'pricerange': ['priced']}
                keyword_selection = {'food': self.foods, 'area': self.areas, 'pricerange': self.price_ranges}

                # Extract variable before relevant keyword
                words = string.split(" ")

                # TODO: Add more rigorous any preference detection
                if set(keywords[missing_pref]).issubset(set(words)):
                    change_found = 1
                    miss_word = ''
                    if missing_pref != 'area':
                        for indx in range(0, len(words)):
                            if words[indx] == keywords[missing_pref][0]:
                                miss_word = words[indx - 1]
                    else:
                        for indx in range(0, len(words)):
                            if indx != 0 and [words[indx - 1], words[indx]] == keywords[missing_pref]:
                                miss_word = words[indx + 1]

                    if miss_word == 'any':
                        pref[missing_pref] = 'any'
                        break
                    # Check for matching with Levenshtein distance
                    # more than distance 3 it will fail
                    distances[missing_pref] = {
                        '1': [],
                        '2': [],
                        '3': []
                    }

                    # let's check if every misspelled word before food can be similar to something in the dataset
                    for stuff in keyword_selection[missing_pref]:
                        if lev.distance(stuff, miss_word) <= 3:
                            # print(lev.distance(food, miss_word), lev.distance('Levenshtein', 'food'), food, miss_word)
                            distances[missing_pref][str(lev.distance(stuff, miss_word))].append((stuff, miss_word))
        if change_found:
            return pref, distances
        return pref, {}

    def extract_correct_spelling(self, distances):
        # finally let's set the food preference giving priority to the one with less distance
        for missing_pref in distances.keys():
            dst = distances[missing_pref]
            if len(dst) and len(dst['1']):
                for entry, miss_word in dst['1']:
                    return entry, miss_word, missing_pref
            elif len(dst) and len(dst['2']):
                for entry, miss_word in dst['2']:
                    return entry, miss_word, missing_pref
            elif len(dst) and len(dst['3']):
                for entry, miss_word in dst['3']:
                    return entry, miss_word, missing_pref
        return '', 'your word', ''

    def lookup_in_restaurant_info(self, preferences):
        if preferences.loc[0]['food'] != 'any':
            food = self.dataset.restaurant_info_df['food'] == preferences.loc[0]['food']
        else:
            food = True
        if preferences.loc[0]['area'] != 'any':
            area = self.dataset.restaurant_info_df['area'] == preferences.loc[0]['area']
        else:
            area = True
        if preferences.loc[0]['pricerange'] != 'any':
            pricerange = self.dataset.restaurant_info_df['pricerange'] == preferences.loc[0]['pricerange']
        else:
            pricerange = True

        if preferences.loc[0]['food'] == 'any' and preferences.loc[0]['area'] == 'any' and preferences. \
                loc[0]['pricerange'] == 'any':
            restaurants = self.dataset.restaurant_info_df
        else:
            restaurants = self.dataset.restaurant_info_df.loc[food & area & pricerange]
        return restaurants.reset_index()

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
            self.restaurants = self.lookup_in_restaurant_info(preferences)
        self.recommendation = self.recommend_restaurant()

    def propose_alternative_type(self, preferences):
        """
        Method to propose changes to the user preference in order to actually find a restaurant.
        Only executed, if user used preferences which lead to no found restaurant.
        Will adapt one of the preferences and check if there are possible restaurants found then.
        First changes type of food, then area, then price
        :param preferences: Preferences entered by user
        :return: List of tuples with possible changes to one of the preferences
        """
        # check if any of the preferences is already set to any (don't need to check then)
        food_any = preferences.loc[0]['food'] == 'any'
        area_any = preferences.loc[0]['area'] == 'any'
        price_any = preferences.loc[0]['pricerange'] == 'any'
        possible_options = []

        if not food_any:
            # modify the specific preference to any and look up possible restaurants
            preferences_new = preferences.copy(deep=True)
            preferences_new.loc[0]['food'] = 'any'
            possible_restaurants = self.lookup_in_restaurant_info(preferences_new)
            # get a list of unique values for that category
            possible_food = possible_restaurants['food'].unique()
            for item in possible_food:
                possible_options.append((item, 'food'))
        if not area_any:
            preferences_new = preferences.copy(deep=True)
            preferences_new.loc[0]['area'] = 'any'
            possible_restaurants = self.lookup_in_restaurant_info(preferences_new)
            possible_areas = possible_restaurants['area'].unique()
            for item in possible_areas:
                possible_options.append((item, 'area'))
        if not price_any:
            preferences_new = preferences.copy(deep=True)
            preferences_new.loc[0]['pricerange'] = 'any'
            possible_restaurants = self.lookup_in_restaurant_info(preferences_new)
            possible_prices = possible_restaurants['pricerange'].unique()
            for item in possible_prices:
                possible_options.append((item, 'pricerange'))
        return possible_options

    def choose_proposal(self, possible_options):
        """
        Method that lets you choose one element of the possible options. It returns a new one each time,
        when it has returned all, it starts from the beginning again
        :param possible_options: List of possible preference changes that will allow you to find a restaurant
        :return: one possible change to either food type, price or area. Returns tuple with new value and type
        """
        self.index_category += 1
        return possible_options[self.index_category % len(possible_options)]

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
