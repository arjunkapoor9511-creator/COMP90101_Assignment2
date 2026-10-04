import random

MAX_KEY = 10**7          # keys are drawn uniformly from [0, MAX_KEY], per spec


def setSeed(seed):
    """
    Seed the generator once at the start of a sequence/experiment. Every
    genElement()/genPush() call afterwards advances the same deterministic
    stream, so a fixed seed reproduces the exact same sequence end to end.
    """
    random.seed(seed)


def genElement():
    """Generate one random key in [0, MAX_KEY]. Call setSeed() beforehand for reproducibility."""
    return random.randint(0, MAX_KEY)


def genPush():
    """Generate a push operation (1, key) for a freshly generated key."""
    x = genElement()
    return (1, x)


def genPop():
    """Generate a pop operation (2,)."""
    return (2,)


def genGetTop():
    """Generate a getTop operation (3,)."""
    return (3,)


def writeFile(path, operations):
    """
    Write a sequence of operations to `path` in the spec's file format: the
    operation count on the first line, then one line per operation (its
    tuple values space-separated). The count is derived from `operations`,
    so the caller never has to track or pass it separately.
    """
    lines = [str(len(operations))]
    lines.extend(" ".join(map(str, op)) for op in operations)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
