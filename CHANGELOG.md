# Changelog

## September 2026: reproducible version

- Rebuilt the Udacity schema in SQLite (`data/processed/weather.db`) so the queries can be run by anyone.
- Replaced the Excel steps with code: the continent lookup (with the 18 country name fixes written down) and the moving averages (now a SQL window function and pandas).
- Updated the data with Berkeley Earth: global land average to 2024, city series to 2020.
- Found that Campinas/Guarulhos and Colombo/Curitiba have identical series, because they share a point of the Berkeley Earth grid.
- Fixed missing years stored as 0 in the spreadsheet, and incomplete years (2013 in the Udacity export) counted as full years.
- Changed the main comparison from absolute temperature to change since 1854–1900.
- Added an interactive report (`app/`).

## June 2024: first version

- Report for the Udacity Data Analyst Nanodegree: SQL extraction, moving averages and line chart in Excel, Brazil map in Python (Folium), comparison with Amsterdam and Dublin.
