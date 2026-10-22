# Background notes for documenting the data

These notes are source material for the intern-created data dictionary. They are not
the dictionary itself.

- `pixel_id` is a zero-based identifier for a fixed analysis-grid location. It is the
  key shared by the monthly and location files; it is not a person or household ID.
- `year` and `month` are calendar fields. The first stored month is April 2013 and the
  final stored month is December 2024.
- `ndvi` is monthly normalized difference vegetation index. It is dimensionless and
  stored as a 32-bit floating-point value. A missing value is not zero; it indicates
  that no valid value is stored for that location-month.
- `lst` is monthly daytime Landsat land-surface temperature in degrees Celsius, stored
  as a 32-bit floating-point value. It is surface temperature, not air temperature or
  experienced temperature. A missing value is not zero.
- `lon` and `lat` are longitude and latitude in decimal degrees using EPSG:4326. They
  identify the nominal centre of an approximately 30 m analysis-grid location.
- `green_months_2013_2024` counts months in the complete stored period for which raw
  NDVI is greater than 0.2. It is the field used to describe the retrospective
  ever-green support rule.
- The annual files preserve a row for every one of the 141 location-month slots for
  each included location, including rows with missing NDVI or LST.
- The annual package contains only locations that have at least three months with NDVI
  greater than 0.2 somewhere in the complete April 2013–December 2024 period.
- The source panel was derived from Landsat products processed in Google Earth Engine.
  The historical monthly products are analysis-ready derivatives; the exact executed
  monthly NDVI workflow and complete scene inventory were not retained. This limitation
  should be recorded rather than replaced by an assumed upstream workflow.

The data dictionary should add evidence obtained by inspecting the files, including
storage types, observed ranges, missingness, row counts, keys, and join relationships.
