import os
from collections import Counter
import sys


class Node:
    def __init__(self, freq, key):
        self.frequency = freq
        self.code = key
        self.root = False
        self.child_a = None
        self.child_b = None
        self.binary = ''

    def has_children(self):
        if self.child_a is not None or self.child_b is not None:
            return True
        else:
            return False


def read_text(name):
    filename = name
    file = open(filename, "r")
    read = file.read()
    file.close()
    return read


def count_frequencies(text):
    # Count Frequencies
    count = Counter(text)
    return count


def create_tree(frequencies):
    # Initialise Tree
    tree = {}
    for (key, value) in frequencies.items():
        tree[key] = Node(value, key)
    # Merge leaves to form tree structure
    while len(frequencies) > 2:
        ordered = frequencies.most_common()
        char_a, count_a = ordered[-1]
        char_b, count_b = ordered[-2]
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
    root = Node(a[1] + b[1], a[0] + b[0])
    root.root = True
    root.child_a = tree[a[0]]
    root.child_b = tree[b[0]]
    return root


def attach_binary(tree):
    child_a = tree.child_a
    child_b = tree.child_b
    try:
        child_a.binary = tree.binary + '0'
        attach_binary(child_a)
    except AttributeError:
        pass
    try:
        child_b.binary = tree.binary + '1'
        attach_binary(child_b)
    except AttributeError:
        pass
    return tree


def tree_to_dict(tree, dictionary):
    if not tree.has_children():
        dictionary[tree.code] = tree.binary
        return dictionary
    else:
        if tree.child_a is not None:
            dictionary = tree_to_dict(tree.child_a, dictionary)
        if tree.child_b is not None:
            dictionary = tree_to_dict(tree.child_b, dictionary)
        return dictionary


def search_tree_encode(key, tree):
    if tree.code == key:
        return tree.binary
    elif key in tree.child_a.code:
        return search_tree_encode(key, tree.child_a)
    else:
        return search_tree_encode(key, tree.child_b)


def search_tree_decode(binary, tree):
    print("Decoding binary...")
    output = []
    pointer = 0
    end = len(binary)
    while pointer < end:
        current = tree
        search = binary[pointer]
        if search == '0':
            current = current.child_a
        else:
            current = current.child_b
        while current.has_children():
            search += binary[pointer + len(search)]
            if search[-1] == '0':
                current = current.child_a
            else:
                current = current.child_b
        output.append(current.code)
        pointer += len(search)
    print('100% done')
    return ''.join(output)


def get_tree(text):
    print("Counting frequencies")
    word_frequencies = count_frequencies(text)
    print("Creating binary tree")
    binary_tree = attach_binary(create_tree(word_frequencies))
    return binary_tree


def write_tree(tree):
    string = []
    child_a = tree.child_a
    child_b = tree.child_b
    if child_a.has_children():
        string.append('0')
        string.extend(write_tree(child_a))
    else:
        string.append('1' + child_a.code)
    if child_b.has_children():
        string.append('0')
        string.extend(write_tree(child_b))
    else:
        string.append('1' + child_b.code)
    return string


def encode(name):
    text = read_text('Plaintext/' + name + ".txt")
    binary_tree = get_tree(text)
    dictionary = tree_to_dict(binary_tree, {})
    tree_list = write_tree(binary_tree)
    tree_list.append('1')
    tree = ''.join(tree_list)
    tree = tree.encode()
    print("Encoding text.")
    output = [dictionary[char] for char in text]
    write_binary('Encoded/' + name + ".hc", ''.join(output), tree)
    print(name + " encoded.\n")


def write_text(name, data):
    filename = name
    write = open(filename, "w")
    write.write(data)
    write.close()


def write_binary(name, data, tree_data):
    print("Writing binary to " + name)
    filename = name
    write = open(filename, "wb")
    write.write(tree_data)
    array = [data[i:i + 8] for i in range(0, len(data), 8)]
    to_write = bytearray()
    final_array = bytearray()
    buffer = 0
    final_chunk = array[-1]
    array = array[:-1]
    for chunk in array:
        num = int(chunk, 2)
        to_write.append(num)
    # Handles the last byte having less than 8 bits.
    while len(final_chunk) < 8:
        final_chunk += '0'
        buffer += 1
    final_array.append(buffer)
    num = int(final_chunk, 2)
    to_write.append(num)
    # Writes to file.
    write.write(final_array + to_write)
    write.close()


def reconstruct_tree(bytes_in):
    byte_obj = bytearray(bytes_in)
    tree = Node(None, None)
    for i in range(2):
        flag = chr(byte_obj[0])
        if flag == '0':
            del byte_obj[0]
            if tree.child_a is None:
                tree.child_a, byte_obj = reconstruct_tree(byte_obj)
            else:
                tree.child_b, byte_obj = reconstruct_tree(byte_obj)
        else:
            del byte_obj[0]
            collection = bytearray()
            collection.append(byte_obj[0])
            del byte_obj[0]
            char = chr(byte_obj[0])
            while (char != '0') & (char != '1'):
                collection.append(byte_obj[0])
                del byte_obj[0]
                char = chr(byte_obj[0])
            if len(collection) > 1:
                char = collection.decode()
            else:
                char = chr(collection[0])
            if tree.child_a is None:
                tree.child_a = Node(None, char)
            else:
                tree.child_b = Node(None, char)
    return tree, byte_obj


def read_binary(name):
    print("Reading binary from " + name)
    file = open(name, "rb")
    read = file.read()
    file.close()
    string = []
    tree, read = reconstruct_tree(read)
    tree = attach_binary(tree)
    read = read[1:]
    buffer = read[0]
    read = read[1:]
    length = len(read)
    for i in range(length):
        raw = read[i]
        binary = bin(raw)[2:]
        while len(binary) < 8:
            binary = '0' + binary
        if i >= length - 1:
            binary = binary[:-buffer]
        string.append(binary)
    return tree, ''.join(string)


def decode(name):
    binary_tree, string = read_binary('Encoded/' + name + ".hc")
    write_text('Decoded/' + name + ".txt", search_tree_decode(string, binary_tree))
    print(name + " decoded.\n")


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
        print("File encoded/decoded successfully.\n---------------------------------- ")
    else:
        print("Encoding/decoding failure.")


if __name__ == '__main__':
    try:
        file_name = sys.argv[1]
        encode(file_name)
        decode(file_name)
        # check(file_name)
        # get_ratio(file_name)
    except IndexError:
        # print("Error: No filename provided.")
        # print("usage: Huffman.py filename")
        file_name = "Sherlock Holmes"
        encode(file_name)
        decode(file_name)
        check(file_name)
        get_ratio(file_name)
