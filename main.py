import xml.etree.ElementTree as ET
import os
import argparse
import xml.etree.ElementTree as ET
import os
import argparse
import pandas as pd


def argument_parsers():
    parser = argparse.ArgumentParser(description="Process XML and CSV for speaker mode/channel update.")
    parser.add_argument("-p", "--path", dest="xml_path", required=True, help="Path to the XML file to process")
    parser.add_argument("-c", "--csv", dest="csv_path", required=True, help="Path to the CSV file for mapping")
    return parser.parse_args()


def get_name(name_file):
    base, ext = os.path.splitext(name_file)
    new_file = base + "_corrected" + ext
    return new_file


def get_doctype_line(xml_path):
    with open(xml_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("<!DOCTYPE"):
                return line.strip()
    return None


def insert_doctype(xml_file, doctype_line):
    with open(xml_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("<?xml"):
            insert_index = i + 1
            break
    else:
        insert_index = 0
    lines.insert(insert_index, doctype_line + "\n")
    with open(xml_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

def load_speaker_mode_channel_map(csv_path):
    df = pd.read_csv(csv_path, delimiter=";")
    mapping = {}
    ignored = set()

    # Map speakers to mode/channel per column
    for col, (mode, channel) in {
        "spontaneous_studio": ("spontaneous", "studio"),
        "spontaneous_telephone": ("spontaneous", "telephone"),
        "planned_studio": ("planned", "studio"),
    }.items():
        for spks in df[col].dropna():
            for spk in str(spks).split(";"):
                spk = spk.strip()
                if spk:
                    mapping[spk] = (mode, channel)

    # Load ignored speakers
    for spks in df["ignore"].dropna():
        for spk in str(spks).split(";"):
            spk = spk.strip()
            if spk:
                ignored.add(spk)

    return mapping, ignored


def write_xml_with_formatting(tree, file_path):
    # Write xml declaration line manually with double quotes and uppercase UTF-8
    declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

    # Serialize XML tree to string
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8", method="xml")
    xml_str = xml_bytes.decode("utf-8")

    # Remove spaces before self-closing tags "/>"
    xml_str = xml_str.replace(" />", "/>")

    # Write to file with manual declaration line
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(declaration)
        f.write(xml_str)

    print(f"\nFile saved with cleaned XML formatting: {file_path}")


def change_mode_channel(xml_path, csv_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mapping, ignored = load_speaker_mode_channel_map(csv_path)

    # Dictionary to group changes by attribute
    changed_attributes = {
        'mode': [],
        'channel': [],
    }

    for turn in root.findall(".//Turn"):
        spk = turn.get("speaker")
        if not spk:
            continue

        for spk_id in spk.split():
            if spk_id in ignored:
                continue
            if spk_id in mapping:
                mode, channel = mapping[spk_id]

                # Conditionally add mode attribute
                if "mode" not in turn.attrib:
                    turn.set("mode", mode)
                    changed_attributes['mode'].append(f"Speaker {spk_id} - added mode='{mode}'")

                # Conditionally add channel attribute
                if "channel" not in turn.attrib:
                    turn.set("channel", channel)
                    changed_attributes['channel'].append(f"Speaker {spk_id} - added channel='{channel}'")

    # Print grouped logs by attribute category
    for attr, changes_list in changed_attributes.items():
        if changes_list:
            print(f"\nChanged {attr}s:")
            for entry in changes_list:
                print(f"    {entry}")
        else:
            print(f"\nNo {attr}s changed.")

    print(f"\nTotal mode attributes modified: {len(changed_attributes['mode'])}")
    print(f"Total channel attributes modified: {len(changed_attributes['channel'])}")

    new_file = get_name(xml_path)
    write_xml_with_formatting(tree, new_file)

    doctype_line = get_doctype_line(xml_path)
    if doctype_line:
        insert_doctype(new_file, doctype_line)


def main():
    args = argument_parsers()
    change_mode_channel(args.xml_path, args.csv_path)


if __name__ == "__main__":
    main()
