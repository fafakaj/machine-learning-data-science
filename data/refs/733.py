class Solution:
    def floodFill(self, image, sr, sc, color):
        old = image[sr][sc]
        if old == color:
            return image
        def fill(r, c):
            if 0 <= r < len(image) and 0 <= c < len(image[0]) and image[r][c] == old:
                image[r][c] = color
                fill(r + 1, c); fill(r - 1, c); fill(r, c + 1); fill(r, c - 1)
        fill(sr, sc)
        return image
