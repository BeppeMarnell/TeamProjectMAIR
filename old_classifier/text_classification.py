import pandas as pd
import numpy as np
from collections import Counter
from sklearn import tree
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


class Classification:
    """
    Class for classifying restaurant domain text sentences into 15 categories.
    """
    # count most common tokens
    dialog = Counter()
    # words = defaultdict(Counter)
    # convert words to vectors
    vectorizer = CountVectorizer()
    # list of categories used for converting names to indices
    items = []
    # array of all sentences of training set as matrix
    X = []
    # train and test set
    df, train, test = [], [], []

    def open_file(self, filename):
        """
        Open a file and set dataframe of class as well as list of categories (items)
        :param filename: Name of the file to be extracted
        """
        with open(filename, "r") as f:
            dialogues = []
            for line in f:
                # use the lowercase of each sentence
                token, line = line.lower().split(' ', 1)
                dialogues.append((token, line))
                self.dialog[token] += 1
                # for word in line[1:]:
                #     self.words[word][token]+= 1
        df = pd.DataFrame.from_records(dialogues, columns=["dialog", "utterance"])
        self.items = list(self.dialog)
        self.df = df

    def split_train_test(self, df):
        """
        Split dataframe into training set (85%) and test set (15%)
        :param df: Dataframe to be split
        """
        msk = np.random.rand(len(df)) < 0.85
        self.train = df[msk]
        self.test = df[~msk]

    def add_extra_column(self, df):
        """
        Add extra column to the dataset to have the number of the category for each row
        :param df: Dataset to which the column is added
        :return: modified dataset
        """
        # get extra column with number
        indices = []
        for index, row in df.iterrows():
            index = self.items.index(row['dialog'])
            indices.append(index)
        df.insert(2, 'class', indices, False)
        print(df)
        return df

    def init_vectorizer(self, df):
        """
        Initialize the count vectorizer, which will convert the sentences into matrices.
        Sets vectorizer and X of class.
        :param df: dataframe which will be vectorized
        """
        self.vectorizer = CountVectorizer()
        self.X = self.vectorizer.fit_transform(df['utterance'])

    def vectorize(self, sentence):
        """
        Returns vectorization for new sentence, based on vectorizer of this class
        :param sentence: User input, which will be transformed
        :return: Matrix representation of the sentence
        """
        X_new_counts = self.vectorizer.transform(sentence).toarray()
        return X_new_counts

    def majority_class(self, sentence):
        """
        Classification method using only the majority class.
        :param sentence: Input, for which the class will be analysed
        :return: Index of the most commonly used class of the training set
        """
        return self.items.index(self.dialog.most_common(1)[0][0])

    def rule_based(self, sentence):
        """
        Classification method using some rules. If none of the rules apply, the majority class is used
        :param sentence: Input, for which the class will be analysed
        :return: Index of the corresponding class, if any rule is correct, otherwise index of the majority label
        """
        if "goodbye" in sentence:
            return self.items.index('bye')
        if 'hello' in sentence or "hi" in sentence:
            return self.items.index('hello')
        if 'yes' in sentence:
            return self.items.index('affirm')
        else:
            return self.majority_class(sentence)

    def decision_tree(self, sentence):
        """
        Classification method using scikit learn decision tree.
        :param sentence: Array of inputs, for which the class will be analysed
        :return: Array of predictions for each sentence in input, if only one, return scalar
        """
        # if type(sentence) != list:
        #     sentence = list(sentence)
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(self.X.toarray(), self.train['class'])
        pred = clf.predict(self.vectorize(sentence))
        if len(pred) > 1:
            return pred
        return pred[0]

    def logistic_regression(self, sentence):
        """
        Classification method using scikit learn logistic regression.
        :param sentence: Array of inputs, for which the class will be analysed
        :return: Array of predictions for each sentence in input, if only one, return scalar
        """
        clf = LogisticRegression(random_state=0, max_iter=1000).fit(self.X.toarray(), self.train['class'])
        pred = clf.predict(self.vectorize(sentence))
        if len(pred) > 1:
            return pred
        return pred[0]

    def classify(self, index):
        """
        Method to convert index or array of indices into the correct class label
        :param index: Scalar or array containing indices
        :return: List of labels or just label of class as string
        """
        if type(index) == np.ndarray:
            classes = []
            for item in index:
                classes.append(self.items[item])
            return classes
        item = self.items[index]
        return item

    def __init__(self):
        """
        Initialize class by opening file, splitting train and test, adding extra columns and initializing vectorizer
        """
        self.open_file("dialog_acts.dat")
        self.split_train_test(self.df)
        self.train = self.add_extra_column(self.train)
        self.test = self.add_extra_column(self.test)
        self.init_vectorizer(self.train)
