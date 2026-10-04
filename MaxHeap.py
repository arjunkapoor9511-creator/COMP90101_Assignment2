CAPACITY = 10**6        # the heap never holds more than 10^6 elements

A = [0] * CAPACITY      # the heap array, allocated once
n = 0                   # number of elements currently in the heap


def reset():
    """Empty the heap. Only A[0..n-1] is meaningful, so setting n = 0 is enough."""
    global n
    n = 0


# ----------------------------------------------------------------------
# Core helpers
# ----------------------------------------------------------------------
def bubbleUp(i):
    """
    Move the element at index i UP, swapping it with its parent while the
    parent is smaller. O(log n).
    """
    a = A                    # local alias: local lookups are faster than global
    while i > 0:
        p = (i - 1) >> 1     # parent index (>> 1 is integer divide by 2)
        if a[p] >= a[i]:
            break            # heap property holds, stop
        a[i], a[p] = a[p], a[i]   # swap child and parent
        i = p                # continue from the parent's position


def bubbleDown(i):
    """
    Move the element at index i DOWN, swapping it with its LARGER child while
    that child is bigger. Swapping with the larger child makes it the parent,
    so the heap property holds on both sides. O(log n).
    """
    a = A
    m = n                    # local copy of the size
    while True:
        c = 2 * i + 1        # left child
        if c >= m:
            break            # no children: i is a leaf
        r = c + 1            # right child
        if r < m and a[r] > a[c]:
            c = r            # pick the larger child
        if a[c] <= a[i]:
            break            # both children <= current, done
        a[i], a[c] = a[c], a[i]   # swap with the larger child
        i = c                # continue from the child's position


# ----------------------------------------------------------------------
# Public operations
# ----------------------------------------------------------------------
def push(key):
    """Place key in the next free slot (keeps the tree complete), then bubble up."""
    global n
    if n >= CAPACITY:
        raise OverflowError("heap is full")
    A[n] = key
    bubbleUp(n)
    n += 1


def getTop():
    """Return the max without removing it. O(1). None if empty."""
    if n == 0:
        return None
    return A[0]


def pop():
    """
    Remove and return the max. O(log n). None if empty.
    Save the root, move the LAST element to the root (keeps the tree
    complete), shrink the size, then bubble the new root down.
    """
    global n
    if n == 0:
        return None
    a = A
    top = a[0]
    n -= 1
    if n > 0:
        a[0] = a[n]
        bubbleDown(0)
    return top


def loadUnordered(keys):
    """Copy keys into the array as-is, without heap order. Follow with heapify()."""
    global n
    k = len(keys)
    if k > CAPACITY:
        raise OverflowError("too many keys")
    A[:k] = keys
    n = k


def heapify():
    """
    Turn A[0..n-1] (in any order) into a valid max-heap, bottom-up.
    Leaves (indices n//2 .. n-1) are already valid one-element heaps, so
    start at the last internal node (n//2 - 1) and bubble each node down,
    working back to the root.
    O(n) total: most nodes are near the bottom and sink only a short way.
    """
    for i in range(n // 2 - 1, -1, -1):
        bubbleDown(i)