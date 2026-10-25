class Solution:
    def eraseOverlapIntervals(self, intervals):
        iv = sorted(intervals)
        n = len(iv)
        best = [1] * n
        for i in range(n):
            for j in range(i):
                if iv[j][1] <= iv[i][0]:
                    best[i] = max(best[i], best[j] + 1)
        return n - max(best)
