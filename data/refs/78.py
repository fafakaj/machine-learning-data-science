class Solution:
    def subsets(self, nums):
        out = []
        path = []
        def go(i):
            if i == len(nums):
                out.append(path[:])
                return
            go(i + 1)
            path.append(nums[i])
            go(i + 1)
            path.pop()
        go(0)
        return out
