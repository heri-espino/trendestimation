"""Download additional *real* FHWA NGSIM episodes with auditable raw pages.

Each run writes to a NEW persistent VM data directory. No simulated rows,
no silent input substitution, and no writes to old Paper C data/results.

Example:
    python fetch_real_ngsim.py --data-dir "C:/.../experiment004/run001/data"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://data.transportation.gov/resource/8ect-6jqj.csv"
DOI = "10.21949/1504477"
SITES = ("us-101", "i-80")
FIELDS = "vehicle_id,frame_id,global_time,local_y,local_x,location"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def query_url(site: str, offset: int, page_size: int, max_vehicle_id: int) -> str:
    if site not in SITES:
        raise ValueError(f"Unrecognized NGSIM site: {site}")
    parameters = {
        "$select": FIELDS,
        "$where": f"location = '{site}' AND vehicle_id >= 1 AND vehicle_id <= {max_vehicle_id}",
        "$order": "vehicle_id ASC, global_time ASC, frame_id ASC",
        "$limit": str(page_size),
        "$offset": str(offset),
    }
    return BASE + "?" + urllib.parse.urlencode(parameters)


def fetch_page(url: str, destination: Path, retries: int = 3) -> bytes:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite raw source page: {destination}")
    last = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "TrendEstimation-NGSIM-Research/1.0",
                    "Accept": "text/csv",
                },
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
            if not raw or b"vehicle_id" not in raw[:600]:
                raise ValueError("NGSIM returned an empty or unrecognized CSV response")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
            return raw
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(min(8, 2 ** attempt))
    raise RuntimeError(f"NGSIM page download failed after {retries} attempts: {url}") from last


def parse_page(raw: bytes, site: str) -> list[tuple[int, int, int, float, float]]:
    rows = []
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    needed = {"vehicle_id", "frame_id", "global_time", "local_y", "local_x", "location"}
    if not needed.issubset(set(reader.fieldnames or [])):
        raise ValueError(f"NGSIM source schema changed: {reader.fieldnames}")
    for row in reader:
        if row["location"].strip().lower() != site:
            raise ValueError("Unexpected location in site-specific NGSIM page")
        try:
            vid = int(float(row["vehicle_id"]))
            frame = int(float(row["frame_id"]))
            timestamp = int(float(row["global_time"]))
            longitudinal = float(row["local_y"]) * 0.3048
            lateral = float(row["local_x"]) * 0.3048
            if not all(map(__import__("math").isfinite, (longitudinal, lateral))):
                raise ValueError("Nonfinite coordinate")
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"Malformed NGSIM record, not silently discarded: {row}") from exc
        rows.append((vid, timestamp, frame, longitudinal, lateral))
    return rows


def split_episodes(
    rows: list[tuple[int, int, int, float, float]],
) -> list[list[tuple[int, int, int, float, float]]]:
    """Episode boundaries include reused IDs and timing/frame discontinuities."""
    rows.sort(key=lambda row: (row[0], row[1], row[2]))
    output = []
    current = []
    for row in rows:
        if current:
            previous = current[-1]
            if not (
                row[0] == previous[0]
                and row[1] - previous[1] == 100
                and row[2] - previous[2] == 1
            ):
                output.append(current)
                current = []
        current.append(row)
    if current:
        output.append(current)
    return output


def eligible(episode: list, origin: int, min_frames: int) -> tuple[bool, str]:
    """Quality selection only uses historical positions, not future error."""
    import numpy as np

    if len(episode) < max(min_frames, origin + 20):
        return False, "short"
    historical = np.asarray([r[3] for r in episode[:origin]], dtype=float)
    speed = np.diff(historical) / 0.1
    if np.any(~np.isfinite(speed)):
        return False, "nonfinite"
    # Same preexisting broad screening convention, applied to observed past only.
    if np.mean(speed >= -1.0) < 0.87 or np.quantile(np.abs(speed), 0.99) >= 65:
        return False, "historic_speed_screen"
    return True, "ok"


def extract_site(
    site: str, raw_dir: Path, data_dir: Path, *, max_vehicle_id: int,
    page_size: int, max_pages: int, origin: int, min_frames: int,
    max_episodes: int,
) -> tuple[list[dict], list[dict], dict]:
    pages = []
    rows = []
    exhausted = False
    for page in range(max_pages):
        url = query_url(site, page * page_size, page_size, max_vehicle_id)
        location = raw_dir / site / f"page{page:04d}.csv"
        raw = fetch_page(url, location)
        batch = parse_page(raw, site)
        pages.append({
            "site": site, "page": page, "url": url,
            "file_relative_to_data": str(location.relative_to(data_dir)).replace("\\", "/"),
            "sha256": sha256(location), "bytes": location.stat().st_size,
            "n_rows": len(batch),
        })
        rows.extend(batch)
        print(f"Downloaded {site} page {page + 1}: {len(batch)} positions", flush=True)
        if len(batch) < page_size:
            exhausted = True
            break
    if not rows:
        raise RuntimeError(f"No real NGSIM records returned for site {site}.")
    episodes = split_episodes(rows)
    # If the API page cap was hit, the last episode could be incomplete.
    if not exhausted and episodes:
        episodes.pop()
    reason_counts: Counter = Counter()
    chosen = []
    for seq in episodes:
        passes, reason = eligible(seq, origin=origin, min_frames=min_frames)
        reason_counts[reason] += 1
        if not passes:
            continue
        vid, start, _, _, _ = seq[0]
        chosen.append({
            "episode_id": f"{site}_{vid}_{start}",
            "site": site, "vehicle_id": vid,
            "first_timestamp_ms": start,
            "last_timestamp_ms": seq[-1][1],
            "n_frames": len(seq),
            "session_proxy": f"{site}_{int(start // (15 * 60 * 1000))}",
            "rows": seq,
        })
        if len(chosen) >= max_episodes:
            break
    metadata = {
        "site": site, "source_rows_downloaded": len(rows),
        "pages": pages, "pagination_exhausted": exhausted,
        "last_episode_dropped_if_capped": not exhausted,
        "eligibility_counts_until_target": dict(reason_counts),
        "n_selected": len(chosen),
        "id_reuse_caveat": (
            "Vehicle_ID can repeat; physical independence across sessions "
            "or recording episodes is not guaranteed."
        ),
    }
    return chosen, pages, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=20000)
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--max-vehicle-id", type=int, default=500)
    parser.add_argument("--max-episodes-per-site", type=int, default=100)
    parser.add_argument("--min-frames", type=int, default=140)
    parser.add_argument("--origin", type=int, default=100)
    args = parser.parse_args()
    if not (100 <= args.page_size <= 50000 and 1 <= args.max_pages <= 100):
        parser.error("Page size or page limit is outside documented bounds.")
    if args.max_vehicle_id < 1 or args.origin < 100 or args.max_episodes_per_site < 1:
        parser.error("Positive vehicle cap, episode cap, and origin >= 100 required.")

    root = args.data_dir.resolve()
    raw = root / "raw"
    if (root / "episode_catalog.json").exists() or (root / "selected_positions.csv").exists():
        raise FileExistsError("Refusing to overwrite an existing episode selection")
    root.mkdir(parents=True, exist_ok=True)
    selected = []
    metadata = []
    for site in SITES:
        episodes, _, site_metadata = extract_site(
            site, raw, root, max_vehicle_id=args.max_vehicle_id,
            page_size=args.page_size, max_pages=args.max_pages,
            origin=args.origin, min_frames=args.min_frames,
            max_episodes=args.max_episodes_per_site,
        )
        selected.extend(episodes)
        metadata.append(site_metadata)
    if not selected:
        raise RuntimeError("No qualifying real NGSIM episodes; no synthetic fallback")

    positions = root / "selected_positions.csv"
    catalog = []
    with positions.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "episode_id", "site", "vehicle_id", "timestamp_ms",
            "frame_id", "longitudinal_m", "lateral_m",
        ])
        for episode in selected:
            for vid, timestamp, frame, y, x in episode["rows"]:
                writer.writerow([
                    episode["episode_id"], episode["site"], vid,
                    timestamp, frame, format(y, ".10g"), format(x, ".10g"),
                ])
            catalog.append({k: v for k, v in episode.items() if k != "rows"})
    manifest = {
        "schema": 1, "status": "complete",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_title": "FHWA Next Generation Simulation Vehicle Trajectories",
        "official_doi": DOI,
        "source_url": "https://data.transportation.gov/d/8ect-6jqj",
        "license": "CC BY-SA 3.0; FHWA/USDOT attribution required",
        "selection_type": "first eligible by ordered site, vehicle ID, and start timestamp",
        "selection_does_not_use_future_forecast_errors": True,
        "target_episodes_per_site": args.max_episodes_per_site,
        "origin_frame": args.origin, "minimum_frames": args.min_frames,
        "max_vehicle_id": args.max_vehicle_id,
        "page_size": args.page_size, "max_pages": args.max_pages,
        "sites": metadata,
        "episode_count": len(selected),
        "selected_positions_csv_sha256": sha256(positions),
        "selected_positions_csv_bytes": positions.stat().st_size,
        "reference_sample_dt_seconds": 0.1,
        "unit_conversion": "NGSIM Local_Y/Local_X in feet; multiply by exactly 0.3048",
        "uniqueness_warning": (
            "Episode IDs are (site, vehicle_id, start_ms), NOT certified "
            "unique physical vehicle identities."
        ),
    }
    (root / "episode_catalog.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8",
    )
    (root / "download_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({
        "episode_count": len(selected),
        "by_site": {row["site"]: row["n_selected"] for row in metadata},
        "positions_sha256": manifest["selected_positions_csv_sha256"],
        "output_directory": str(root),
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
