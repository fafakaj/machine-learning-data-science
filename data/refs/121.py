class Solution:
    def maxProfit(self, prices):
        low = float("inf")
        best = 0
        for p in prices:
            best = max(best, p - low)
            low = min(low, p)
        return best
