class Solution:
    def coinChange(self, coins, amount):
        def best(s):
            if s == 0:
                return 0
            res = float("inf")
            for c in coins:
                if c <= s:
                    res = min(res, 1 + best(s - c))
            return res
        r = best(amount)
        return r if r != float("inf") else -1
