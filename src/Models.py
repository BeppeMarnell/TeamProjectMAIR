import numpy as np
import pandas as pd
import re
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import Levenshtein as lev
import nltk
from nltk.corpus import stopwords

#testchange 

class Models:

    def __init__(self, dataset, baseline1=False, baseline2=False):
        # Get the train and test sets
        self.dataset = dataset

        # Prepare some useful data
        self.price_ranges = self.dataset.restaurant_info_df['pricerange'].unique() #unique restaurant prices 
        self.areas = self.dataset.restaurant_info_df['area'].unique() #unique restaurant areas 
        self.foods = self.dataset.restaurant_info_df['food'].unique() #unique restaurant foods 

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
            #SetSingleModel is true so this will be executed 
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

    def RegExpress_baseline2(self, utterance):
        #Define words and regular expressions for the second baseline 
        bye = re.search("good bye|darling|dear|goodb|[a-z]*bye", utterance)
        thankyou = re.search("thank you|welcome|thank|thanks|day|good[a-z]*|afternoon", utterance)
        ack = re.search("okay|um|ok|umh|ah", utterance)
        affirm = re.search("yes|right|alright|yeah|perfect|correct|cool|nice|awesome|great|sounds", utterance)
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
        restart = re.search("start over|nevermind", utterance)
           
        if bye !=None:
            return 'bye'
    
        if hello != None:
            return 'hello'
            
        if affirm !=None:
            return 'affirm'

        if ack != None:
            return 'ack'
        
        if confirm != None:
            return 'confirm'
        
        if deny != None:
            return 'deny'

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

    def evalueNewUtterance(self, utterance):
        # TODO: Implement other baselines in a more thoughtful way
        # Implement baseline
        if self.baseline1:
            return 'inform'

        if self.baseline2:
            return self.RegExpress_baseline2(utterance)

        # Evaluate the new utterance
        # Uses the learned vocab based on the training 
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

        care = 'i dont care'
        any = 'any'            

        # Look for the pricerange in the text
        for price in self.price_ranges:
            if care or any in string:
                pref['pricerange'] = any 
            if price in string:
                pref['pricerange'] = price
                break

        # Look for the area in the text
        for area in self.areas:
            if care or any in string:
                pref['area'] = any 
            if area in string:
                pref['area'] = area
                break

        # Look for the food in the text
        for food in self.foods:
            if care or any in string:
                pref['food'] = any
            if food in string:
                pref['food'] = food
                break

        # In case the food is not found, use some keyword matching,
        # maybe there is a spelling error
        # Should do the same for area and price?

        if pref['food'] == '':
            # Extract variable before keyword 'food'
            words = string.split(" ")

            if 'food' in words:
                miss_word = ''

                for indx in range(0, len(words)):
                    if words[indx] == 'food':
                        miss_word = words[indx - 1]

                # let's check if every misspelled word before food can be similar to something in the datase
                for food in self.foods:
                    option = self.levenshtein_option(food, miss_word)
                    pref['food'] = option                         
                    # This can also be 'not found'. Have to find a way to repeat the question
                    # or ask the user to be more specific 
    
        if pref['area'] == '':
                # Extract variable before keyword 'part'
                words = string.split(" ")

                if 'part' in words:
                    miss_word = ''

                    for indx in range(0, len(words)):
                        if words[indx] == 'part':
                            miss_word = words[indx - 1]

                    # let's check if every misspelled word before part can be similar to something in the datase
                    for area in self.areas:
                        option = self.levenshtein_option(area, miss_word)
                        pref['area'] = option 
                        # This can also be 'not found'. Have to find a way to repeat the question
                        # or ask the user to be more specific 
        
        if pref['pricerange'] == '':
                # Extract variable before keyword 'restaurant'
                words = string.split(" ")

                if 'restaurant' in words:
                    miss_word = ''

                    for indx in range(0, len(words)):
                        if words[indx] == 'restaurant':
                            miss_word = words[indx - 1]

                    # Check for matching with Levenshtein distance
                    # more than distance 3 it will fail


                    # let's check if every misspelled word before restaurant can be similar to something in the datase
                    for pricerange in self.price_ranges:
                        option = self.levenshtein_option(pricerange, miss_word)
                        pref['pricerange'] = option
                        # This can also be 'not found'. Have to find a way to repeat the question
                        # or ask the user to be more specific 
                



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
    
    def levenshtein_option(self, word_1, word_2):
        
        dst = {
            '1': [],
            '2': [],
            '3': []
                }
        
        if lev.distance(word_1, word_2) <= 3:
            dst[str(lev.distance(word_1, word_2))].append(word_1)
        
        if len(dst['1']) > 1:
            return dst['1']
        else:
            if len(dst['2']) > 1:
                return dst['2']
            else:
                if len(dst['3']) > 1:
                    return dst['3']
                else:
                    return 'not found'


