import csv
import os

import Experiment1 as E1
import Experiment4 as E4

EXPERIMENT_NODE_TRACK_ROOT = "Experiment4NodeTrack"

# Reuse Experiment 1's sigma_1..sigma_5 exactly: same seeds, lengths, folders
SEQUENCE_CONFIGS = E1.SEQUENCE_CONFIGS


def bubbleDownTracked(a, i, n):
    """
    Same logic as MaxHeap.bubbleDown(i), but operates on a plain local array
    `a` of size `n` (never touching MaxHeap's module state) and returns how
    many swaps this single call performed - i.e. how many levels this one
    node sank. 0 means the node was already in place on the first check.
    """
    swaps = 0
    while True:
        c = 2 * i + 1
        if c >= n:
            break
        r = c + 1
        if r < n and a[r] > a[c]:
            c = r
        if a[c] <= a[i]:
            break
        a[i], a[c] = a[c], a[i]
        i = c
        swaps += 1
    return swaps


def heapifyTracked(keys):
    """
    Runs the same bottom-up heapify as MaxHeap.heapify() over a private
    copy of `keys`, visiting internal nodes in the same order (last
    internal node up to the root), but records each node's own swap count
    instead of discarding it. Returns (swapCounts, a): the list of
    per-node swap counts in visiting order, and the resulting array - the
    latter lets a caller verify the result is actually a valid heap.
    """
    a = list(keys)
    n = len(a)
    swapCounts = []
    for i in range(n // 2 - 1, -1, -1):
        swapCounts.append(bubbleDownTracked(a, i, n))
    return swapCounts, a


def bubbleUpTracked(a, i):
    """
    Same logic as MaxHeap.bubbleUp(i), but operates on a plain local array
    `a` and returns how many swaps this single call performed instead of
    discarding the count - i.e. how many levels this one just-inserted
    node rose. 0 means it was already in place relative to its parent.
    """
    swaps = 0
    while i > 0:
        p = (i - 1) >> 1
        if a[p] >= a[i]:
            break
        a[i], a[p] = a[p], a[i]
        i = p
        swaps += 1
    return swaps


def pushOneByOneTracked(keys):
    """
    Builds a heap by inserting `keys` one at a time into a private array,
    mirroring MaxHeap.push()'s placement-then-bubbleUp exactly, but records
    each insertion's own swap count instead of discarding it. Unlike
    heapifyTracked (which only visits internal nodes - n//2 of them, since
    leaves are already valid one-element heaps on their own), every single
    key here triggers its own bubbleUp call, so there are n swap counts,
    one per insertion, in push order. Returns (swapCounts, a): the
    per-insertion swap counts, and the resulting array - the latter lets a
    caller verify the result is actually a valid heap.
    """
    n = len(keys)
    a = [0] * n
    swapCounts = [0] * n
    for i in range(n):
        a[i] = keys[i]
        swapCounts[i] = bubbleUpTracked(a, i)
    return swapCounts, a


def buildHistogramRow(operation, sequenceLength, swapCounts, maxSwapsSeen):
    """Tabulate one operation's swap counts into a single CSV row of bucket counts."""
    histogram = {}
    for swaps in swapCounts:
        histogram[swaps] = histogram.get(swaps, 0) + 1
    totalNodes = len(swapCounts)
    averageSwaps = sum(swapCounts) / totalNodes
    rowCounts = [histogram.get(s, 0) for s in range(maxSwapsSeen + 1)]
    return [operation, sequenceLength, totalNodes, averageSwaps] + rowCounts


def runExperiment4NodeTrack():
    """
    For each (seed, sequenceLength, folder) in SEQUENCE_CONFIGS (reused
    from Experiment 1), load its keys the same way Experiment4 does
    (Experiment 1's file if already generated, else regenerate from the
    seed), then track BOTH construction methods' per-node swap counts over
    the SAME keys: heapifyTracked (bottom-up heapify, via bubbleDown) and
    pushOneByOneTracked (via bubbleUp). This tests both halves of the
    construction-method comparison at the node level: heapify()'s O(n)
    claim that most nodes sink only a short distance, and push()'s O(log n)
    per-insertion claim that most insertions only rise a short distance.

    Writes one row per (operation, sequenceLength) pair to
    Experiment4NodeTrack/results.csv - a "Heapify" row and a "Push" row for
    every sequence length, all sharing one header, since both are the same
    kind of measurement (a per-node/per-insertion swap-count histogram).
    Columns: Operation ("Heapify" or "Push"), SequenceLength,
    TotalNodesTracked (n//2 internal nodes for Heapify vs n insertions for
    Push - see the two tracked functions above for why they differ),
    AverageSwaps, then Swaps_0, Swaps_1, ... Swaps_K for every swap count
    observed across BOTH operations and ALL sequence lengths, so every row
    shares one consistent set of columns.

    Note: this overwrites results.csv rather than appending to whatever is
    already on disk. The column schema changed (Operation is new), so a
    literal file-append would concatenate two CSVs with different headers
    into one broken file; rebuilding it fresh achieves the same end goal -
    the file now holds both operations' data together - without that
    corruption.
    """
    os.makedirs(EXPERIMENT_NODE_TRACK_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT_NODE_TRACK_ROOT, "results.csv")

    perConfigSwapCounts = []   # [(operation, sequenceLength, swapCounts), ...]
    maxSwapsSeen = 0
    for seed, sequenceLength, folder in SEQUENCE_CONFIGS:
        if os.path.isfile(os.path.join(folder, "OperationsSequence.txt")):
            keys = E4.loadDataFromFile(seed, sequenceLength, folder)
        else:
            keys = E4.generateData(seed, sequenceLength, folder)

        heapifySwaps, _ = heapifyTracked(keys)
        pushSwaps, _ = pushOneByOneTracked(keys)

        maxSwapsSeen = max(maxSwapsSeen, max(heapifySwaps), max(pushSwaps))
        perConfigSwapCounts.append(("Heapify", sequenceLength, heapifySwaps))
        perConfigSwapCounts.append(("Push", sequenceLength, pushSwaps))

    swapColumns = [f"Swaps_{s}" for s in range(maxSwapsSeen + 1)]
    header = ["Operation", "SequenceLength", "TotalNodesTracked", "AverageSwaps"] + swapColumns

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(header)
        for operation, sequenceLength, swapCounts in perConfigSwapCounts:
            writer.writerow(buildHistogramRow(operation, sequenceLength, swapCounts, maxSwapsSeen))
