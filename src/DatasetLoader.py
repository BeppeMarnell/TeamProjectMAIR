import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split


class DatasetLoader:

    def __init__(self):
        # Load the dataset
        self.utterances_df = pd.read_csv('assets/dialog_acts.dat', names=['dialog_act'])
        self.utterances_df[['dialog_act', 'utterance_content']] = self.utterances_df["dialog_act"]\
            .str.split(" ", 1, expand=True)

        self.restaurant_info_df = pd.read_csv("assets/restaurant_info2.csv")
        # Some features were empty, let's replace them with 'unknown'
        self.restaurant_info_df = self.restaurant_info_df.replace(np.nan, 'unknown', regex=True)

        # Clean the dataset
        self.__clean()

        # Split the dataset for training and for tests
        train, test = train_test_split(self.utterances_df, test_size=0.15, random_state=42)

        # Create a BOW
        self.count_vect = CountVectorizer(min_df=0)
        x_bow = self.count_vect.fit_transform(train['utterance_content'])

        tfidf_transformer = TfidfTransformer()
        self.x_train = tfidf_transformer.fit_transform(x_bow)

        # Create a BOW representation of the test set
        self.x_test = self.count_vect.transform(test['utterance_content'])

        # Get the labels for the training set
        self.y_train = train['dialog_act'].values
        self.y_test = test['dialog_act'].values

        # LOGs
        # print('-----> Dataset Loaded \n')

    def __clean(self):
        # Function used to lowercase the data set

        # Lower case all
        self.utterances_df['dialog_act'] = self.utterances_df['dialog_act'].str.lower()
        self.utterances_df['utterance_content'] = self.utterances_df['utterance_content'].str.lower()

    def showHead(self):
        # Print the first few lines of the dataset
        print(self.utterances_df.head())
