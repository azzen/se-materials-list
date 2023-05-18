# Source Engine Models materials list

Small tool to list materials (both vmts and vtfs) used by a source engine model (.mdl).

- It enables you to build the corresponding file structure containing all the materials used to a specified directory.

- It use SMD and QC files, therefore you must decompile the MDL file of your model before using it.

Requirements: 
  - Python (>=3.11)
  - A source engine models decompiler (I recommend to use the excellent tool [Crowbar](https://github.com/ZeqMacaw/Crowbar))


```
usage: main.py [-h] [--output OUTPUT] [--verbose VERBOSE] [--build-dir BUILD_DIR] dir qc materials

List materials used by SMD files.

positional arguments:
  dir                   Directory to search for SMD files
  qc                    Path to the QC file of the model
  materials             Path to the materials folder of the model

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file
  --verbose VERBOSE, -v VERBOSE
                        Verbose mode
  --build-dir BUILD_DIR, -b BUILD_DIR
                        Build the directory from found materials to the specified directory
```

