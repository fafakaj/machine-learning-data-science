"""Helpers for problem definitions.

A problem is a dict with the public spec fields (see app/py/harness.py) plus
build-only fields that never reach problems.json:

    brute   function(*args) -> expected, written independently of `ref`
    ref     reference solution source (saved to app/data/refs/<id>.py)
    naive   slower correct solution source; must fail perf (saved to refs/<id>_naive.py)
    cases   hand-picked argument lists; the first `visible` of them are shown
    visible how many hand-picked cases are visible (default: len(examples))
    rand    function(rng) -> args for random small cross-check inputs
    perf    list of generator sources ("def gen(): ... return [args]")
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "py"))

import harness  # noqa: E402

build_tree = harness._build_tree
dump_tree = harness._dump_tree
TreeNode = harness.TreeNode


def rand_ints(rng, n_min, n_max, lo, hi):
    return [rng.randint(lo, hi) for _ in range(rng.randint(n_min, n_max))]


def rand_word(rng, n_min, n_max, alphabet="abc"):
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(n_min, n_max)))


def rand_tree(rng, n_max, lo=-10, hi=10, n_min=0):
    """Random binary tree with up to n_max nodes, as a LeetCode level-order list."""
    n = rng.randint(n_min, n_max)
    if n == 0:
        return []
    root = TreeNode(rng.randint(lo, hi))
    nodes = [root]
    for _ in range(n - 1):
        while True:
            parent = rng.choice(nodes)
            side = rng.choice(("left", "right"))
            if getattr(parent, side) is None:
                child = TreeNode(rng.randint(lo, hi))
                setattr(parent, side, child)
                nodes.append(child)
                break
    return dump_tree(root)


def rand_bst(rng, n_max, lo=-50, hi=50, n_min=0):
    """Random valid BST (distinct values) as a level-order list."""
    n = rng.randint(n_min, min(n_max, hi - lo + 1))
    values = rng.sample(range(lo, hi + 1), n)
    root = None
    for v in values:
        root = _bst_insert(root, v)
    return dump_tree(root)


def _bst_insert(root, v):
    if root is None:
        return TreeNode(v)
    if v < root.val:
        root.left = _bst_insert(root.left, v)
    else:
        root.right = _bst_insert(root.right, v)
    return root


def tree_values_inorder(level):
    out = []

    def walk(node):
        if node:
            walk(node.left)
            out.append(node.val)
            walk(node.right)

    walk(build_tree(level))
    return out


def rand_grid(rng, r_max, c_max, chars, weights=None, r_min=1, c_min=1):
    rows = rng.randint(r_min, r_max)
    cols = rng.randint(c_min, c_max)
    return [[rng.choices(chars, weights)[0] for _ in range(cols)] for _ in range(rows)]
