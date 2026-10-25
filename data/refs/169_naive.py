class Solution:
    def majorityElement(self, nums):
        for x in nums:
            c = 0
            for y in nums:
                if y == x:
                    c += 1
            if c * 2 > len(nums):
                return x
