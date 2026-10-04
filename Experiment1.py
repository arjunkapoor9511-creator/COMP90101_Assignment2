import csv
import os
import time

import Competitor as C
import DataGenerator as G
import MaxHeap as H

EXPERIMENT1_ROOT = "Experiment1"

# (seed, sequenceLength, folder) for sigma_1..sigma_5: L = 0.1M, 0.2M, 0.5M, 0.8M, 1M
SEQUENCE_CONFIGS = [
    (1, 100_000, "Experiment1/L0.1M"),
    (2, 200_000, "Experiment1/L0.2M"),
    (3, 500_000, "Experiment1/L0.5M"),
    (4, 800_000, "Experiment1/L0.8M"),
    (5, 1_000_000, "Experiment1/L1M"),
]


def generateData(seed, sequenceLength, dataFolder):
    """
    Seed the generator, then build a push-only sequence of `sequenceLength`
    operations. Creates `dataFolder` if it doesn't exist yet and writes the
    sequence to OperationsSequence.txt inside it. Returns the keys as an array.
    """
    G.setSeed(seed)
    keys = [0] * sequenceLength
    operations = [None] * sequenceLength
    for i in range(sequenceLength):
        op = G.genPush()
        operations[i] = op
        keys[i] = op[1]
    os.makedirs(dataFolder, exist_ok=True)
    filePath = os.path.join(dataFolder, "OperationsSequence.txt")
    G.writeFile(filePath, operations)
    return keys


def runExperiment1():
    """
    Run Experiment 1: for each (seed, sequenceLength, folder) in
    SEQUENCE_CONFIGS, generate the push-only sequence, then time pushing
    its keys into MaxHeap and into Competitor, sequentially and separately.
    Each row (sequenceLength, heap runtime, competitor runtime) is appended
    to Experiment1/results.csv as soon as that sequence length finishes.
    """
    os.makedirs(EXPERIMENT1_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT1_ROOT, "results.csv")

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(["SequenceLength", "MaxHeapRuntimeSeconds", "CompetitorRuntimeSeconds"])

        for seed, sequenceLength, folder in SEQUENCE_CONFIGS:
            keys = generateData(seed, sequenceLength, folder)

            # Two independent copies so the heap and array runs can't affect each other's input.
            heapKeys = list(keys)
            arrayKeys = list(keys)

            H.reset()                        # clear heap state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: nothing but MaxHeap.push() below ---
            for key in heapKeys:
                H.push(key)
            heapRuntime = time.perf_counter() - start   # --- timing stops here ---

            C.reset()                        # clear array state from the previous config, untimed
            start = time.perf_counter()      # --- timing starts: nothing but Competitor.push() below ---
            for key in arrayKeys:
                C.push(key)
            arrayRuntime = time.perf_counter() - start  # --- timing stops here ---

            writer.writerow([sequenceLength, heapRuntime, arrayRuntime])
            resultsFile.flush()
