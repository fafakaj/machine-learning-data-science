class Solution:
    def findKthLargest(self, nums, k):
        h = nums[:k]
        heapq.heapify(h)
        for x in nums[k:]:
            if x > h[0]:
                heapq.heapreplace(h, x)
        return h[0]
