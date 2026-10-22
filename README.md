# Greening predictive analysis

This repository is for an internship project built around the following question:

> Among locations with prior evidence of vegetation, does monthly greenness,
> measured by NDVI, improve land-surface-temperature estimates beyond season and
> location—and does that improvement hold in later years and unseen areas?

The first assignment is about handling the data correctly. It has two parts:

1. recreate the supplied 5,000-location reference sample; and
2. write a data dictionary in your own words.

These tasks come before predictive modelling. They establish that the files have
been read, sampled, joined, and understood correctly.

## What is supplied

The project lead will provide the full source files through a private NYU Box or
Google Drive link. The link should not be added to this repository.

The bundle may be supplied as `greening_predictive_source_data_v1.zip`. If so,
place it in the repository's top-level directory and extract it there; it will create
`data/source/`. If the files are supplied individually, place them directly in
`data/source/`:

```text
data/source/
  evergreen_locations.parquet
  evergreen_monthly_2013.parquet
  evergreen_monthly_2014.parquet
  evergreen_monthly_2015.parquet
  evergreen_monthly_2016.parquet
  evergreen_monthly_2017.parquet
  evergreen_monthly_2018.parquet
  evergreen_monthly_2019.parquet
  evergreen_monthly_2020.parquet
  evergreen_monthly_2021.parquet
  evergreen_monthly_2022.parquet
  evergreen_monthly_2023.parquet
  evergreen_monthly_2024.parquet
  SHA256SUMS
  source_manifest.json
```

The annual files contain monthly NDVI and land-surface-temperature observations.
The locations file contains one row per `pixel_id` with its coordinates and its
full-period count of green months. Together, the annual files cover 461,695
locations and 141 months, from April 2013 through December 2024.

The repository itself contains a small but real reference dataset:

```text
data/sample/evergreen_reference_sample.parquet
```

It contains 5,000 locations and the complete 141-month history of each location.
It is suitable for learning, testing code, and prototyping. It is not intended for
final scientific estimates.

The full source files and any recreated outputs are deliberately ignored by Git.
Do not force-add them.

## Initial setup

Clone the repository, create a Python environment, and install the small set of
required packages:

```bash
git clone https://github.com/tmulumba/greening_predictive.git
cd greening_predictive
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Obtain the source-data link privately from the project lead and copy the downloaded
files into `data/source/`. From that directory, verify that the files arrived intact:

```bash
cd data/source
shasum -a 256 -c ../../docs/source_data_checksums.sha256
cd ../..
```

On a system that provides `sha256sum` instead of `shasum`, use:

```bash
cd data/source
sha256sum -c ../../docs/source_data_checksums.sha256
cd ../..
```

Before doing any work, create a branch:

```bash
git switch -c intern/sample-recreation
```

## Task 1: recreate the reference sample

Write a script named:

```text
scripts/recreate_reference_sample.py
```

The script should build the reference sample from the annual files and the locations
file. Do not sample individual monthly rows. Select locations once, then keep the
complete monthly history for every selected location.

### Step 1: inspect the inputs

Before sampling, check the files rather than assuming they are correct:

1. List the columns and storage types in each kind of file.
2. Confirm that `pixel_id` occurs only once in the locations file.
3. Confirm that an annual file has no duplicate `pixel_id`–`year`–`month` rows.
4. Confirm that every annual file refers to the same set of locations.
5. Record unexpected results instead of silently dropping or changing records.

### Step 2: select exactly 5,000 locations

Use this deterministic procedure so that the same locations are selected on every
computer:

1. Take the distinct `pixel_id` values from the monthly data.
2. Write each ID as an ordinary base-10 integer, with no spaces, decimal point,
   leading zeros, or newline.
3. Put the exact text `greening-predictive-v1:` immediately before the ID. For
   example, pixel 123 becomes `greening-predictive-v1:123`.
4. Encode that text as UTF-8 and calculate its SHA-256 hash.
5. Sort the locations by that hash, from smallest to largest. Use the numeric
   `pixel_id` as a tie-breaker.
6. Take the first 5,000 locations.

Do not use Python's built-in `hash()` function, and do not apply a random sample to
the 65 million monthly rows. Both approaches can produce the wrong sample.

### Step 3: assemble and join the sample

1. Filter every annual file to the selected locations.
2. Append the filtered annual files.
3. Join coordinates from `evergreen_locations.parquet` using `pixel_id`.
4. Keep missing NDVI or LST measurements as missing—do not drop or fill them.
5. Confirm that the join does not change the number of monthly rows.
6. Confirm that every selected location receives longitude and latitude.
7. Keep the columns in this order:

   ```text
   pixel_id, year, month, ndvi, lst, lon, lat
   ```

8. Sort by `pixel_id`, `year`, and `month`.
9. Write the result to:

   ```text
   outputs/evergreen_reference_sample_recreated.parquet
   ```

Here, one row represents one location in one calendar month. The expected result has:

- 5,000 distinct locations;
- 705,000 rows;
- 45,000 rows in 2013, because the panel begins in April;
- 60,000 rows in each year from 2014 through 2024;
- no duplicate `pixel_id`–`year`–`month` combinations; and
- no missing coordinates.

The reference-sample manifest in
`data/sample/reference_sample_manifest.json` contains additional checks. Use these
checks to find errors; do not change the selection rule merely to force a match.

### Step 4: check the recreation

Run the supplied checker:

```bash
python scripts/check_recreated_sample.py \
  outputs/evergreen_reference_sample_recreated.parquet
```

The checker compares table contents rather than Parquet file bytes. Two programs can
write equivalent Parquet tables with different internal metadata or compression.

Create `docs/sample_recreation_report.md` and briefly report:

- how you read and combined the annual files;
- how you selected locations;
- how you performed and checked the join;
- the row, location, duplicate, and missing-value checks;
- whether your output matched the reference; and
- any problem or ambiguity you encountered.

## Task 2: create the data dictionary

Create:

```text
docs/data_dictionary.csv
```

The dictionary should contain one row for every field in:

- the annual monthly files;
- the locations file; and
- the reference sample.

Use at least these headings:

```text
file_group
field
storage_type
units_or_crs
plain_language_definition
unit_of_observation
allowed_values_or_range
missing_value_meaning
source_or_derivation
notes_or_caveats
```

Also document, for each file group:

- what one row represents;
- its date coverage;
- its row count and number of unique locations;
- its primary or candidate key;
- how it joins to the other files; and
- the number or percentage of missing values in each field.

Inspect the files and supporting notes before writing definitions. Write in plain
language that another researcher could understand. Do not guess. If something cannot
be established, write `To be confirmed` and raise it as a question in the pull request.
Use `docs/data_background.md` as source material, but independently inspect the files
for types, ranges, keys, and missingness.

## Important scientific distinction

The supplied “ever-green” universe is retrospective. A location enters it if NDVI was
greater than 0.2 in at least three months somewhere in the complete April 2013–December
2024 record. That definition is useful for describing historical analysis support.

It must not be used unchanged to claim that a model generalizes to later years. For a
later-year test, eligibility must be recalculated using only information available in
the training period—for example, at least three green months through December 2021.
Eligible locations must then be frozen before 2022–2024 are evaluated. In the reference
sample, 4,317 of the 5,000 locations meet that pre-2022 rule; 683 qualify only later.

The eventual project tests predictive improvement and generalization. It does not, by
itself, establish that NDVI causally changes land-surface temperature.

## What to submit

Open a draft pull request containing:

- `scripts/recreate_reference_sample.py`;
- any necessary update to `requirements.txt`;
- `docs/sample_recreation_report.md`;
- `docs/data_dictionary.csv`; and
- a short list of unresolved questions, if any.

Do not commit the annual source files, the full locations file, recreated Parquet
outputs, caches, credentials, access links, or machine-specific absolute paths.
Before every commit, run `git status` and inspect exactly what is staged.
