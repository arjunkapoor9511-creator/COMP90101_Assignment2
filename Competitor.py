CAPACITY = 10**6        # the array never holds more than 10^6 elements

A = [0] * CAPACITY      # the backing array, allocated once
cnt = 0                  # number of elements currently in A
i_max = -1               # index of the largest element in A; -1 means A is empty


def reset():
    """Empty the array. Only A[0..cnt-1] is meaningful, so cnt = 0, i_max = -1 is enough."""
    global cnt, i_max
    cnt = 0
    i_max = -1


# ----------------------------------------------------------------------
# Public operations
# ----------------------------------------------------------------------
def push(key):
    """Append key at the back of A. O(1): i_max only needs a single comparison."""
    global cnt, i_max
    if cnt >= CAPACITY:
        raise OverflowError("array is full")
    A[cnt] = key
    if i_max == -1 or A[i_max] < A[cnt]:
        i_max = cnt
    cnt += 1


def getTop():
    """Return the max without removing it. O(1). None if empty."""
    if i_max == -1:
        return None
    return A[i_max]


def pop():
    """
    Remove and return the max. O(n): unlike the heap, the new max can only be
    found by rescanning every remaining element. None if empty.
    Save the max, swap it with the last element (so the removal itself is an
    O(1) overwrite), shrink cnt, then scan A[0..cnt-1] for the new max.
    """
    global cnt, i_max
    if i_max == -1:
        return None
    a = A                    # local alias: local lookups are faster than global
    key_max = a[i_max]
    a[i_max], a[cnt - 1] = a[cnt - 1], a[i_max]
    cnt -= 1
    if cnt == 0:
        i_max = -1
        return key_max
    best = 0
    for idx in range(1, cnt):
        if a[idx] > a[best]:
            best = idx
    i_max = best
    return key_max
