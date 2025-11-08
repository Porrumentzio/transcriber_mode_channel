# Transcriber Mode-Channel postedition
This scripts adds the missing mode and channel tags to each turn in a Transcriber .trs file, following the pattern specified in data/speaker-mapping.csv. This way, you can just add the exceptional values to these keys when using Transcriber, and this script will fill out what's missing.

## Prerequisites
- Install Python
- Install module 'pandas' (`pip install pandas`)
- Download the code (Main page > Code > Download ZIP)

## How to use
1. Enter the TRS file into the _data_ directory.
2. Edit the CSV in _data_ so each speaker ID (spk2, spk3) is in their desired column¹
3. Execute main.py:

>Windows:
>`python main.py -p data\NAME_OF_THE_TRS_FILE.trs -c data\speaker-mapping.csv`
>then `Enter`
>
>Linux (probably Mac too):
>`python main.py -p data/NAME_OF_THE_TRS_FILE.trs -c data/speaker-mapping.csv`
>then `Enter`

¹ The speaker IDs are assigned to each speaker starting at the sixth line of the .trs.
