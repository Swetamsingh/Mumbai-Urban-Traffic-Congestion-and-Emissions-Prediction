# Dataset documentation

This project runs with a synthetic sample dataset for demonstration purposes so the model pipeline can be trained and evaluated without external downloads.

## Dataset name
Synthetic urban traffic sample

## Source
Generated locally for this project to demonstrate the full ML workflow and dashboard behavior.

## Download date and coverage
Generated in the repository as part of the prototype; sample period covers a representative hourly traffic pattern across several road segments.

## Columns
- `timestamp`: UTC timestamp for each observation.
- `road_segment_id`: road segment identifier.
- `traffic_speed_kmh`: observed average speed in kilometers per hour.
- `traffic_volume`: vehicles counted during the interval.
- `temperature_c`: road-side temperature in degrees Celsius.
- `rainfall_mm`: rainfall in millimeters during the interval.
- `road_type`: road category such as arterial or highway.

## Notes
- Data is observed and synthetic, not live traffic.
- It is intended for development, testing, and demonstration of the project architecture.
- Missing values are handled explicitly and no fabricated data is used for a production claim.
