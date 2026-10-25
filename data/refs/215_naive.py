class Solution:
    def findKthLargest(self, nums, k):
        nums = list(nums)
        for _ in range(k - 1):
            nums.remove(max(nums))
        return max(nums)
