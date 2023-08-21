class PriorityQueueElement:
    def __init__(self, v):
        self.data = v

    def __lt__(self, other):
        return self.data[0] < other.data[0]
