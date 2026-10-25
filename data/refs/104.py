class Solution:
    def maxDepth(self, root):
        level = [root] if root else []
        depth = 0
        while level:
            depth += 1
            level = [c for n in level for c in (n.left, n.right) if c]
        return depth
