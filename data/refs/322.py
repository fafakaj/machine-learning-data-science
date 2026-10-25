class Solution:
    def coinChange(self, coins, amount):
        dp = [0] + [float("inf")] * amount
        for s in range(1, amount + 1):
            for c in coins:
                if c <= s and dp[s - c] + 1 < dp[s]:
                    dp[s] = dp[s - c] + 1
        return dp[amount] if dp[amount] != float("inf") else -1
