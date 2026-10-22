# Data layout

- `source/` is for the annual files and locations file supplied privately by the
  project lead. Its data files are ignored by Git.
- `sample/` contains the tracked 5,000-location reference sample and its manifest.
- recreated data should be written to `../outputs/`, which is also ignored by Git.

The reference sample is intentionally small enough for code development. Final
scientific estimates must use an appropriately defined analysis population and the
full relevant data, not the 5,000-location teaching sample.
