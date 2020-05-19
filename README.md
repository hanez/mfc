# MFC - MiFare classic Converter

A converter for various file formats used to store MIFARE dumps and related data.

	usage: mfc.py [-h] [-s] [-f] {mfd,mct} {mfd,mct,c,keys} input_path output_path

	MFC - MiFare classic Converter

	positional arguments:
	  {mfd,mct}         input format
	  {mfd,mct,c,keys}  output format
	  input_path
	  output_path

	optional arguments:
	  -h, --help        show this help message and exit
	  -s, --strict      Fail on missing data (otherwise filled with zeros)
	  -f, --fuzzy       Accept file sizes >= 1024 for mfd format

## Formats descriptions:

| Name | Description |
| ---- | ----------- |
| mfd | [libnfc](https://github.com/nfc-tools/libnfc) utils (binary) |
| mct | [Mifare Classic Tools](https://github.com/ikarus23/MifareClassicTool) |
| c | C (programming language) matrix (legacy for [Scribe](https://github.com/hexwell/scribe)) |
| keys | unique keys in plain text, one for each line |
