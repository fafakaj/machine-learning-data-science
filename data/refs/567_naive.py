class Solution:
    def checkInclusion(self, s1, s2):
        target = sorted(s1)
        for i in range(len(s2) - len(s1) + 1):
            if sorted(s2[i:i + len(s1)]) == target:
                return True
        return False
