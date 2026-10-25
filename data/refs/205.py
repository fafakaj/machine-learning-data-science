class Solution:
    def isIsomorphic(self, s, t):
        st, ts = {}, {}
        for a, b in zip(s, t):
            if st.setdefault(a, b) != b or ts.setdefault(b, a) != a:
                return False
        return True
