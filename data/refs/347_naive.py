class Solution:
    def topKFrequent(self, nums, k):
        distinct = list(set(nums))
        distinct.sort(key=lambda x: -nums.count(x))
        return distinct[:k]
