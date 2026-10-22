"""Build a flat, journal-ready Springer Nature LaTeX source package.

Computational Statistics instructions explicitly forbid subfolders in uploaded
LaTeX source archives. The research repository keeps the convenient
sections/ and figures/ layout; ONLY the submission ZIP is flattened.

The package carries the exact December 2024 official sn-jnl.cls, its
author--year bibliography style, a self-contained manuscript, and existing
vector PDF figures. It does not regenerate measurements or invent results.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

PAPER = Path(__file__).resolve().parent
CLASS_GIT_SHA = "d25f07cb51c685e90a4ab97e95479826289486d4"
BST_GIT_SHA = "35533152b3a21c47815f2fe194fef46285c4ccd8"
SOURCE_FILES = ("main.tex", "bibliografia.bib", "sn-jnl.cls", "sn-mathphys-ay.bst")
# Only rewrite file references that are LaTeX source dependencies,
# never manuscript prose or printed texttt paths.
PATTERN = re.compile(
    r"\\(input|includegraphics|IfFileExists)\s*(?:\[[^\]]*\])?"
    r"\s*\{([^{}]+)\}"
)


def git_blob_sha(content: bytes) -> str:
    prefix = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(prefix + content).hexdigest()


def package(output: Path, *, require_pdf: bool = True) -> list[str]:
    for filename, expected in (
        ("sn-jnl.cls", CLASS_GIT_SHA),
        ("sn-mathphys-ay.bst", BST_GIT_SHA),
    ):
        path = PAPER / filename
        if not path.is_file() or git_blob_sha(path.read_bytes()) != expected:
            raise ValueError(
                f"{filename} differs from the user's official December 2024 "
                "Springer Nature archive; restore the exact template before packaging"
            )
    required = [PAPER / name for name in SOURCE_FILES]
    if require_pdf:
        required.append(PAPER / "main.pdf")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing files for submission package: " + ", ".join(missing)
        )

    # Avoid a stale old ZIP being accidentally treated as current output.
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    copied: dict[str, tuple[Path, bytes]] = {}

    def add_file(source: Path, name: str, data: bytes) -> None:
        if "/" in name or "\\" in name or name in {"", ".", ".."}:
            raise ValueError(f"Invalid flat archive filename: {name}")
        previous = copied.get(name)
        if previous is not None and previous[0] != source:
            raise ValueError(f"Filename collision: {previous[0]} and {source}")
        copied[name] = (source, data)

    def resolve_source(reference: str, *, suffix: str = "") -> Path:
        path = (PAPER / (reference + suffix)).resolve()
        # Do not let a LaTeX filename escape the paper directory.
        if PAPER.resolve() not in path.parents:
            raise ValueError(f"Disallowed source path: {reference}")
        return path

    seen_tex: set[Path] = set()

    def add_tex(path: Path) -> None:
        path = path.resolve()
        if path in seen_tex:
            return
        if not path.is_file():
            raise FileNotFoundError(path)
        seen_tex.add(path)
        text = path.read_text(encoding="utf-8")

        def rewrite(match: re.Match[str]) -> str:
            command, ref = match.groups()
            extension = ".tex" if command == "input" and not Path(ref).suffix else ""
            resource = resolve_source(ref, suffix=extension)
            target = resource.name
            if not resource.is_file():
                if command == "IfFileExists":
                    # Optional plots remain disabled if no data were measured.
                    return match.group(0).replace("{" + ref + "}", "{" + target + "}")
                raise FileNotFoundError(
                    f"Missing manuscript dependency for {command}: {resource}"
                )
            if resource.suffix == ".tex":
                add_tex(resource)
            else:
                add_file(resource, target, resource.read_bytes())
            return match.group(0).replace("{" + ref + "}", "{" + target + "}")

        updated = PATTERN.sub(rewrite, text)
        # The template uses \bibliography{bibliografia} and the class selects
        # the author--year .bst automatically, without extra custom macros.
        add_file(path, path.name, updated.encode("utf-8"))

    add_tex(PAPER / "main.tex")
    for name in SOURCE_FILES[1:]:
        path = PAPER / name
        add_file(path, name, path.read_bytes())
    if require_pdf:
        path = PAPER / "main.pdf"
        add_file(path, path.name, path.read_bytes())

    # A source archive should not contain any subdirectories, TeX aux files,
    # private data or giant outputs. Only referenced artifacts are included.
    with tempfile.NamedTemporaryFile(
        suffix=".zip", prefix="computational-statistics-", dir=output.parent,
        delete=False,
    ) as temporary:
        tmp = Path(temporary.name)
    try:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(copied):
                archive.writestr(name, copied[name][1])
        tmp.replace(output)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"[springer] Created flat submission ZIP: {output}")
    print(f"[springer] Included {len(copied)} files, with no subdirectories")
    return sorted(copied)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=PAPER / "computational-statistics-submission.zip",
    )
    parser.add_argument(
        "--allow-no-pdf", action="store_true",
        help="For test/package inspection only; journal upload needs a PDF",
    )
    args = parser.parse_args()
    package(args.output, require_pdf=not args.allow_no_pdf)


if __name__ == "__main__":
    main()
