from enum import Enum


class StateManager:

    def __init__(self):
        #TODO: update the graph according to graph in Teams

        # Create the graph
        s1 = StateNode(State.S1)
        s2 = StateNode(State.S2)
        s3 = StateNode(State.S3)
        s4 = StateNode(State.S4)
        s5 = StateNode(State.S5)
        s6 = StateNode(State.S6)

        self.__states = [s1, s2, s3, s4, s5, s6]

        e1 = Edge(s2, ['inform', 'reqalts', 'negate'])
        e2 = Edge(s1, ['confirm', 'affirm', 'request', 'thankyou', 'null', 'bye', 'hello', 'repeat', 'ack', 'restart',
                       'deny', 'reqmore'])
        s1.addEdge(e1)
        s1.addEdge(e2)

        # TODO: come up with a way this works. State2 is a transition node where the preference are checked
        # TODO add possibility to restart
        e2 = Edge(s2, ['_missinginfo'])
        # e3 = Edge(s3, ['_missinginfo'])
        e4 = Edge(s4, ['_allinfo'])
        s2.addEdge(e2)
        # s2.addEdge(e3)
        s2.addEdge(e4)

        # TODO remove null (as that can mean not understood)
        e5 = Edge(s3, ['confirm', 'affirm', 'request', 'thankyou', 'null', 'bye', 'repeat', 'ack', 'deny', 'reqmore', 'hello'])
        e6 = Edge(s2, ['inform', 'reqalts', 'negate'])
        e7 = Edge(s1, ['restart'])
        s3.addEdge(e5)
        s3.addEdge(e6)
        s3.addEdge(e7)

        # TODO if yes moves to state 5, then you cannot say yes, then ask for more infos.
        #  Need state 6 as final state, only if you say goodbye or thank you
        #  State 5: restaurant is pretty safe, (has been ack or more details have been requested)
        #   if alternative is asked, switch to S4
        #
        # e8 = Edge(s4, ['confirm', 'deny', 'inform', 'negate', 'request', 'repeat', 'reqmore', 'reqalts'])
        # e9 = Edge(s5, ['ack', 'affirm', 'null', 'bye', 'thankyou'])
        # e10 = Edge(s1, ['restart', 'hello'])
        # TODO move confirm and inform and ... to e9?
        e8 = Edge(s4, ['confirm', 'deny', 'inform', 'negate', 'reqmore', 'reqalts'])
        e9 = Edge(s5, ['request', 'repeat', 'ack', 'affirm', 'null', 'thankyou'])
        e10 = Edge(s1, ['restart', 'hello'])
        e11 = Edge(s6, ['bye'])
        s4.addEdge(e8)
        s4.addEdge(e9)
        s4.addEdge(e10)
        s4.addEdge(e11)

        e12 = Edge(s4, ['confirm', 'deny', 'inform', 'negate', 'reqmore', 'reqalts'])
        e13 = Edge(s5, ['request', 'repeat', 'ack', 'affirm', 'null'])
        e14 = Edge(s1, ['restart', 'hello'])
        e15 = Edge(s6, ['bye', 'thankyou'])
        s5.addEdge(e12)
        s5.addEdge(e13)
        s5.addEdge(e14)
        s5.addEdge(e15)

    def processState(self, state, utterance, preferences):
        # All the possibilities should be here, based on the utterance,
        # the function will return the next state

        #TODO: add special case, when in state S2,
        # then check for preferences before going on

        for s in self.__states:
            if s.state == state:
                # special case if state is S2
                if s.state == State.S2:
                    print(preferences)
                    food = True if preferences['food'].tolist()[0] != '' else False
                    area = True if preferences['area'].tolist()[0] != '' else False
                    price = True if preferences['pricerange'].tolist()[0] != '' else False
                    if food and area and price:
                        utterance = "_allinfo"
                    else:
                        utterance = "_missinginfo"
                print(utterance)
                return s.solve(utterance)

        return None


class State(Enum):
    S1 = 1,
    S2 = 2,
    S3 = 3,
    S4 = 4,
    S5 = 5,
    S6 = 6,


class StateNode:

    def __init__(self, state):
        self.state = state
        self.edges = []

    def addEdge(self, edge):
        self.edges.append(edge)

    def solve(self, utterance):
        # Look at the utterance and return the child node
        for edge in self.edges:
            if utterance in edge.utterances:
                return edge.end.state

        return None


class Edge:

    def __init__(self, end, utterances):
        # Attach to the end node
        self.end = end
        # List with the possible utterances in the edge
        self.utterances = utterances
