#!/usr/bin/env python3
"""Compare an intern-created sample with the tracked reference table."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


EXPECTED_COLUMNS = ["pixel_id", "year", "month", "ndvi", "lst", "lon", "lat"]
KEY_COLUMNS = ["pixel_id", "year", "month"]
EXPECTED_ROWS = 705_000
EXPECTED_PIXELS = 5_000
EXPECTED_ID_DIGEST = "8e7a3fbacc7608244516e2f9ee029357ac4c8fa73f8ea9349137e5ac62ac7002"


def id_digest(values: pd.Series) -> str:
    ids = sorted(int(value) for value in values.drop_duplicates())
    payload = "".join(f"{value}\n" for value in ids).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_sorted(path: Path) -> tuple[pd.DataFrame, object]:
    table = pq.read_table(path)
    frame = table.to_pandas()
    if all(column in frame.columns for column in KEY_COLUMNS):
        frame = frame.sort_values(KEY_COLUMNS, kind="mergesort").reset_index(drop=True)
    return frame, table.schema


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Path to the recreated Parquet file")
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data/sample/evergreen_reference_sample.parquet",
    )
    args = parser.parse_args()

    errors: list[str] = []
    if not args.candidate.exists():
        raise SystemExit(f"Candidate file does not exist: {args.candidate}")
    if not args.reference.exists():
        raise SystemExit(f"Reference file does not exist: {args.reference}")

    candidate, candidate_schema = load_sorted(args.candidate)
    reference, reference_schema = load_sorted(args.reference)

    if list(candidate.columns) != EXPECTED_COLUMNS:
        errors.append(
            f"Columns differ. Expected {EXPECTED_COLUMNS}; found {list(candidate.columns)}"
        )
    if candidate_schema != reference_schema:
        errors.append(
            "Arrow storage types differ from the reference.\n"
            f"  Expected: {reference_schema}\n"
            f"  Found:    {candidate_schema}"
        )
    if len(candidate) != EXPECTED_ROWS:
        errors.append(f"Expected {EXPECTED_ROWS:,} rows; found {len(candidate):,}")
    if "pixel_id" in candidate:
        pixels = int(candidate["pixel_id"].nunique(dropna=False))
        if pixels != EXPECTED_PIXELS:
            errors.append(f"Expected {EXPECTED_PIXELS:,} locations; found {pixels:,}")
        digest = id_digest(candidate["pixel_id"])
        if digest != EXPECTED_ID_DIGEST:
            errors.append(f"Selected pixel IDs differ (digest {digest})")
    if all(column in candidate for column in KEY_COLUMNS):
        duplicate_count = int(candidate.duplicated(KEY_COLUMNS).sum())
        if duplicate_count:
            errors.append(f"Found {duplicate_count:,} duplicate pixel-year-month rows")
    for coordinate in ["lon", "lat"]:
        if coordinate in candidate and candidate[coordinate].isna().any():
            errors.append(f"Column {coordinate} contains missing coordinates")

    if list(candidate.columns) == EXPECTED_COLUMNS and len(candidate) == len(reference):
        try:
            pd.testing.assert_frame_equal(
                candidate,
                reference,
                check_dtype=True,
                check_exact=False,
                rtol=0.0,
                atol=1e-7,
            )
        except AssertionError as exc:
            errors.append(f"Table values differ from the reference: {exc}")

    if errors:
        print("Sample check FAILED:\n")
        for number, error in enumerate(errors, start=1):
            print(f"{number}. {error}")
        return 1

    year_counts = candidate.groupby("year", dropna=False).size().to_dict()
    print("Sample check PASSED")
    print(f"  Rows: {len(candidate):,}")
    print(f"  Locations: {candidate['pixel_id'].nunique():,}")
    print(f"  Years: {min(year_counts)}–{max(year_counts)}")
    print(f"  Missing NDVI rows: {candidate['ndvi'].isna().sum():,}")
    print(f"  Missing LST rows: {candidate['lst'].isna().sum():,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
