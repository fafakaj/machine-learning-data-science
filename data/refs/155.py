class MinStack:
    def __init__(self):
        self.data = []
    def push(self, val):
        self.data.append((val, min(val, self.data[-1][1]) if self.data else val))
    def pop(self):
        self.data.pop()
    def top(self):
        return self.data[-1][0]
    def getMin(self):
        return self.data[-1][1]
