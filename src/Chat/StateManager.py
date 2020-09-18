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

        e12 = Edge(s2, ['inform', 'reqalts', 'negate', 'deny', 'reqmore'])
        e11 = Edge(s1, ['confirm', 'affirm', 'request', 'null', 'hello', 'repeat', 'ack', 'restart'])
        e14 = Edge(s4, ['_allinfo'])
        e16 = Edge(s6, ['bye', 'thankyou'])
        s1.addEdge(e12)
        s1.addEdge(e11)
        s1.addEdge(e14)
        s1.addEdge(e16)

        # TODO: come up with a way this works. State2 is a transition node where the preference are checked
        # TODO add possibility to restart and say bye
        e22 = Edge(s2, ['confirm', 'affirm', 'request', 'null', 'repeat', 'ack', 'deny',
                        'reqmore', 'inform', 'reqalts', 'negate'])
        e21 = Edge(s1, ['restart', 'hello'])
        e26 = Edge(s6, ['bye', 'thankyou'])
        # e3 = Edge(s3, ['_missinginfo'])
        e24 = Edge(s4, ['_allinfo'])
        s2.addEdge(e22)
        s2.addEdge(e21)
        s2.addEdge(e24)
        s2.addEdge(e26)

        # TODO remove null (as that can mean not understood)
        #e33 = Edge(s3, ['confirm', 'affirm', 'request', 'thankyou', 'null', 'bye', 'repeat', 'ack', 'deny', 'reqmore', 'hello'])
        #e32 = Edge(s2, ['inform', 'reqalts', 'negate'])
        #e31 = Edge(s1, ['restart'])
        #s3.addEdge(e33)
        #s3.addEdge(e32)
        #s3.addEdge(e31)

        # TODO if yes moves to state 5, then you cannot say yes, then ask for more infos.
        #  Need state 6 as final state, only if you say goodbye or thank you
        #  State 5: restaurant is pretty safe, (has been ack or more details have been requested)
        #   if alternative is asked, switch to S4
        #
        # e8 = Edge(s4, ['confirm', 'deny', 'inform', 'negate', 'request', 'repeat', 'reqmore', 'reqalts'])
        # e9 = Edge(s5, ['ack', 'affirm', 'null', 'bye', 'thankyou'])
        # e10 = Edge(s1, ['restart', 'hello'])
        # TODO move confirm and inform and ... to e9?
        e42 = Edge(s2, ['inform'])
        e44 = Edge(s4, ['confirm', 'repeat', 'deny', 'negate', 'reqmore', 'reqalts'])
        e45 = Edge(s5, ['request', 'ack', 'affirm', 'null'])
        e41 = Edge(s1, ['restart', 'hello'])
        e46 = Edge(s6, ['bye', 'thankyou'])
        s4.addEdge(e42)
        s4.addEdge(e44)
        s4.addEdge(e45)
        s4.addEdge(e41)
        s4.addEdge(e46)

        e54 = Edge(s4, ['deny', 'inform', 'negate', 'reqmore', 'reqalts'])
        e55 = Edge(s5, ['confirm', 'request', 'repeat', 'ack', 'affirm', 'null'])
        e51 = Edge(s1, ['restart', 'hello'])
        e56 = Edge(s6, ['bye', 'thankyou'])
        s5.addEdge(e54)
        s5.addEdge(e55)
        s5.addEdge(e51)
        s5.addEdge(e56)

    def processState(self, state, utterance, preferences):
        # All the possibilities should be here, based on the utterance,
        # the function will return the next state

        # TODO: add special case, when in state S2,
        #  then check for preferences before going on

        for s in self.__states:
            if s.state == state:
                # special case if state is S2
                if s.state == State.S2 or s.state == State.S1:
                    food = True if preferences['food'].tolist()[0] != '' else False
                    area = True if preferences['area'].tolist()[0] != '' else False
                    price = True if preferences['pricerange'].tolist()[0] != '' else False
                    if food and area and price:
                        utterance = "_allinfo"
                    # TODO if I don't use elif block, i should be able to handle all utterances
                    # elif s.state == State.S2:
                    #     utterance = "_missinginfo"
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
