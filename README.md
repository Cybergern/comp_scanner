## Description

This is a tool for https://data.styrkelyft.se/. One big feature that is missing currently is a way to gather up all results from the past series into one collection so you can see all results a particular club has done during a series. This tool uses Selenium to scrape all competition data between the given dates. I have only tested it with Chrome, other browsers might work, try it.

### Usage

Just run python comp_scanner.py <start_date> <end_date> <club_name> <file_name>
Example: python .\comp_scanner.py 2026-01-21 2026-03-22 "Stockholms AK" serie1_2026.csv

This will scan all competitions between the given dates and save all results by the given club to the given file name
