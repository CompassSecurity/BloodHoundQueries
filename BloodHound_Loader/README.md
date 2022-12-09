# BloodHound Loader

## Introduction

[BloodHoundLoader.py](BloodHoundLoader.py) is a tool to set the value of an
attribute in BloodHound (e.g. high value, owned...) for all the items contained
in a file.

## Installation

It should be used with Python 3 and with the Neo4j module installed since it is run directly against the Neo4j database:
```bash
pip3 install --upgrade neo4j
```

Set all the computers in the file "high_value.txt" to high value targets:
```bash
python3 BloodHoundLoader.py --dburi bolt://localhost:7687 --dbuser neo4j --dbpassword BloodHound --mode h high_value.txt
```

Set all the computers in the file "owned.txt" to owned principals:
```bash
python3 BloodHoundLoader.py --mode o owned.txt
```

Set all the computers in the file "no_smb_signing.txt" to "hassigning = false", in order to use them with the queries "All Shortest Paths from no Signing to *":
```bash
python3 BloodHoundLoader.py --mode s no_smb_signing.txt
```

The names of users and computers in the text file should correspond to the text shown on the GUI, e.g.:
```
DC.ACME.COM
COMPUTER.ACME.COM
GUEST@ACME.COM
```

Create new AdminTo edges based on the tuples in the file "adminto.txt":
```bash
python3 BloodHoundLoader.py --edge AdminTo adminto.txt
```

The names tuples in the text file must be comma separated and ordered (source,destination):
```
DOMAIN ADMINS@ACME.COM,DC.ACME.COM
SERVER ADMINS@ACME.COM,COMPUTER1.ACME.COM
EDWARD.NIGMA@ACME.COM,RIDDLE.ACME.COM
```

## Full Help

```bash
python3 BloodHoundLoader.py --help
usage: BloodHoundLoader.py [-h] [--dburi DATABASEURI] [--dbuser DATABASEUSER] [--dbpassword DATABASEPASSWORD] (-m {h,o,s} | -o OPERATION) [-c COMMENT] [-v] filePaths [filePaths ...]

BloodHoundLoader, tool to set attributes in BloodHound for all the items contained in files

positional arguments:
  filePaths             Paths of files the to import

optional arguments:
  -h, --help            show this help message and exit
  --dburi DATABASEURI   Database URI (default: bolt://localhost:7687)
  --dbuser DATABASEUSER
                        Database user (default: neo4j)
  --dbpassword DATABASEPASSWORD
                        Database password (default: BloodHound)
  -m {h,o,s}, --mode {h,o,s}
                        Mode, h = set to high value, o = set to owned, s = set to no SMB signing, u = umark as owned (default: None)
  -o OPERATION, --operation OPERATION
                        Operation to perform if the mode is not set, for instance "highvalue = true" (default: None)
  -e EDGE, --edge EDGE
                        Create the provided edge, file must contain exactly 2 nodes per line, comma separated (default: None)
  -c COMMENT, --comment COMMENT
                        Comment for the log (default: )
  -v, --verbose         Verbose mode (default: False)
```
