class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = [[] for _ in range(numCourses)]
        for a, b in prerequisites:
            graph[b].append(a)
        state = [0] * numCourses   # 0 new, 1 on the stack, 2 done
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
                    stack.pop()
                elif state[nxt] == 1:
                    return False
                elif state[nxt] == 0:
                    state[nxt] = 1
                    stack.append((nxt, iter(graph[nxt])))
        return True
