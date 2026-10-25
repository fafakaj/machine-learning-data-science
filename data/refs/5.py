class Solution:
    def longestPalindrome(self, s):
        best = ""
        for c in range(2 * len(s) - 1):
            l, r = c // 2, (c + 1) // 2
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 > len(best):
                best = s[l + 1:r]
        return best
