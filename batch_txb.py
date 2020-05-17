import os
import os.path
from os import path

file_path = "F:\GR2\GravityRush2\\arc\\txb\ep00_EN.txb"
folder = 'F:\GR2\GravityRush2\\arc\\txb\\'
output_folder = 'F:\GR2\\txb_extracted\\'

cast_new_line = True
guess_text_name = True
load_font = True

FNV1A_32_OFFSET = 0x811c9dc5
FNV1A_32_PRIME = 0x01000193

def fnv1a_32_str(string):
    # Set the offset basis
    hash = FNV1A_32_OFFSET

    # For each character
    for character in string:
        # Xor with the current character
        hash ^= ord(character)

        # Multiply by prime
        hash *= FNV1A_32_PRIME

        # Clamp
        hash &= 0xffffffff

    # Return the final hash as a number
    hash = hex(hash)[2:]
    if len(hash) == 7:
        hash = '0' + hash
    hash = hash[6:8]+hash[4:6]+hash[2:4]+hash[0:2]
    return hash

dictionary = {}
dictionary_list = {}

def generate_dictionary(file_name):
    global dictionary
    dictionary = {}
    base_filename = file_name.split("_")[0] + "_"
    if base_filename in  dictionary_list:
        dictionary = dictionary_list[base_filename]
        return
    for i in range(20):
        for t in range(1000):
            string = base_filename + str(i).zfill(2) + str(t).zfill(3)
            print(string)
            dictionary[fnv1a_32_str(string)] = string
    for i in range(600):
        for t in range(1000):
            string = base_filename + "00" + str(i).zfill(3) + "k_" + str(t).zfill(3)
            print(string)
            dictionary[fnv1a_32_str(string)] = string
    for i in range(600):
        for t in range(200):
            string = base_filename + "00" + str(i).zfill(3) + "m_" + str(t*5).zfill(3)
            print(string)
            dictionary[fnv1a_32_str(string)] = string
    for i in range(500):
        for t in range(200):
            string = base_filename + "00" + str(i).zfill(3) + "c_" + str(t*5).zfill(3)
            print(string)
            dictionary[fnv1a_32_str(string)] = string

    print("Dictionary generated")
    dictionary_list[base_filename] = dictionary

def getNameFromHash(nameHash):
    nameHash = hex(nameHash)[2:]
    if len(nameHash) == 7:
        nameHash = '0' + nameHash
    nameHash = nameHash[6:8]+nameHash[4:6]+nameHash[2:4]+nameHash[0:2]
    try:
        return dictionary[nameHash]
    except:
        print("Can't find string of hash %s" % nameHash)
        return nameHash

fonttable = {}
def load_fonttable():
    fonts = []
    file_name = file_path.split("\\")[-1]
    lang = file_name.split('.')[0].split('_')[-1]
    if lang in fonttable:
        return fonttable[lang]
    fonttable_filename = "FontTable2_" + lang + ".bin"
    if path.exists(file_path.replace(file_name, fonttable_filename)) == False:
        fonttable_filename = "FontTable2_Default" + ".bin"
    file = open(file_path.replace(file_name, fonttable_filename), mode='rb')
    data = file.read()
    data_list = data.split(b'\x00')
    #print(len(data_list))
    for data_chunk in data_list:
        fonts.append(data_chunk.split(b'\x2E')[0].decode('UTF8'))
    fonttable[lang] = fonts
    return fonts
    #print(fonts)


files = []

for r, d, f in os.walk(folder):
    for file in f:
        print("Scaning directory: %s" % file)
        if '.txb' in file:
            files.append(os.path.join(r, file))

for file_path in files:
    file = open(file_path, mode='rb')
    data = file.read()
    texts = []
    fonts = []
    if len(data) > 0x40 and data[0:4] == b'txbL':
        file.seek(0x8, 0)
        file_length = int.from_bytes(file.read(4), byteorder='little')
        text_count = int.from_bytes(file.read(4), byteorder='little')
        file_name = file.read(0x18).decode('UTF8')
        if guess_text_name:
            generate_dictionary(file_name)
        if load_font:
            fonts = load_fonttable()
        for i in range(text_count):
            texts.append([getNameFromHash(int.from_bytes(file.read(4), byteorder='little')), None, None, []])
        for i in range(text_count):
            texts[i][1] = int.from_bytes(file.read(4), byteorder='little')
        data_begin = file.tell()
        for i in range(text_count):
            file.seek(data_begin + texts[i][1], 0)
            text_length = int.from_bytes(file.read(2), byteorder='little')
            text_size = int.from_bytes(file.read(2), byteorder='little')
            num_of_font_changes = int.from_bytes(file.read(2), byteorder='little')
            file.seek(0x16, 1)
            texts[i][2] = file.read((text_size//4+1)*4).split(b'\x00')[0].decode('UTF8')
            if cast_new_line:
                texts[i][2] = texts[i][2].replace("\x0a", " \\n ")
            for f in range(num_of_font_changes):
                begin = int.from_bytes(file.read(2), byteorder='little')
                end = int.from_bytes(file.read(2), byteorder='little')
                file.seek(2,1) #Text Size I think, not needed
                font_id = int.from_bytes(file.read(1), byteorder='little')
                file.seek(1,1)
                texts[i][3].append([begin, end, fonts[font_id]])
        texts.sort(key=lambda x:x[0])

        output_filepath = r"%s%s.tsv" % (output_folder, file_path.split(folder)[1].split('.')[0])
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        with open(output_filepath, 'w', encoding='utf-8') as output_file:
                if load_font:
                    output_file.write("Reference Name\tText\tFont\n")
                else:
                    output_file.write("Reference Name\tText\n")

                for text in texts:
                    if load_font:
                        output_file.write("%s\t%s\t" % (text[0], text[2]))
                        output_file.write(str(text[3])[1:-1])
                        output_file.write('\n')
                    else:
                        output_file.write("%s\t%s\n" % (text[0], text[2]))
    else:
        print("File Incorrect")