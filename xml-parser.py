import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, List, Dict, Union

def get_element_child_text_value(element: ET.Element, child_tag: str) -> str:
    return element.findtext(child_tag, "")

def group_data_by_child(child_name: str, root: ET.Element) -> DefaultDict[str, list[ET.Element]]:
    def sort_dict_by_values_length(dict_to_sort: DefaultDict[str, list[ET.Element]]) -> DefaultDict[str, list[ET.Element]]:
        return defaultdict(list, sorted(dict_to_sort.items(), key=lambda item: len(item[1]), reverse=True))

    group_data_by_child: DefaultDict[str, list[ET.Element]] = defaultdict(list)
    for planned_work in root.findall("ha_planned_works"):
        data_to_group_by = planned_work.find(child_name)
        group_data_by_child[data_to_group_by.text].append(planned_work)
    return sort_dict_by_values_length(group_data_by_child)

def write_html_file(file_name: str, html_content: str):
    with open(file_name + ".html", "w", encoding="utf-8") as file:
        file.write(html_content)

def get_days_between_dates(start_date: str, end_date: str) -> int:
    def parse_date(date_string: str) -> datetime:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

    return (parse_date(end_date) - parse_date(start_date)).days

def get_longest_work_for_road(grouped_by_road: DefaultDict[str, list[ET.Element]]) -> Dict[str, Dict[str, Union[str, int]]]:
    max_differences_by_road = {}

    for road, works in grouped_by_road.items():
        first_work = works[0]
        max_diff = {
            "max_days": get_days_between_dates(get_element_child_text_value(first_work, "start_date"), get_element_child_text_value(first_work, "end_date")),
            "start_date": get_element_child_text_value(first_work, "start_date"),
            "end_date": get_element_child_text_value(first_work, "end_date"),
            "reference_number": get_element_child_text_value(first_work, "reference_number"),
            "location": get_element_child_text_value(first_work, "location"),
            "expected_delay": get_element_child_text_value(first_work, "expected_delay"),
            "description": get_element_child_text_value(first_work, "description"),
            "traffic_management": get_element_child_text_value(first_work, "traffic_management"),
            "closure_type": get_element_child_text_value(first_work, "closure_type"),
            "local_authority": get_element_child_text_value(first_work, "local_authority")
        }

        for work in works[1:]:
            start_date_str = get_element_child_text_value(work, "start_date")
            end_date_str = get_element_child_text_value(work, "end_date")

            diff = get_days_between_dates(start_date_str, end_date_str)

            if diff >= max_diff["max_days"]:
                max_diff = {
                    "max_days": diff,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "reference_number": get_element_child_text_value(work, "reference_number"),
                    "location": get_element_child_text_value(work, "location"),
                    "expected_delay": get_element_child_text_value(work, "expected_delay"),
                    "description": get_element_child_text_value(work, "description"),
                    "traffic_management": get_element_child_text_value(work, "traffic_management"),
                    "closure_type": get_element_child_text_value(work, "closure_type"),
                    "local_authority": get_element_child_text_value(work, "local_authority")
                }

        max_differences_by_road[road] = max_diff

    return max_differences_by_road

def filter_and_sort_significant_works(grouped_by_road: DefaultDict[str, list[ET.Element]], significant_work_threshold: int) -> DefaultDict[str, list[ET.Element]]:
    filtered_works: DefaultDict[str, list[ET.Element]] = defaultdict(list)

    for road, works in grouped_by_road.items():
        significant_works_with_duration = [
            (work, get_days_between_dates(get_element_child_text_value(work, "start_date"), get_element_child_text_value(work, "end_date")))
            for work in works
        ]

        significant_works_with_duration_filtered = [
            (work, duration) for work, duration in significant_works_with_duration if duration >= significant_work_threshold
        ]

        filtered_works[road] = [work for work, _ in sorted(significant_works_with_duration_filtered, key=lambda item: item[1], reverse=True)]

    return filtered_works

def merge_xml_files(file1_route: str, file2_route: str) -> ET.Element:
    def append_if_not_seen(root, already_seen, merged_root):
        for child in root:
            child_reference = get_element_child_text_value(child, "reference_number")
            if(child_reference) not in already_seen:
                merged_root.append(child)
                already_seen.add(child_reference)

    tree1 = ET.parse(file1_route)
    tree2 = ET.parse(file2_route)

    root1 = tree1.getroot()
    root2 = tree2.getroot()

    merged_root = ET.Element(root1.tag)

    already_seen = set()

    append_if_not_seen(root1, already_seen, merged_root)
    append_if_not_seen(root2, already_seen, merged_root)

    return merged_root

def generate_html_table(grouped_by_road: DefaultDict[str, list[ET.Element]], max_differences_by_road: Dict[str, Dict[str, Union[str, int]]], significative_works: DefaultDict[str, list[ET.Element]]) -> str:
    
    def generate_longest_work_html(grouped_by_road: DefaultDict[str, list[ET.Element]], max_differences_by_road: Dict[str, Dict[str, Union[str, int]]]) -> str:
        
        def generate_significative_works_html(significative_works_list: List[ET.Element]) -> str:
            significative_works_html = "<ul>"
            for significative_work in significative_works_list:
                significative_works_html += f"""
                    <li>
                        Ref: <strong>{get_element_child_text_value(significative_work, "reference_number")}</strong>
                        <ul>
                            <li>
                                Duration: {get_days_between_dates(get_element_child_text_value(significative_work, "start_date"), get_element_child_text_value(significative_work, "end_date"))} days
                            </li>
                            <li>
                                Location: {get_element_child_text_value(significative_work, "location")}
                            </li>
                            <li>
                                Expected delay: {get_element_child_text_value(significative_work, "expected_delay")}
                            </li>
                            <li>
                                Traffic management: {get_element_child_text_value(significative_work, "traffic_management")}
                            </li>
                        </ul>
                    </li>
                    <br>
                """
            significative_works_html += "</ul>"

            return significative_works_html

        longest_work_html = ""
        for road_name, road_values in grouped_by_road.items():
            longest_work_html += f"""
            <tr>
                <td>{road_name}</td>
                <td>{len(road_values)}</td>
                <td>
                    <ul>
                        <li>Duration: {max_differences_by_road[road_name]["max_days"]} days</li>
                        <li>Description: {max_differences_by_road[road_name]["description"]}</li>
                        <li>Traffic management: {max_differences_by_road[road_name]["traffic_management"]}</li>
                        <li>Closure type: {max_differences_by_road[road_name]["closure_type"]}</li>
                        <li>Local authority: {max_differences_by_road[road_name]["local_authority"]}</li>
                        <li>Start: {max_differences_by_road[road_name]["start_date"]}, end: {max_differences_by_road[road_name]["end_date"]}</li>
                        <li>Reference number: {max_differences_by_road[road_name]["reference_number"]}</li>
                        <li>Location: {max_differences_by_road[road_name]["location"]}</li>
                        <li>Expected delay: {max_differences_by_road[road_name]["expected_delay"]}</li>
                    </ul>
                </td>
                <td>
                    {generate_significative_works_html(significative_works[road_name])}
                </td>
            <tr>
            """
        
        return longest_work_html

    html_table = """
        <table>
            <tr>
                <th>Road</th>
                <th>Total planned works</th>
                <th>Longest work</th>
                <th style="min-width: 500px">Significative works (more than six months)</th>
            </tr>
          """
    
    html_table += generate_longest_work_html(grouped_by_road, max_differences_by_road)
    html_table += """
        </table>\n
    """

    return html_table
    
significant_work_threshold = 180

root = merge_xml_files("./xml-files/he_roadworks_2016_02_29.xml", "./xml-files/he_roadworks_2016_03_07.xml")

grouped_by_road = group_data_by_child("road", root)

max_differences_by_road = get_longest_work_for_road(grouped_by_road)
significative_works = filter_and_sort_significant_works(grouped_by_road, significant_work_threshold)

html_init_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Planned Roadworks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2 { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>Planned Roadworks</h1>
"""
html_final_content = """</body>
</html>
"""

html_content = html_init_content + generate_html_table(grouped_by_road, max_differences_by_road, significative_works) + html_final_content

write_html_file("roadwork_data", html_content)
print("HTML file \"roadworks.html\" generated successfully!")
