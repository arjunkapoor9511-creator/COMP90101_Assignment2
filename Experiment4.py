# DataGenerator's randomness is seeded deterministically (see DataGenerator.setSeed): the same
# seed, run through the same sequence of genPush() calls, reproduces the exact same key stream
# every time, on any machine - this was verified directly against Experiment 1's real output files
# on disk, not just two fresh runs matching each other. So in principle Experiment 4 could just
# regenerate sigma_1..sigma_5 from their seeds (generateData() below) and never touch a file.
#
# We benchmarked both approaches at the largest config (L = 1M) before picking one:
#   lite generateData (reseed + regenerate): ~0.49s
#   loadDataFromFile  (read + parse 1M lines): ~0.36s
# Reading the file back was the cheaper of the two - parsing a line of text costs less than the
# per-call Python overhead of genPush()/genElement()/random.randint() repeated a million times - so
# runExperiment4() uses loadDataFromFile() by default to save that time. The tradeoff: this makes
# Experiment 4 depend on Experiment 1 having already been run (its OperationsSequence.txt files
# must exist). generateData() is kept as the seed-only alternative for when that dependency isn't
# available - pass it explicitly as runExperiment4(dataSource=generateData).

import csv
import os
import time

import DataGenerator as G
import Experiment1 as E1
import MaxHeap as H

EXPERIMENT4_ROOT = "Experiment4"

# Reuse Experiment 1's sigma_1..sigma_5 exactly: same seeds, lengths, folders
SEQUENCE_CONFIGS = E1.SEQUENCE_CONFIGS


def generateData(seed, sequenceLength, dataFolder):
    """
    Lite data source: regenerate the push-only key sequence purely from the
    seed, with no file I/O. Relies on the proven guarantee that setSeed(seed)
    followed by the same genPush() call pattern Experiment1.generateData()
    uses reproduces the exact same keys Experiment1 already wrote to disk.
    `dataFolder` is accepted but unused here, kept only so this has the same
    (seed, sequenceLength, dataFolder) call contract as loadDataFromFile().
    """
    G.setSeed(seed)
    keys = [0] * sequenceLength
    for i in range(sequenceLength):
        keys[i] = G.genPush()[1]
    return keys


def loadDataFromFile(seed, sequenceLength, dataFolder):
    """
    Alternate data source, same (seed, sequenceLength, dataFolder) contract
    as generateData(), but reads the push-only key sequence back from the
    OperationsSequence.txt file already written to dataFolder (e.g. by
    Experiment 1) instead of regenerating it. `seed` is accepted but unused,
    kept only for interchangeability with generateData(). Raises if the
    file's declared operation count doesn't match sequenceLength.
    """
    filePath = os.path.join(dataFolder, "OperationsSequence.txt")
    with open(filePath) as f:
        lines = f.read().splitlines()
    count = int(lines[0])     # first line is only the operation count (DataGenerator.writeFile's
    if count != sequenceLength:  # header), not a key - used here purely to validate, then discarded
        raise ValueError(f"{filePath} declares {count} operations, expected {sequenceLength}")
    return [int(line.split()[1]) for line in lines[1:]]   # lines[1:] skips that count line entirely


def runExperiment4(dataSource=None):
    """
    Run Experiment 4: for each (seed, sequenceLength, folder) in
    SEQUENCE_CONFIGS (reused from Experiment 1), build the keys, then time
    two ways of constructing a MaxHeap from them: pushing one by one,
    versus bulk-loading then heapify(). MaxHeap keeps its state in
    module-level globals shared by every call, so the two methods WOULD
    interfere if run back to back without a reset: push-one-by-one leaves
    n == sequenceLength behind, and a second push-one-by-one run on top of
    that would double up elements and could overflow CAPACITY; conversely
    heapify()'s loadUnordered() would silently overwrite a prior push run's
    array. H.reset() between the two methods (untimed) keeps them fully
    isolated. Each row (sequenceLength, push-one-by-one runtime, heapify
    runtime) is appended to Experiment4/results.csv as soon as that config
    finishes.

    `dataSource` controls where each config's keys come from. Left at its
    default (None), each config is checked individually: if Experiment 1
    already wrote that config's OperationsSequence.txt, loadDataFromFile()
    is used (the cheaper option per the module header's benchmark);
    otherwise it falls back to generateData() so this still works even if
    Experiment 1 hasn't been run. Pass loadDataFromFile or generateData
    explicitly to force one approach for every config regardless of what's
    on disk.
    """
    os.makedirs(EXPERIMENT4_ROOT, exist_ok=True)
    resultsPath = os.path.join(EXPERIMENT4_ROOT, "results.csv")

    with open(resultsPath, "w", newline="") as resultsFile:
        writer = csv.writer(resultsFile)
        writer.writerow(["SequenceLength", "PushOneByOneRuntimeSeconds", "HeapifyRuntimeSeconds"])

        for seed, sequenceLength, folder in SEQUENCE_CONFIGS:
            if dataSource is not None:
                source = dataSource
            else:
                # flag: has Experiment 1 already generated this config's data on disk?
                alreadyGenerated = os.path.isfile(os.path.join(folder, "OperationsSequence.txt"))
                source = loadDataFromFile if alreadyGenerated else generateData
            keys = source(seed, sequenceLength, folder)

            # Two independent copies so neither method's input list can affect the other's.
            pushKeys = list(keys)
            heapifyKeys = list(keys)

            H.reset()                        # empty heap, untimed, so push-one-by-one starts clean
            start = time.perf_counter()      # --- timing starts: only MaxHeap.push() calls below ---
            for key in pushKeys:
                H.push(key)
            # the loop only reaches the next line once every push() call has returned, so all
            # pushes are guaranteed complete before the clock stops (plain synchronous execution)
            pushRuntime = time.perf_counter() - start   # --- timing stops here ---

            H.reset()                        # clear the pushed heap, untimed, before the heapify method
            start = time.perf_counter()      # --- timing starts: only loadUnordered()+heapify() below ---
            H.loadUnordered(heapifyKeys)
            H.heapify()
            # heapify() is a plain synchronous call; this line only runs once it has fully
            # returned, so its work is guaranteed complete before the clock stops
            heapifyRuntime = time.perf_counter() - start  # --- timing stops here ---

            writer.writerow([sequenceLength, pushRuntime, heapifyRuntime])
            resultsFile.flush()
