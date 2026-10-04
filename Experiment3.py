import csv
import os
import random
import time

import Competitor as C
import DataGenerator as G
import MaxHeap as H

EXPERIMENT3_ROOT = "Experiment3"
SEQUENCE_LENGTH = 1_000_000      # L = 1M, fixed per spec for every config in Experiment 3

# (seed, popPercentage, folder) for sigma_1..sigma_5: pop = 0.1%, 0.5%, 1%, 5%, 10%
SEQUENCE_CONFIGS = [
    (11, 0.1, "Experiment3/Pop0.1pct"),
    (12, 0.5, "Experiment3/Pop0.5pct"),
    (13, 1, "Experiment3/Pop1pct"),
    (14, 5, "Experiment3/Pop5pct"),
    (15, 10, "Experiment3/Pop10pct"),
]


def generateData(seed, popPercentage, dataFolder):
    """
    Seed the generator, then build a fixed-length (SEQUENCE_LENGTH) sequence
    where each operation is a pop with probability popPercentage/100, and a
    push otherwise. The push/pop decision is drawn from the same seeded
    random stream as the keys themselves (random.random() shares state with
    DataGenerator's random.randint() calls), so the entire sequence is fully
    determined by `seed` alone. Creates `dataFolder` if it doesn't exist yet
    and writes the sequence to OperationsSequence.txt inside it. Returns
    (operations, actualPopPercentage): the operations array (not just keys,
    since this sequence mixes two operation types), and the actual pop
    percentage counted at generation time (total pops / SEQUENCE_LENGTH),
    which can differ slightly from the target popPercentage since each
    operation's type is a probabilistic draw.
    """
    G.setSeed(seed)
    probability = popPercentage / 100
    operations = [None] * SEQUENCE_LENGTH
    popCount = 0
    for i in range(SEQUENCE_LENGTH):
        if random.random() < probability:
            operations[i] = G.genPop()
            popCount += 1
        else:
            operations[i] = G.genPush()
    os.makedirs(dataFolder, exist_ok=True)
    filePath = os.path.join(dataFolder, "OperationsSequence.txt")
    G.writeFile(filePath, operations)
    actualPopPercentage = 100 * popCount / SEQUENCE_LENGTH
    return operations, actualPopPercentage


def runExperiment3():
    """
    Run Experiment 3: for each (seed, popPercentage, folder) in
    SEQUENCE_CONFIGS, generate the mixed push/pop sequence, then time
    replaying it against MaxHeap and against Competitor, sequentially and
    separately. Each row (target popPercentage, actual popPercentage, heap
    runtime, competitor runtime) is appended to Experiment3/results.csv as
    soon as that config finishes.
    """
    os.makedirs(EXPERIMENT3_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT3_ROOT, "results.csv")

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(["PopPercentage", "ActualPopPercentage", "MaxHeapRuntimeSeconds", "CompetitorRuntimeSeconds"])

        for seed, popPercentage, folder in SEQUENCE_CONFIGS:
            operations, actualPopPercentage = generateData(seed, popPercentage, folder)

            # Two independent copies so the heap and array runs can't affect each other's input.
            heapOps = list(operations)
            arrayOps = list(operations)

            H.reset()                        # clear heap state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: only MaxHeap.push()/pop() below ---
            for op in heapOps:
                if op[0] == 1:
                    H.push(op[1])
                else:
                    H.pop()
            heapRuntime = time.perf_counter() - start   # --- timing stops here ---

            C.reset()                        # clear array state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: only Competitor.push()/pop() below ---
            for op in arrayOps:
                if op[0] == 1:
                    C.push(op[1])
                else:
                    C.pop()
            arrayRuntime = time.perf_counter() - start  # --- timing stops here ---

            writer.writerow([popPercentage, actualPopPercentage, heapRuntime, arrayRuntime])
            resultsFile.flush()
