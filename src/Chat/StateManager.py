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

        e1 = Edge(s2, ['inform', 'reqalts', 'negate'])
        e2 = Edge(s1, ['confirm', 'affirm', 'request', 'thankyou', 'null', 'bye', 'hello', 'repeat', 'ack', 'restart',
                       'deny', 'reqmore'])
        s1.addEdge(e1)
        s1.addEdge(e2)

        # TODO: come up with a way this works. State2 is a transition node where the preference are checked
        e3 = Edge(s3, [])
        e4 = Edge(s4, [])
        s2.addEdge(e3)
        s2.addEdge(e4)

        e5 = Edge(s3, ['confirm', 'affirm', 'request', 'thankyou', 'null', 'bye', 'repeat', 'ack', 'deny', 'reqmore', 'hello'])
        e6 = Edge(s2, ['inform', 'reqalts', 'negate'])
        e7 = Edge(s1, ['restart'])
        s3.addEdge(e5)
        s3.addEdge(e6)
        s3.addEdge(e7)

        e8 = Edge(s4, ['confirm', 'deny', 'inform', 'negate', 'request', 'repeat', 'reqmore', 'reqalts'])
        e9 = Edge(s5, ['ack', 'affirm', 'bye', 'null', 'thankyou'])
        e10 = Edge(s1, ['restart', 'hello'])
        s4.addEdge(e8)
        s4.addEdge(e9)
        s4.addEdge(e10)

    def processState(self, state, utterance):
        # All the possibilities should be here, based on the utterance,
        # the function will return the next state

        #TODO: add special case, when in state S2,
        # then check for preferences before going on

        for s in self.__states:
            if s.state == state:
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
