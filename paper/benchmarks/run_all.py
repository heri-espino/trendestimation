"""Execute the two paper-only PLS benchmark suites in one reproducible command.

From the repository root:
  python paper/benchmarks/run_all.py --preset quick --repeats 5
  python paper/benchmarks/run_all.py --preset full --repeats 7
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke","quick","full"), default="quick")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--blas-threads", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE/"results")
    args = parser.parse_args()
    if args.repeats < 1 or args.blas_threads < 1:
        parser.error("repeats and blas-threads must be positive")
    for script in ("run_benchmarks.py", "trace_benchmarks.py"):
        command = [
            sys.executable, str(HERE/script),
            "--preset", args.preset,
            "--repeats", str(args.repeats),
            "--blas-threads", str(args.blas_threads),
            "--output-dir", str(args.output_dir.resolve()),
        ]
        print("Running", " ".join(command), flush=True)
        subprocess.run(command, check=True)
    print("All numerical checks passed; files saved at", args.output_dir.resolve())


if __name__ == "__main__":
    main()
