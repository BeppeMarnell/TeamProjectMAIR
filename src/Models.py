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

        # TODO: here you can activate and deactivate the models
        self.models = {
            'logReg': LogisticRegression(C=100, random_state=0, max_iter=1000),
            # 'decTree': DecisionTreeClassifier(),
            # 'SVM': SVC(gamma='scale', probability=True, C=1),
            # 'multiNB': MultinomialNB(),
            # 'kNeigh': KNeighborsClassifier(n_neighbors=3)
        }

        # Set some variables

        # TODO: Here you can activate if you'd like one or multiple models at the same time
        # TODO: From task 1.b on, it is not possible to have multiple models
        self.singleModel = True
        self.singleModelName = 'logReg'  # Default one

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

    def setSingleModel(self, singleModel=True, name='logReg'):
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
        words = string.split(" ")
        if pref['food'] == '':
            # Extract variable before keyword 'food'
            # words = string.split(" ")

            if 'food' in words:
                miss_word = ''

                for indx in range(0, len(words)):
                    if words[indx] == 'food':
                        miss_word = words[indx - 1]

                if miss_word == 'any' or miss_word == 'world':
                    pref['food'] = 'any'
                else:
                    pref['food'] = self.get_levenshtein_items([miss_word], self.foods)

        if pref['area'] == '':
            # Only use words in sentences that contain in (like in the center, ...)
            if 'in' in words:
                miss_word = ''

                for indx in range(0, len(words)):
                    if words[indx] == 'in':
                        if words[indx + 1] == 'the':
                            miss_word = words[indx + 2]
                # TODO find alternatives for any
                if 'any' in words:
                    pref['area'] = 'any'
                else:
                    pref['area'] = self.get_levenshtein_items([miss_word], self.areas)

        if pref['pricerange'] == '':
            # TODO find keywords

            if 'price' in words:
                if 'any' == words[words.index('price') - 1]:
                    pref['pricerange'] = 'any'
            else:
                pref['pricerange'] = self.get_levenshtein_items(words, self.price_ranges)

        return pref

    # TODO fix method (not mandatory but nice to have)
    # def negative_preferences(self, string):
    #     """
    #       This method evaluates strings in the form "not in the centre" and "no european food" and ensures that the
    #       no is handled correctly (suggest everything except that part)
    #     """
    #     words = string.split(" ")
    #     negative_words = ['no', 'not']
    #     negation_indices = []
    #     for negative_word in negative_words:
    #         indices = [i for i, x in enumerate(words) if x == negative_word]
    #         negation_indices.append(indices)
    #     negation_indices = [item for sublist in negation_indices for item in sublist]
    #     print(negation_indices)
    #     for index in negation_indices:
    #         if len(words) >= index+1:
    #             miss_word = words[index+1]
    #             print(miss_word)
    #             pref = self.extractPreference(miss_word)
    #             print(pref)
    #             # price = self.get_levenshtein_items([miss_word], self.foods)

    def get_levenshtein_items(self, miss_words, possible_words):
        # Check for matching with Levenshtein distance
        # more than distance 3 it will fail

        # remove all stopwords to not get a close distance to words like 'the'
        stop_words = set(stopwords.words('english'))
        # print(miss_words)
        miss_words = [w for w in miss_words if w not in stop_words]
        # print(miss_words)

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
        # print(dst)
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

        restaurants = self.dataset.restaurant_info_df.loc[food & area & pricerange]
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
            self.lookup_in_restaurant_info(preferences)
        self.recommendation = self.recommend_restaurant()
        # print(self.recommendation)

    def extract_details(self, string):
        string = string.lower()
        requested = []
        # TODO add restaurant, name, price, type, address, number as keywords
        # details = ["restaurantname", "pricerange", "area", "food", "phone", "addr", "postcode"]
        details = {"restaurantname": ["name", "restaurantname", "restaurant"],
                   "pricerange": ["price", "pricerange", "cost", "how much"],
                   "area": ["area", "city", "part", "region"],
                   "food": ["food", "type", "category"],
                   "phone": ["phone number", "phone", "number"],
                   "addr": ["address", "street", "where"],
                   "postcode": ["postcode"]}

        for element in details.keys():
            names = details.get(element)
            for item in names:
                if item in string:
                    requested.append((details.get(element)[0], self.recommendation[element]))
                    break
        return requested
