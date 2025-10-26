import xml.etree.ElementTree as ET
import os
import argparse



def argument_parsers():
    """Parse command-line arguments for the XML file path."""
    parser = argparse.ArgumentParser(description="Process an XML file to set mode and channel attributes.")
    parser.add_argument("-p", "--path", dest="xml_path", required=True, help="Path to the XML file to process")
    return parser.parse_args()



def get_name(name_file):
    """
    Args: name_file (str)
    Return: new_file (str)
    Generates a new filename for saving the modified XML.
    """
    base, ext = os.path.splitext(name_file)
    new_file = base + "_corrected" + ext
    print(f"New file will be saved as: {new_file}")
    return new_file



def get_doctype_line(xml_path):
    """Scans and returns the DOCTYPE line if present, otherwise returns None."""
    with open(xml_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('<!DOCTYPE'):
                return line.strip()
    return None



def insert_doctype(xml_file, doctype_line):
    """Inserts the DOCTYPE after the XML prologue."""
    with open(xml_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()


    # Find XML
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




def change_mode_channel(xml_path):
    """Update <Turn> tags by adding missing 'mode' or 'channel', and save the file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    changes = 0

    for turn in root.findall('.//Turn'):
        updated = False
        if 'mode' not in turn.attrib:
            turn.set('mode', 'spontaneous')
            print(f"Adding MODE 'spontaneous' to Turn: {turn.attrib}")
            updated = True
        if 'channel' not in turn.attrib:
            turn.set('channel', 'studio')
            print(f"Adding CHANNEL 'studio' to Turn: {turn.attrib}")
            updated = True
        if updated:
            changes += 1



    new_file = get_name(xml_path)
    print(f"The new file will be saved at {new_file}")
    tree.write(new_file, encoding='utf-8', xml_declaration=True)
    print(f"Total Turns updated: {changes}")


    # Scan for DOCTYPE in original file and reinsert it into the output
    # Solving the limits of the XML library
    doctype_line = get_doctype_line(xml_path)
    if doctype_line:
        insert_doctype(new_file, doctype_line)
    else:
        print("No DOCTYPE found in the input file.")




def main():
    args = argument_parsers()
    change_mode_channel(args.xml_path)

if __name__ == '__main__':
    main()
