class Solution:
    def checkInclusion(self, s1, s2):
        m = len(s1)
        if m > len(s2):
            return False
        need = [0] * 26
        have = [0] * 26
        for ch in s1:
            need[ord(ch) - 97] += 1
        for i, ch in enumerate(s2):
            have[ord(ch) - 97] += 1
            if i >= m:
                have[ord(s2[i - m]) - 97] -= 1
            if have == need:
                return True
        return False
