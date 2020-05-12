# MFC - MiFare classic Converter

A converter for various file format used to store MIFARE dumps and related data.

	usage: mfc.py [-h] [-s] {mfd,mct} {mfd,mct,c,keys} input_path output_path

	MFC - MiFare classic Converter

	positional arguments:
	  {mfd,mct}         input format
	  {mfd,mct,c,keys}  output format
	  input_path
	  output_path

	optional arguments:
	  -h, --help        show this help message and exit
	  -s, --strict      Fail on missing data (otherwise filled with zeros)

## Formats descriptions:

| Name | Description |
| ---- | ----------- |
| mfd | libnfc tool (binary) |
| mct | [Mifare Classic Tools](https://github.com/ikarus23/MifareClassicTool) |
| c | C (programming language) matrix |
| keys | unique keys in plain text, one for each line |
