from src.ChatManager import ChatManager
from src.DatasetLoader import DatasetLoader
from src.Models import Models
import time

class Main:

    def __init__(self):
        # load the dataset
        data = DatasetLoader('assets/dialog_acts.dat')

        # create and train the models
        modelz = Models(data)
        modelz.showPerformances()
        modelz.baseline2 = True

        while not modelz.endLoading:
            time.sleep(1)

        chat = ChatManager(modelz)
        chat.run()


if __name__ == '__main__':
    Main()
