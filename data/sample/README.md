# Reference sample

`evergreen_reference_sample.parquet` is the expected result for the first internship
task. It contains 5,000 deterministically selected locations and all 141 stored months
for each location, joined to longitude and latitude.

`reference_sample_manifest.json` records the selection rule and high-level validation
counts. Compare recreated tables by their contents, not by Parquet file checksum alone.

This sample is for learning, code development, and testing. It is not large enough for
final scientific estimates.
