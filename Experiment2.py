import csv
import os
import random
import time

import Competitor as C
import DataGenerator as G
import MaxHeap as H

EXPERIMENT2_ROOT = "Experiment2"
SEQUENCE_LENGTH = 1_000_000      # L = 1M, fixed per spec for every config in Experiment 2

# (seed, getTopPercentage, folder) for sigma_1..sigma_5: getTop = 0.1%, 0.5%, 1%, 5%, 10%
SEQUENCE_CONFIGS = [
    (6, 0.1, "Experiment2/GetTop0.1pct"),
    (7, 0.5, "Experiment2/GetTop0.5pct"),
    (8, 1, "Experiment2/GetTop1pct"),
    (9, 5, "Experiment2/GetTop5pct"),
    (10, 10, "Experiment2/GetTop10pct"),
]


def generateData(seed, getTopPercentage, dataFolder):
    """
    Seed the generator, then build a fixed-length (SEQUENCE_LENGTH) sequence
    where each operation is a getTop with probability getTopPercentage/100,
    and a push otherwise. The push/getTop decision is drawn from the same
    seeded random stream as the keys themselves (random.random() shares
    state with DataGenerator's random.randint() calls), so the entire
    sequence is fully determined by `seed` alone. Creates `dataFolder` if
    it doesn't exist yet and writes the sequence to OperationsSequence.txt
    inside it. Returns the operations array (not just keys, since this
    sequence mixes two operation types).
    """
    G.setSeed(seed)
    probability = getTopPercentage / 100
    operations = [None] * SEQUENCE_LENGTH
    for i in range(SEQUENCE_LENGTH):
        if random.random() < probability:
            operations[i] = G.genGetTop()
        else:
            operations[i] = G.genPush()
    os.makedirs(dataFolder, exist_ok=True)
    filePath = os.path.join(dataFolder, "OperationsSequence.txt")
    G.writeFile(filePath, operations)
    return operations


def runExperiment2():
    """
    Run Experiment 2: for each (seed, getTopPercentage, folder) in
    SEQUENCE_CONFIGS, generate the mixed push/getTop sequence, then time
    replaying it against MaxHeap and against Competitor, sequentially and
    separately. Each row (getTopPercentage, heap runtime, competitor
    runtime) is appended to Experiment2/results.csv as soon as that config
    finishes.
    """
    os.makedirs(EXPERIMENT2_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT2_ROOT, "results.csv")

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(["GetTopPercentage", "MaxHeapRuntimeSeconds", "CompetitorRuntimeSeconds"])

        for seed, getTopPercentage, folder in SEQUENCE_CONFIGS:
            operations = generateData(seed, getTopPercentage, folder)

            # Two independent copies so the heap and array runs can't affect each other's input.
            heapOps = list(operations)
            arrayOps = list(operations)

            H.reset()                        # clear heap state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: only MaxHeap.push()/getTop() below ---
            for op in heapOps:
                if op[0] == 1:
                    H.push(op[1])
                else:
                    H.getTop()
            heapRuntime = time.perf_counter() - start   # --- timing stops here ---

            C.reset()                        # clear array state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: only Competitor.push()/getTop() below ---
            for op in arrayOps:
                if op[0] == 1:
                    C.push(op[1])
                else:
                    C.getTop()
            arrayRuntime = time.perf_counter() - start  # --- timing stops here ---

            writer.writerow([getTopPercentage, heapRuntime, arrayRuntime])
            resultsFile.flush()
