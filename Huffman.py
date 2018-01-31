import os
import struct
from collections import Counter


class Node:
    def __init__(self, freq, key):
        self.frequency = freq
        self.code = key
        self.root = False
        self.child_a = None
        self.child_b = None
        self.binary = ''
        self.depth = None

    def has_children(self):
        if self.child_a is not None or self.child_b is not None:
            return True
        else:
            return False


def read_text(name):
    print("Reading text from " + name)
    filename = name
    file = open(filename, "r")
    read = file.read()
    file.close()
    return read


def count_frequencies(text):
    # Count Frequencies
    count = Counter()
    total = 0
    for char in text:
        count[char] += 1
        total += 1
    return count


def create_tree(frequencies):
    # Initialise Tree
    tree = Counter()
    for key in frequencies.elements():
        tree[key] = Node(frequencies[key], key)
    # Merge leaves to form tree structure
    while len(frequencies) > 2:
        a = frequencies.most_common()[-1]
        b = frequencies.most_common()[-2]
        char_a = a[0]
        count_a = a[1]
        char_b = b[0]
        count_b = b[1]
        del frequencies[char_a], frequencies[char_b]
        merged = char_a + char_b
        merged_sum = count_a + count_b
        frequencies[merged] = merged_sum
        node = Node(merged_sum, merged)
        node.child_a = tree[char_a]
        node.child_b = tree[char_b]
        del tree[char_a], tree[char_b]
        tree[merged] = node
    a = frequencies.most_common()[-1]
    b = frequencies.most_common()[-2]
    merged = a[0] + b[0]
    merged_sum = a[1] + b[1]
    root = Node(merged_sum, merged)
    root.root = True
    root.child_a = tree[a[0]]
    root.child_b = tree[b[0]]
    return root


def attach_binary(tree):
    child_a = tree.child_a
    child_b = tree.child_b
    if child_a is not None:
        child_a.binary = tree.binary + '0'
        attach_binary(child_a)
    if child_b is not None:
        child_b.binary = tree.binary + '1'
        attach_binary(child_b)
    return tree


def search_tree_encode(key, tree):
    if tree.code == key:
        return tree.binary
    elif key in tree.child_a.code:
        return search_tree_encode(key, tree.child_a)
    else:
        return search_tree_encode(key, tree.child_b)


def search_tree_decode(binary, tree):
    print("Decoding binary")
    output = ''
    total = len(binary)
    x = 1
    percent = x
    x_percent = len(binary) * x / 100
    progress = int(total - x_percent)
    while len(binary) > 0:
        if len(binary) < progress:
            progress = int(progress - x_percent)
            print(str(percent) + '% done')
            percent += x
        current = tree
        search = binary[0]
        if search == '0':
            current = current.child_a
        else:
            current = current.child_b
        while current.has_children():
            try:
                search += binary[len(search)]  # TODO: This is throwing exceptions at the end of the larger files.
            except IndexError:
                print("oh no")
            if search[-1] == '0':
                current = current.child_a
            else:
                current = current.child_b
        output += current.code
        binary = binary[len(search):]
    print('100% done')
    return output


def get_tree(name):
    print("Generating binary tree")
    text = read_text('Plaintext/' + name + ".txt")
    word_frequencies = count_frequencies(text)
    binary_tree = attach_binary(create_tree(word_frequencies))
    return binary_tree


def encode(name):
    binary_tree = get_tree(name)
    output = ''
    text = read_text('Plaintext/' + name + ".txt")
    for char in text:
        output += search_tree_encode(char, binary_tree)
    write_binary('Encoded/' + name + ".hc", output)
    print("Encoded " + name)


def write_text(name, data):
    print("Writing text to " + name)
    filename = name
    write = open(filename, "w")
    write.write(data)
    write.close()


def write_binary(name, data):
    print("Writing binary to " + name)
    filename = name
    write = open(filename, "wb")
    array = []
    count = 0
    block_size = 31
    for number in data:
        index = int(count/block_size)
        try:
            x = array[index]
            array[index] = x + number
        except IndexError:
            array.append(number)
        count += 1
    to_write = ''
    for chunk in array:
        num = int(chunk, 2)
        byte = struct.pack('i', num)
        to_write += str(byte)[2:-1]
        write.write(byte)
    write.close()


def read_binary(name):
    print("Reading binary from " + name)
    file = open(name, "rb")
    read = file.read()
    file.close()
    string = ''
    length = len(read)
    for i in range(length):
        modulo = i % 4
        if modulo == 0:
            four = bytes(read[i:(i+4)])
            something = struct.unpack('i', four)[0]
            binary = str(bin(something))[2:]
            if i < length - 4 or binary == '0':
                while len(binary) < 31:
                    binary = '0' + binary
            string += binary
    return string


def decode(name):
    binary_tree = get_tree(name)
    string = read_binary('Encoded/' + name + ".hc")
    write_text('Decoded/' + name + ".txt", search_tree_decode(string, binary_tree))
    print("Decoded " + name)


def get_ratio(name):
    text = os.path.getsize("Plaintext/" + name + ".txt")
    print("Original size: " + str(text))
    code = os.path.getsize("Encoded/" + name + ".hc")
    print("Encoded size: " + str(code))
    print("Ratio: " + str(code/text))


def check(name):
    text = read_text('Plaintext/' + name + ".txt")
    code = read_text('Decoded/' + name + ".txt")
    if text == code:
        print("File encoded/decoded successfully.")
    else:
        print("Encoding/decoding failure.")

if __name__ == '__main__':
    file_name = "Huffman coding - Wikipedia"
    encode(file_name)
    decode(file_name)
    check(file_name)
    get_ratio(file_name)
