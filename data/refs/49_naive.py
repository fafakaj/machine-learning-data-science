class Solution:
    def groupAnagrams(self, strs):
        groups = []
        for s in strs:
            for g in groups:
                if sorted(g[0]) == sorted(s):
                    g.append(s)
                    break
            else:
                groups.append([s])
        return groups
