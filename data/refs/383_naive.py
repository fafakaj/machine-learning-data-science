class Solution:
    def canConstruct(self, ransomNote, magazine):
        rest = list(magazine)
        for ch in ransomNote:
            if ch not in rest:
                return False
            rest.remove(ch)
        return True
