from Chat.ChatManager import ChatManager
from DatasetLoader import DatasetLoader
from Models import Models
import time


class Main:

    def __init__(self):
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
        chat = ChatManager(modelz)
        chat.run()


if __name__ == '__main__':
    Main()
