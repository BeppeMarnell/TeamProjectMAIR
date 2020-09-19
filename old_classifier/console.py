from old_classifier.text_classification import Classification
import old_classifier.evaluation
import time


def read_from_console():
    """
    Method to read input from console and make it lowercase
    :return: Input entered by user
    """
    print("Please enter your sentence. Enter 'quit' to exit.")
    input1 = input()
    return input1.lower()


def output(analysis, time_needed):
    """
    Print analysis to screen
    :param analysis: Prediction of the sentence using one predefined model
    :param time_needed: Time needed to predict label of sentence
    """
    print("The sentence analysed is of the category:", analysis)
    print("This took", time_needed, "seconds.")


if __name__ == '__main__':
    tc = Classification()
    # run evaluation
    evaluation.evaluate()
    # run endless loop reading input and analyzing it
    while True:
        sentence = read_from_console()
        # stop if user types "quit"
        if sentence == "quit":
            break
        # analyse sentence using logistic regression
        start = time.time()
        analysis = tc.classify(tc.logistic_regression([sentence]))
        end = time.time()
        time_needed = end - start
        output(analysis, time_needed)

        # analyse sentence using decision tree
        start = time.time()
        analysis = tc.classify(tc.decision_tree([sentence]))
        end = time.time()
        time_needed = end - start
        output(analysis, time_needed)
