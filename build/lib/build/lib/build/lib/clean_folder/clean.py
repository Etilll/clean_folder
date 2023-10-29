import argparse
import sys
import shutil
from pathlib import Path
import re

KNOWN_FORMATS_REF = {'JPEG':'images', 'JPG':'images', 'PNG':'images','SVG':'images', 'AVI':'video', 'MP4':'video', 'MOV':'video', 'MKV':'video', 'DOC':'documents', 'DOCX':'documents', 'TXT':'documents', 'PDF':'documents', 'XLSX':'documents', 'PPTX':'documents', 'MP3':'audio', 'OGG':'audio', 'WAV':'audio', 'AMR':'audio', 'ZIP':'archives', 'GZ':'archives', 'TAR':'archives', 'RAR':'archives', '7Z':'archives'}

FOLDERS = []
ALL_LISTS = {}
KNOWN_SUFFIXES = set()
UNKNOWN_SUFFIXES = set()

def sorter(path: Path):
    for file in path.iterdir():
        if not file.is_dir():
            file_name = file.name
            known = False
            suff = Path(file_name).suffix[1:].upper()
            for check,category in KNOWN_FORMATS_REF.items():
                if suff == check:
                    dir_dict = KNOWN_FORMATS_REF[check] + "_list"
                    if not dir_dict in ALL_LISTS:
                        ALL_LISTS[dir_dict] = {}
                    if not suff in ALL_LISTS[dir_dict]:
                        ALL_LISTS[dir_dict][suff] = []
                    
                    ALL_LISTS[dir_dict][suff].append(path / file_name)
                    known = True

            if known != True:
                KNOWN_FORMATS_REF[suff] = 'unknown'
                if not 'unknown_list' in ALL_LISTS:
                    ALL_LISTS['unknown_list'] = {}

                ALL_LISTS['unknown_list'][suff] = []
                ALL_LISTS['unknown_list'][suff].append(path / file_name)
            
            if KNOWN_FORMATS_REF[suff] != 'unknown':
                KNOWN_SUFFIXES.add(suff)
            else:
                UNKNOWN_SUFFIXES.add(suff)
            
        elif file.is_dir() and (file.name not in ('archives', 'video', 'audio', 'documents', 'images', 'unknown')):
            FOLDERS.append(path / file.name)
            sorter(path / file.name)

    return ALL_LISTS, KNOWN_SUFFIXES, UNKNOWN_SUFFIXES, FOLDERS




def info_printer(RETURN_TUPLE: tuple): # Here you can print any info on scan/parse results, using the dict from sorter()
    CAT_STRING = '\n"'
    for k,v in RETURN_TUPLE[0].items():
        tmp_n = k[0:len(k)-5].capitalize()
        CAT_STRING += tmp_n + '",\n"'
    
    CAT_STRING = CAT_STRING[:len(CAT_STRING)-3]
    print(f'Known_prefixes_found: {RETURN_TUPLE[1]}\nUnknown_prefixes_found: {RETURN_TUPLE[2]}\nItem categories found: {CAT_STRING}')


def real_sorter(path: Path, output: Path):
    RETURN_TUPLE = sorter(path)
    info_printer(RETURN_TUPLE)
    for categories, unnamed in RETURN_TUPLE[0].items():
        output_c = output / str(categories[0:len(categories)-5])
        if not output_c.exists():
            output_c.mkdir(exist_ok=True, parents=True)
        for extension, extlist in unnamed.items():
            output_e = output_c / str(extension)
            if not output_e.exists():
                output_e.mkdir(exist_ok=True, parents=True)
            for dir in extlist:
                file_name = str(dir)
                file_name = file_name[file_name.rfind("\\") + 1:]
                suff = file_name[file_name.rfind("."):]
                file_name = file_name[:len(file_name) - len(file_name[file_name.rfind("."):])]
                if categories != 'archives_list':
                    dir.replace(output_e / normalize(file_name, suff))
                else:
                    tmp_namee = output_e / normalize(file_name)
                    try:
                        shutil.unpack_archive(dir, output_e, suff[1:])
                        dir.unlink()
                    except shutil.ReadError:
                        tmp_namee.rmdir()
    for em_folder in RETURN_TUPLE[3]:
        try:
            em_folder.rmdir()
        except OSError:
            print(f'Error during remove folder {em_folder}')


CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = dict()

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyrillic)] = latin
    TRANS[ord(cyrillic.upper())] = latin.upper()


def normalize(name: str, suff="") -> str:
    translate_name = re.sub(r'\W', '_', name.translate(TRANS))
    translate_name += suff
    return translate_name

def packet_start():
    if sys.argv[1] and sys.argv[2]:
        inut = Path(sys.argv[1])
        output = Path(sys.argv[2])
        real_sorter(Path(inut),Path(output))
    else:
        print('Doesnt work! Not enough/no arguments!\nCorrect usage: arg1=where_from(dir)    arg2=where_to(dir)')

#####USAGE: python main.py --source 'source' --output 'output'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sorting directory')
    parser.add_argument('--source', '-s', required=True, help='Source folder')
    parser.add_argument('--output', '-o', default='destination', help='Output folder')
    args = vars(parser.parse_args())
    inut = args.get('source')
    output = args.get('output')
    real_sorter(Path(inut),Path(output))