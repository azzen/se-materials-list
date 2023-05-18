import os
import argparse
import re
from sys import platform
import shutil

VMT_TEXTURES_PARAMS = ["basetexture", "bumpmap", "lightwarptexture", "basetexture2", "detail"]

parser = argparse.ArgumentParser(description='List materials used by SMD files.')
parser.add_argument('directory', metavar='dir', type=str, default='.', help='Directory to search for SMD files')
parser.add_argument('qc', type=str, help='Path to the QC file of the model')
parser.add_argument('materials', type=str, help='Path to the materials folder of the model')
parser.add_argument('--output', '-o', type=str, default='materials.txt', help='Output file')
parser.add_argument('--verbose', '-v', type=bool, default=False, help='Verbose mode')
parser.add_argument('--build-dir', '-b', type=str, help='Build the directory from found materials to the specified directory')

def build_dir(base_path: str, build_dir: str, files: list[str]):
    print("[+] Building directory '{}'".format(build_dir))
    # strip the base path from the files
    build_dir = os.path.join(build_dir, 'materials')
    dirs = [f.replace(base_path, '') for f in files]
    # remove the first slash
    dirs = [f[1:] if (f[0] == '/' or f[0] == '\\') else f for f in dirs]
    # remove the file 
    dirs = [os.path.dirname(f) for f in dirs]
    dirs = set(dirs)
    # build directories
    for d in dirs:
        path = os.path.join(build_dir, d)
        if not os.path.isdir(path):
            os.makedirs(path)
    # Copy files 
    for f in files:
        dst = f.replace(base_path, '')
        dst = dst[1:] if (dst[0] == '/' or dst[0] == '\\') else dst
        dst = os.path.join(build_dir, dst)

        print(f" - Copying \x1b[32m{f}\x1b[0m to \x1b[32m{dst}\x1b[0m")
        shutil.copy(f, dst)

def get_vmt(smd_files: list[str]) -> set[str]:
    files = set()
    for smd_file in smd_files:
        buffer = open(smd_file, 'r').read()
        if not 'triangles' in buffer:
            continue
        buffer = buffer.split('triangles')[1]
        for line in buffer.split('\n'):
            if len(line) > 0 and line[0].isalpha() and line != 'end':
                files.add(line)
    return files


def read_vmts(base_path, files: list[str]) -> set[str]:
    output = []
    for file in files:
        buffer = open(file, 'r').read()
        print(file)
        for param in VMT_TEXTURES_PARAMS:
            regex = re.compile(r"^\s*[\"']?\$%s[\"']? .*?[\"'](.*?)[\"']$\n" % param, re.MULTILINE)
            output.extend(os.path.join(base_path, (cg if platform != 'win32' else cg.replace('/', '\\')) + '.vtf') for cg in regex.findall(buffer))
    return set(output)

def get_existings_files(paths_to_search: list[str], filenames: list[str], extension: str, verbose=False) -> list[str]:
    max_len = max([len(filename) for filename in filenames])

    output = []
    for f in filenames:
        for i, path in enumerate(paths_to_search):
            path = os.path.join(path, f + extension)
            # We consider the first file found as the correct one
            if os.path.isfile(path):
                output.append(path)
                if verbose: print(f" - \x1b[32m{path}\x1b[0m")
                break 
            elif i == len(paths_to_search) - 1:
                print(f" - \x1b[31m{f: <{max_len}}\t[File Not Found]\x1b[0m")
    return output

if __name__ == "__main__":
    args = parser.parse_args()

    directory = args.directory
    qc_path = args.qc
    materials_path = args.materials
    output_path = args.output
    
    if not os.path.isdir(directory):
        print("[-] Error: directory '{}' does not exist.".format(directory))
        exit(1)
    
    if not os.path.isdir(materials_path):
        print("[-] Error: materials folder '{}' does not exist.".format(materials_path))
        exit(1)

    if not os.path.isfile(qc_path):
        print("[-] Error: QC file '{}' does not exist.".format(qc_path))
        exit(1)
    
    regex = re.compile(r"^\$cdmaterials \"(.*?)\"$\n", re.MULTILINE)
    qc_buffer = open(qc_path, 'r').read()
    cd_materials = [os.path.join(materials_path, cg) for cg in regex.findall(qc_buffer)]

    for mat in cd_materials:
        print("[+] Material directories '{}'".format(mat))

    smd_files = []
    for root, dirs, files in os.walk(directory):
        for files in files:
            if files.endswith(".smd"):
                smd_files.append(os.path.join(root, files))
    
    print("[+] Found {} SMDs".format(len(smd_files)))

    vmts = get_vmt(smd_files)
    vmts = get_existings_files(cd_materials, vmts, ".vmt", verbose=args.verbose)
    print("[+] Found {} VMTs".format(len(vmts))) 

    # Now we have to search all the VTF files used by the VMT files

    vtfs = read_vmts(materials_path, vmts)    
    print("[+] Found {} VTFs".format(len(vtfs))) 

    print("[+] Writing files to '{}'".format(output_path))
    with open(output_path, 'w') as f:
        f.write('\n'.join(list(vmts) + list(vtfs)))
        f.close()

    if args.build_dir is not None:
        build_dir(materials_path, args.build_dir, list(vmts) + list(vtfs))
