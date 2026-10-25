class Solution:
    def isSubtree(self, root, subRoot):
        def same(a, b):
            if a is None or b is None:
                return a is b
            return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)
        stack = [root]
        while stack:
            node = stack.pop()
            if node:
                if same(node, subRoot):
                    return True
                stack += [node.left, node.right]
        return False
