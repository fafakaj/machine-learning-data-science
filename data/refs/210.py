class Solution:
    def findOrder(self, numCourses, prerequisites):
        graph = [[] for _ in range(numCourses)]
        for a, b in prerequisites:
            graph[b].append(a)
        state = [0] * numCourses
        post = []
        for start in range(numCourses):
            if state[start]:
                continue
            stack = [(start, iter(graph[start]))]
            state[start] = 1
            while stack:
                node, it = stack[-1]
                nxt = next(it, None)
                if nxt is None:
                    state[node] = 2
                    post.append(node)
                    stack.pop()
                elif state[nxt] == 1:
                    return []
                elif state[nxt] == 0:
                    state[nxt] = 1
                    stack.append((nxt, iter(graph[nxt])))
        return post[::-1]
