from __future__ import annotations

import argparse
import builtins
import math
import random
import statistics
import time
from collections.abc import Callable

from pyd3js_array import (
    deviation,
    extent,
    max as d3max,
    mean,
    min as d3min,
    sum,
    variance,
)


def _timeit(fn: Callable[[], object], *, repeat: int) -> list[float]:
    out: list[float] = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        out.append(time.perf_counter() - t0)
    return out


def _fmt(label: str, times: list[float]) -> str:
    med = statistics.median(times)
    p95 = (
        statistics.quantiles(times, n=20)[-1]
        if len(times) >= 20
        else builtins.max(times)
    )
    return f"{label:<22} median={med * 1e3:8.2f}ms  p95={p95 * 1e3:8.2f}ms  (n={len(times)})"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Micro-benchmarks for pyd3js-array (no deps)."
    )
    parser.add_argument("--n", type=int, default=200_000, help="input size")
    parser.add_argument("--repeat", type=int, default=10, help="repeat count")
    parser.add_argument("--seed", type=int, default=0, help="PRNG seed")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    nums = [rng.random() for _ in range(args.n)]
    nums_with_holes = [
        (None if (i % 97 == 0) else (float("nan") if (i % 89 == 0) else nums[i]))
        for i in range(args.n)
    ]
    boxed = [{"v": x} for x in nums]

    def bench_pure_numbers() -> None:
        sum(nums)
        mean(nums)
        variance(nums)
        deviation(nums)
        extent(nums)
        d3min(nums)
        d3max(nums)

    def bench_holes() -> None:
        sum(nums_with_holes)  # type: ignore[arg-type]
        mean(nums_with_holes)  # type: ignore[arg-type]
        variance(nums_with_holes)  # type: ignore[arg-type]
        deviation(nums_with_holes)  # type: ignore[arg-type]
        extent(nums_with_holes)  # type: ignore[arg-type]

    def bench_accessors() -> None:
        sum(boxed, lambda d, i, a: d["v"])
        mean(boxed, lambda d, i, a: d["v"])
        variance(boxed, lambda d, i, a: d["v"])

    # Warmup
    bench_pure_numbers()
    bench_holes()
    bench_accessors()

    print(_fmt("pure_numbers", _timeit(bench_pure_numbers, repeat=args.repeat)))
    print(_fmt("with_none_nan", _timeit(bench_holes, repeat=args.repeat)))
    print(_fmt("accessor_dicts", _timeit(bench_accessors, repeat=args.repeat)))

    # Quick sanity: ensure we don't optimize away work.
    assert not math.isnan(mean(nums) or float("nan"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
