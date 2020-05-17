file_path = "F:\GR2\GravityRush2\\arc\\txb\ep00_EN.txb"
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

def generate_dictionary(file_name):
    base_filename = file_name.split("_")[0] + "_"
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

fonts = []
def load_fonttable():
    file_name = file_path.split("\\")[-1]
    fonttable_filename = "FontTable2_" + file_name.split('.')[0].split('_')[-1] + ".bin"
    file = open(file_path.replace(file_name, fonttable_filename), mode='rb')
    data = file.read()
    data_list = data.split(b'\x00')
    print(len(data_list))
    for data_chunk in data_list:
        fonts.append(data_chunk.split(b'\x2E')[0].decode('UTF8'))
    print(fonts)

file = open(file_path, mode='rb')
data = file.read()
texts = []

if len(data) > 0x40 and data[0:4] == b'txbL':
    file.seek(0x8, 0)
    file_length = int.from_bytes(file.read(4), byteorder='little')
    text_count = int.from_bytes(file.read(4), byteorder='little')
    file_name = file.read(0x18).decode('UTF8')
    if guess_text_name:
        generate_dictionary(file_name)
    if load_font:
        load_fonttable()
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
        texts[i][2] = file.read((text_size//4+1)*4).decode('UTF8')
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
    if load_font:
        print("Reference Name, Text, Font")
    else:
        print("Reference Name, Text")

    for text in texts:
        if load_font:
            print("%s, %s," % (text[0], text[2]), end="")
            print(text[3])
        else:
            print("%s, %s" % (text[0], text[2]))
else:
    print("File Incorrect")