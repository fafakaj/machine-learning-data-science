class Solution:
    def maxSubArray(self, nums):
        best = nums[0]
        for i in range(len(nums)):
            s = 0
            for j in range(i, len(nums)):
                s += nums[j]
                best = max(best, s)
        return best
