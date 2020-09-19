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

        self.__states = [s1, s2, s3, s4, s5]

        e12 = Edge(s2, ['inform', 'reqalts', 'negate', 'deny', 'reqmore'])
        e11 = Edge(s1, ['confirm', 'affirm', 'request', 'null', 'hello', 'repeat', 'ack', 'restart', 'thankyou'])
        e13 = Edge(s3, ['_allinfo'])
        e15 = Edge(s5, ['bye'])
        s1.addEdge(e12)
        s1.addEdge(e11)
        s1.addEdge(e13)
        s1.addEdge(e15)

        e22 = Edge(s2, ['confirm', 'affirm', 'request', 'null', 'repeat', 'ack', 'deny',
                        'reqmore', 'inform', 'reqalts', 'negate', 'thankyou'])
        e21 = Edge(s1, ['restart', 'hello'])
        e25 = Edge(s5, ['bye'])
        e23 = Edge(s3, ['_allinfo'])
        s2.addEdge(e22)
        s2.addEdge(e21)
        s2.addEdge(e23)
        s2.addEdge(e25)

        # if yes moves to state 5, then you cannot say yes, then ask for more infos.
        # Need state 6 as final state, only if you say goodbye or thank you
        # State 5: restaurant is pretty safe, (has been ack or more details have been requested)
        #  if alternative is asked, switch to S4
        e31 = Edge(s1, ['restart', 'hello'])
        e32 = Edge(s2, ['inform'])
        e33 = Edge(s3, ['confirm', 'repeat', 'deny', 'negate', 'reqmore', 'reqalts', 'thankyou'])
        e34 = Edge(s4, ['request', 'ack', 'affirm', 'null'])
        e35 = Edge(s5, ['bye'])
        s3.addEdge(e31)
        s3.addEdge(e32)
        s3.addEdge(e33)
        s3.addEdge(e34)
        s3.addEdge(e35)

        e43 = Edge(s3, ['deny', 'inform', 'negate', 'reqmore', 'reqalts'])
        e44 = Edge(s4, ['confirm', 'request', 'repeat', 'ack', 'affirm', 'null'])
        e41 = Edge(s1, ['restart', 'hello'])
        e45 = Edge(s5, ['bye', 'thankyou'])
        s4.addEdge(e43)
        s4.addEdge(e44)
        s4.addEdge(e41)
        s4.addEdge(e45)

    def processState(self, state, utterance, preferences):
        # All the possibilities should be here, based on the utterance,
        # the function will return the next state

        for s in self.__states:
            if s.state == state:
                # special case if state is S2
                if s.state == State.S2 or s.state == State.S1:
                    food = True if preferences['food'].tolist()[0] != '' else False
                    area = True if preferences['area'].tolist()[0] != '' else False
                    price = True if preferences['pricerange'].tolist()[0] != '' else False
                    if food and area and price:
                        utterance = "_allinfo"
                return s.solve(utterance)

        return None


class State(Enum):
    S1 = 1,
    S2 = 2,
    S3 = 3,
    S4 = 4,
    S5 = 5,


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
