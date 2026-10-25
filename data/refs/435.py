class Solution:
    def eraseOverlapIntervals(self, intervals):
        removed = 0
        end = float("-inf")
        for s, e in sorted(intervals, key=lambda iv: iv[1]):
            if s >= end:
                end = e
            else:
                removed += 1
        return removed
