class Solution:
    def minEatingSpeed(self, piles, h):
        k = 1
        while sum((p + k - 1) // k for p in piles) > h:
            k += 1
        return k
