import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split


class DatasetLoader:

    def __init__(self, path, baseline2=False):
        # Load the dataset
        self.df = pd.read_csv(path, names=['dialog_act'])
        self.df[['dialog_act', 'utterance_content']] = self.df["dialog_act"].str.split(" ", 1, expand=True)

        # Clean the dataset
        self.__clean(baseline2)

        # Split the dataset for training and for tests
        train, test = train_test_split(self.df, test_size=0.15, random_state=42)

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
        print('-----> Dataset Loaded \n')

    def __clean(self, baseline2):
        # Lower case all
        self.df['dialog_act'] = self.df['dialog_act'].str.lower()
        self.df['utterance_content'] = self.df['utterance_content'].str.lower()

        # Implement the 2nd baseline system A baseline rule-based system based on keyword matching. An example rule
        # could be: anytime an utterance contains ‘goodbye’, it would be classified with the dialog act bye.
        if baseline2:
            indx = self.df.loc[self.df['utterance_content'].str.contains("have a nice day")].index

            for i in indx:
                self.df.loc[i, 'dialog_act'] = "bye"

    def showHead(self):
        print(self.df.head())
