class Solution:
    def rob(self, nums):
        prev = cur = 0
        for x in nums:
            prev, cur = cur, max(cur, prev + x)
        return cur
