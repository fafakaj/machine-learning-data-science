class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = {}
    def get(self, key):
        if key not in self.data:
            return -1
        self.data[key] = self.data.pop(key)
        return self.data[key]
    def put(self, key, value):
        self.data.pop(key, None)
        self.data[key] = value
        if len(self.data) > self.cap:
            del self.data[next(iter(self.data))]
