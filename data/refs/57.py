class Solution:
    def insert(self, intervals, newInterval):
        s, e = newInterval
        left = [iv for iv in intervals if iv[1] < s]
        right = [iv for iv in intervals if iv[0] > e]
        for a, b in intervals:
            if b >= s and a <= e:
                s, e = min(s, a), max(e, b)
        return left + [[s, e]] + right
