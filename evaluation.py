from text_classification import Classification
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
import time


def evaluate():
    """
    Method to evaluate the different models using several metrics.
    Also measure time how long each model takes to analyse sentences.
    """
    tc = Classification()
    # get list of correct labels
    y_true = tc.test['class'].tolist()

    # Majority
    start = time.time()
    y_pred_majority = []
    # create list of predicted labels
    for index, row in tc.test.iterrows():
        y_pred_majority.append(tc.rule_based(row['utterance']))
    metrics(y_true, y_pred_majority, "Majority")
    end = time.time()
    print("Time needed: ", end-start)
    print("-----------------------------------------------------------")

    # Rule based
    start = time.time()
    y_pred_rule = []
    # create list of predicted labels
    for index, row in tc.test.iterrows():
        y_pred_rule.append(tc.rule_based(row['utterance']))
    metrics(y_true, y_pred_rule, "Rule based")
    end = time.time()
    print("Time needed: ", end - start)
    print("-----------------------------------------------------------")

    # Decision Tree
    start = time.time()
    y_pred_dec = tc.decision_tree(tc.test['utterance'])
    metrics(y_true, y_pred_dec, "Decision Tree")
    end = time.time()
    print("Time needed: ", end - start)
    print("-----------------------------------------------------------")

    # Logistic regression
    start = time.time()
    y_pred_log = tc.logistic_regression(tc.test['utterance'])
    metrics(y_true, y_pred_log, "Logistic Regression")
    end = time.time()
    print("Time needed: ", end-start)
    print("-----------------------------------------------------------")


def metrics(y_true, y_pred, name):
    """
    Use list of predictions and list of correct values to analyse model according to the following metrics:
    - accuracy
    - precision
    - recall
    - F1 score
    :param y_true: List of correct labels
    :param y_pred: List of predicted labels
    :param name: Name of model, used for print statement
    """
    print(name, "accuracy", accuracy_score(y_true, y_pred))
    print(name, "precision:", precision_score(y_true, y_pred, average='weighted', zero_division=0))
    print(name, "recall:", recall_score(y_true, y_pred, average='weighted', zero_division=0))
    print(name, "F1 score:", f1_score(y_true, y_pred, average='weighted', zero_division=0))
    print(classification_report(y_true, y_pred, zero_division=0))


def test_methods():
    """
    Method to test difficult cases
    """
    cla = Classification()
    # print(cla.classify(cla.majority_class("how are you".lower())))
    # print(cla.classify(cla.rule_based("yes that is correct".lower())))
    # print(cla.classify(cla.logistic_regression(['thank you'.lower(), 'i am groot'.lower()])))
    # print(cla.classify(cla.decision_tree(['goodbye'.lower(), 'good evening'.lower()])))

    # Difficult cases:
    # Negation
    negations = ["i dont want that", "please not chinese", "i do not like that", "i cannot not want seafood",
                 "im not looking for a restaurant that serves food"]
    correct = [cla.items.index("deny"), cla.items.index("deny"), cla.items.index("deny"), cla.items.index("inform"),
               cla.items.index("deny")]
    print(negations)
    log = cla.logistic_regression(negations)
    dec = cla.decision_tree(negations)
    print(cla.classify(log))
    print(cla.classify(dec))
    metrics(correct, log, "Logistic regression")
    metrics(correct, dec, "Decision tree")

    # Ambiguous words
    ambiguous = ["please say that again", "please seafood again", "other", "another"]
    correct2 = [cla.items.index("repeat"), cla.items.index("inform"), cla.items.index("reqalts"),
                cla.items.index("reqalts")]
    print(ambiguous)
    log = cla.logistic_regression(ambiguous)
    dec = cla.decision_tree(ambiguous)
    print(cla.classify(log))
    print(cla.classify(dec))
    metrics(correct2, log, "Logistic regression")
    metrics(correct2, dec, "Decision tree")


if __name__ == '__main__':
    evaluate()
    # test_methods()
