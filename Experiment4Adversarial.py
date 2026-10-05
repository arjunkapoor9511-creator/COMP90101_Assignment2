import csv
import os
import time

import Experiment1 as E1
import Experiment4 as E4
import MaxHeap as H

EXPERIMENT4_ADVERSARIAL_ROOT = "Experiment4Adversarial"

# Reuse Experiment 1's sigma_1..sigma_5 exactly: same seeds, lengths, folders
SEQUENCE_CONFIGS = E1.SEQUENCE_CONFIGS


def runExperiment4Adversarial(dataSource=None):
    """
    Adversarial variant of Experiment 4: the same comparison (push-one-by-
    one vs bulk-load + heapify), but the keys are sorted ascending before
    being fed to either method, instead of left in their original random
    order. This is push-one-by-one's genuine worst case: every single
    insertion is a new maximum, so every push's bubbleUp call must climb
    all the way to the root (O(log n) per insertion, O(n log n) total over
    the whole sequence), whereas heapify()'s O(n) bound is input-order-
    independent and stays cheap regardless. Reuses the exact same
    underlying key VALUES as Experiment 4 (same seeds/configs via
    Experiment1.SEQUENCE_CONFIGS), so only the insertion ORDER differs
    between the two experiments - everything else about the comparison is
    held constant.

    `dataSource` behaves exactly as in Experiment4.runExperiment4(): None
    (default) auto-detects per config whether Experiment 1 already wrote
    that config's file (loadDataFromFile if so, else generateData); pass
    Experiment4.loadDataFromFile or Experiment4.generateData directly to
    force one approach for every config.

    Writes one row per sequence length to
    Experiment4Adversarial/results.csv, with the same columns as
    Experiment 4's own results.csv, so the two files can be compared
    side by side.
    """
    os.makedirs(EXPERIMENT4_ADVERSARIAL_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT4_ADVERSARIAL_ROOT, "results.csv")

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(["SequenceLength", "PushOneByOneRuntimeSeconds", "HeapifyRuntimeSeconds"])

        for seed, sequenceLength, folder in SEQUENCE_CONFIGS:
            if dataSource is not None:
                source = dataSource
            else:
                # flag: has Experiment 1 already generated this config's data on disk?
                alreadyGenerated = os.path.isfile(os.path.join(folder, "OperationsSequence.txt"))
                source = E4.loadDataFromFile if alreadyGenerated else E4.generateData
            keys = sorted(source(seed, sequenceLength, folder))   # the one difference vs Experiment4

            # Two independent copies so neither method's input list can affect the other's.
            pushKeys = list(keys)
            heapifyKeys = list(keys)

            H.reset()                        # empty heap, untimed, so push-one-by-one starts clean
            start = time.perf_counter()      # --- timing starts: only MaxHeap.push() calls below ---
            for key in pushKeys:
                H.push(key)
            pushRuntime = time.perf_counter() - start   # --- timing stops here ---

            H.reset()                        # clear the pushed heap, untimed, before the heapify method
            start = time.perf_counter()      # --- timing starts: only loadUnordered()+heapify() below ---
            H.loadUnordered(heapifyKeys)
            H.heapify()
            heapifyRuntime = time.perf_counter() - start  # --- timing stops here ---

            writer.writerow([sequenceLength, pushRuntime, heapifyRuntime])
            resultsFile.flush()
