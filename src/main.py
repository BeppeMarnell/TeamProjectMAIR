from src.Chat.ChatManager import ChatManager
from src.DatasetLoader import DatasetLoader
from src.Models import Models
import time
import argparse
import os
import sys

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))

class Main:

    def __init__(self, formal, delay, caps):
        # Load the dataset
        data = DatasetLoader()
        # Create and train the models
        modelz = Models(data)
        # modelz.showPerformances()
        modelz.setSingleModel()  # this will set the logistic regression model

        # Wait for the models to finish loading
        while not modelz.endLoading:
            time.sleep(1)

        # Initialize the chat and run the dialogs
        chat = ChatManager(modelz, formal, delay, caps)
        chat.run()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--formal", help="formal or informal system speach. Use informal for informal "
                                    "speech.", default="formal")
    p.add_argument("--delay", help="Use delay for a delay of 2 seconds. Use mess_delay for a delay of 2 seconds "
                                   "accompanied with a message. Use off for no delay", default="off")
    p.add_argument("--caps", help="Use caps for system output to be in all caps.", default="no_caps")
    args = p.parse_args(sys.argv[1:])
    Main(args.formal, args.delay, args.caps)
