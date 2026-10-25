class Solution:
    def isAnagram(self, s, t):
        rest = list(t)
        for ch in s:
            if ch not in rest:
                return False
            rest.remove(ch)
        return not rest
