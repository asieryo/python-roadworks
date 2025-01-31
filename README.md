# XML Roadworks Parsing Project
This project is designed to parse and analyze XML files containing roadworks data. It processes the XML files, groups works by road, sort the roads by the number of works, shows the longest work for every road and then filter signficant works for the roads. Finally, generates the HTML report.

## Key Features
### Duplicate Removal:
Duplicate data has been removed from the XML files. Works with the same reference number have been eliminated.

### Grouping and Sorting by Road:
All data is grouped by the road, and the resulting list is sorted by the roads with the most works. For each road, the longest work (the most important one) is selected. Additionally, a list of significant works (those lasting more than 6 months) for each road is created.

### Total Work Count:
The total count of roadworks may appear inflated due to similar works that have the same duration, similar authorities, or expected delays. However, these works are counted as separate because, within the data file, they represent distinct entries that may be important for the client.

## How It Works
### Parse XML Files:
The XML files containing the roadworks data are parsed using Python’s xml.etree.ElementTree library.

### Generate HTML Report:
An HTML report is generated, displaying the grouped data, sorted by the number of works for each road, along with details about the longest and most significant works.

## Usage
Install Dependencies: Make sure you have Python (3.x) installed on your system.

> python xml_parser.py

View the Report: The script generates an HTML report, which can be opened in any web browser to visualize the grouped and filtered data.
