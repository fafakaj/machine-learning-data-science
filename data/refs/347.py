class Solution:
    def topKFrequent(self, nums, k):
        counts = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]
        for x, c in counts.items():
            buckets[c].append(x)
        out = []
        for c in range(len(nums), 0, -1):
            for x in buckets[c]:
                out.append(x)
                if len(out) == k:
                    return out
