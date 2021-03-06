try:
    from Chat.ChatManager import ChatManager
    from DatasetLoader import DatasetLoader
    from Models import Models
except ImportError:
    from src.Chat.ChatManager import ChatManager
    from src.DatasetLoader import DatasetLoader
    from src.Models import Models
import argparse
import sys
import time


class Main:

    def __init__(self, formal, caps, group):
        # Load the dataset
        data = DatasetLoader()
        # Create and train the models
        modelz = Models(data)
        # modelz.showPerformances()
        modelz.setSingleModel()  # this will set the multiNB model

        # Wait for the models to finish loading
        while not modelz.endLoading:
            time.sleep(1)

        # Initialize the chat and run the dialogs
        chat = ChatManager(modelz, group, formal, caps)
        chat.run()


if __name__ == '__main__':
    # function that runs the main class with the given arguments
    p = argparse.ArgumentParser()
    p.add_argument("--formal", help="formal or informal system speech. Use 'informal' for informal "
                                    "speech.", default="formal")
    # p.add_argument("--d", help="Use 'delay' for a delay. Use 'delay_mess' for a delay "
    #                                "accompanied with a message.", default="off")
    # p.add_argument("--dt", help="Define here how long of a delay there should be (in seconds)", default=0)
    p.add_argument("--caps", help="Use 'caps' for system output to be in all caps.", default="no_caps")
    p.add_argument("--group", help="define groupname plus task number", default=None, nargs=2)
    args = p.parse_args(sys.argv[1:])
    Main(args.formal, args.caps, args.group)
