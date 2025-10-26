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
    print(f"New file will be saved as: {new_file}")
    return new_file



def get_doctype_line(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('<!DOCTYPE'):
                return line.strip()
    return None



def insert_doctype(xml_file, doctype_line):
    with open(xml_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('<?xml'):
            insert_index = i + 1
            break
    else:
        insert_index = 0
    lines.insert(insert_index, doctype_line + "\n")
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'DOCTYPE line inserted: {doctype_line}')



def load_speaker_mode_channel_map(csv_path):
    df = pd.read_csv(csv_path, delimiter=';')
    mapping = {}
    for _, row in df.iterrows():
        studio_ids = [s.strip() for s in str(row.get('spontaneous_studio', '')).split(';') if s.strip()]
        telephone_ids = [s.strip() for s in str(row.get('spontaneous_telephone', '')).split(';') if s.strip()]
        for spk in studio_ids:
            mapping[spk] = ('spontaneous', 'studio')
        for spk in telephone_ids:
            mapping[spk] = ('spontaneous', 'telephone')
    return mapping



def change_mode_channel(xml_path, csv_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mapping = load_speaker_mode_channel_map(csv_path)
    changes = 0

    for turn in root.findall('.//Turn'):
        spk = turn.get('speaker')
        if not spk:
            continue
        for spk_id in spk.split():
            if spk_id in mapping:
                mode, channel = mapping[spk_id]
                turn.set('mode', mode)
                turn.set('channel', channel)
                print(f"Set speaker={spk_id}, mode={mode}, channel={channel}")
                changes += 1
    new_file = get_name(xml_path)
    tree.write(new_file, encoding='utf-8', xml_declaration=True)
    
    
    
    doctype_line = get_doctype_line(xml_path)
    if doctype_line:
        insert_doctype(new_file, doctype_line)
    print(f"Total Turns updated by CSV: {changes}")



def main():
    args = argument_parsers()
    change_mode_channel(args.xml_path, args.csv_path)

if __name__ == '__main__':
    main()
