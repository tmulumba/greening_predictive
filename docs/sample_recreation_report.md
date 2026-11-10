# Sample recreation report

## Population and output

- Eligibility was calculated using April 2013–December 2021 only (105 months):
  a pixel is eligible when at least three non-missing monthly NDVI values are
  strictly greater than 0.2.
- The extract includes all 399,674 eligible pixels and every monthly record for
  them from April 2013 through December 2024. No locations were downsampled and
  no monthly values were averaged or removed due to missingness or low NDVI.
- Every eligible pixel is included (no sampling or deliberate oversampling of
  locations; inclusion probability is 1). The spatial holdout randomly assigns
  whole blocks, so its share of pixels need not equal its share of blocks; no
  population sampling weights are applied.
- The output has 56,354,034 pixel-month rows: 3,597,066 in 2013 and 4,796,088
  in each year from 2014 through 2024. `pixel_id`–`year`–`month` is the row key.
- Missing measurements were preserved: 448,562 NDVI values (0.796%) and
  3,253,595 LST values (5.773%) are missing.
- No exact zero NDVI values occur in the eligible curated records. Zero-as-NoData
  values in the source exports were already converted to missing; the extraction
  adds no zero-value filter. The full raw-record comparison ensures no values
  were newly filtered or changed.

## Geographic labels

- All 461,695 source location IDs were unique, had finite coordinates, and
  matched the IDs in every annual file. Annual month coverage, monthly key
  uniqueness, and source schemas were checked before extraction.
- Coordinates were joined on `pixel_id`; all output rows have a coordinate pair.
  Longitude and latitude were projected from EPSG:4326 to EPSG:32640 with
  `always_xy=True`.
- Tile indices use the fixed (0, 0) UTM origin and
  `floor(easting_m / 1000)` / `floor(northing_m / 1000)`. The extract has 2,160
  unique 1-km tiles.
- Provisional block indices use `floor(tile_col / 4)` /
  `floor(tile_row / 4)`, producing 229 unique 4-km blocks. Negative indices use
  mathematical floor; no origin was reset to the sample minimum.
- A seeded SHA-256 ranking of occupied block IDs (seed `42`) assigned 46 of 229
  blocks (20.1%) to `spatial_test`; all pixels in a block share its assignment.
  This corresponds to 99,092 pixels (24.8%) because occupied blocks have
  different pixel counts. Assignments are independent of NDVI and LST outcomes.
- The calendar labels are `fit` (April 2013–December 2021), `validation`
  (January–December 2022), and `final_evaluation` (January 2023–December 2024).
  `analysis_role` combines those periods with geography: development-area
  observations follow those three calendar uses; spatial-test rows are marked
  `unseen_area_test`, `reserved_unseen_area_2022`, or
  `later_year_unseen_area_test`. Spatial-test LST must not be used for fitting
  or model selection and should only be evaluated after model choices are frozen.
- Block assignments, eligibility labels, and calendar roles are stored in the
  monthly Parquet extract; they are not written to separate output tables.
  Re-running `scripts/recreate_reference_sample.py` with the same seed
  reproduces the block assignment.

## Validation and limitations

- The combined extraction and validation script checks the output schema,
  total and annual row counts, missing-value totals, eligibility counts,
  geographic and calendar roles, coordinates, and fixed-origin tile/block
  calculations.
- Its streaming checks matched all 56,354,034 extracted pixel/date/NDVI/LST
  records against the curated annual Parquet inputs. It also checked duplicate
  keys, monthly date coverage, and chronological year ordering without loading
  the full panel into memory. The script prints a quality summary rather than
  writing additional output files.
- The repository contains curated Parquet exports rather than the original
  NumPy arrays, so comparison to original arrays was not possible.
- The selected blocks are scattered, not contiguous, and no exclusion buffer
  was applied because its distance is not yet approved. The supervisor should
  confirm whether this random-block design and buffer are acceptable before
  final scientific evaluation.
- The 4-km grouping is provisional. Grid labels and random block assignment do
  not by themselves establish spatial independence.
- The supervisor review checkpoint for eligibility, geography, split design,
  and buffer remains necessary before EDA.
- Eligibility depends on the specified pre-2022 NDVI period. The source files'
  longer-period green-month count was not used to select pixels.