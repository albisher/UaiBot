# UaiBot File Operations Examples

This document provides examples of using the `-f` flag with UaiBot for various file operations.

## Search Operations

Find files with a specific name:
```
python main.py -f find files with example in the name
python main.py -f search for pdf files in Documents
```

Find CV or resume files:
```
python main.py -f find my cv
python main.py -f where is my resume
```

## Create Operations

Create new files:
```
python main.py -f create a new file called test.txt
python main.py -f make a file named "report.md" in Documents
```

## Read Operations

View file contents:
```
python main.py -f show me the contents of test.txt
python main.py -f read file "~/Documents/report.md"
```

## Delete Operations

Remove files:
```
python main.py -f delete the file test.txt
python main.py -f remove "~/temp/old_data.csv"
```

## List Operations

List directory contents:
```
python main.py -f list files in Documents
python main.py -f show files in "~/Projects"
```

## Additional Operations

Get file information:
```
python main.py -f show info about test.txt
```

Rename files:
```
python main.py -f rename test.txt to new_test.txt
```

Copy files:
```
python main.py -f copy test.txt to backup.txt
```

## Expected Terminal Outputs

Example successful search:
```
Found 3 files matching 'example':
/home/user/Documents/example1.txt
/home/user/Documents/example2.txt
/home/user/Downloads/example3.pdf
```

Example file creation:
```
✅ Created file: /home/user/Documents/test.txt
```

Example file read:
```
📄 Content of /home/user/Documents/test.txt:

This is the content of the test file.
```

Example directory listing:
```
Contents of /home/user/Documents:
📁 Projects/
📁 Images/
📄 report.md
📄 notes.txt
```

Example error message:
```
❌ File not found: /home/user/nonexistent.txt
```
