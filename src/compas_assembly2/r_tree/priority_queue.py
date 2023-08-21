import heapq


class PriorityQueue:
    def __init__(self):
        self.data = []

    def push(self, element):
        heapq.heappush(self.data, element)

    def pop(self):
        return heapq.heappop(self.data)

    def is_empty(self):
        return len(self.data) == 0
