class Solution:
    def combinationSum(self, candidates, target):
        out = []
        path = []
        def backtrack(start, remaining):
            if remaining == 0:
                out.append(path[:])
                return
            for i in range(start, len(candidates)):
                c = candidates[i]
                if c <= remaining:
                    path.append(c)
                    backtrack(i, remaining - c)
                    path.pop()
        backtrack(0, target)
        return out
