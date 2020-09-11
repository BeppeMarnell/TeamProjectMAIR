class ChatManager:

    def __init__(self, models):
        # Define properties
        self.commands = [1, 2]
        self.models = models

        print('-----> Welcome to the dialog system project')
        self.showCommands()

    def run(self):
        # Start the chat loop
        while True:
            command = input("-----> type command:")

            if int(command) in self.commands:
                # New utterance
                if int(command) == self.commands[0]:
                    utterance = input("-----> type new utterance:")
                    self.models.evalueNewUtterance(utterance)

                # Exit
                if int(command) == self.commands[1]:
                    break

    def showCommands(self):
        print('-----> here there is a list of possible commands: ')
        # print('----->       type 1 to show the list of classifiers')
        print(''.join(['----->       type ', str(self.commands[0]), ' to enter a new utterance']))
        print(''.join(['----->       type ', str(self.commands[1]), ' to end']))
