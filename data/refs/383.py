class Solution:
    def canConstruct(self, ransomNote, magazine):
        stock = Counter(magazine)
        for ch in ransomNote:
            stock[ch] -= 1
            if stock[ch] < 0:
                return False
        return True
