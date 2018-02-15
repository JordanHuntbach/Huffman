import os
from collections import Counter
from heapq import heapify, heappop, heappush


# Defines the node class, including a comparison to allow heap sorting, a has_children method to define leaves, and
#  other attributes.
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

    def __gt__(self, node2):
        return self.frequency > node2.frequency


# Reads plaintext from a file.
def read_text(name):
    filename = name
    file = open(filename, "r")
    read = file.read()
    file.close()
    return read


# Creates a tree from the word frequencies given.
def create_tree(frequencies):

    # Create a node for each word, and then convert the list of nodes to a heap.
    tree = [Node(value, key) for (key, value) in frequencies.items()]
    heapify(tree)

    # Iteratively merge the two least frequent nodes, to form the tree structure
    while len(tree) > 1:
        child_a = heappop(tree)
        child_b = heappop(tree)
        merged = Node(child_a.frequency + child_b.frequency, child_a.code + child_b.code)
        merged.child_a = child_a
        merged.child_b = child_b
        heappush(tree, merged)
    root = tree[0]
    root.root = True
    return root


# Recursively propagate through a given tree, attaching a binary value to each node.
def attach_binary(tree):
    # The exceptions are in place for when the current node doesn't have children. For large trees - when time is more
    #  of a concern - this is quicker than checking this scenario with an 'if' clause.

    # For the left child, the binary value is the current node's value + '0'.
    child_a = tree.child_a
    try:
        child_a.binary = tree.binary + '0'
        attach_binary(child_a)
    except AttributeError:
        pass

    # For the right child, the binary value is the current node's value + '1'.
    child_b = tree.child_b
    try:
        child_b.binary = tree.binary + '1'
        attach_binary(child_b)
    except AttributeError:
        pass

    return tree


# Breaks the given text up into chunks of n characters, returning a list of 'chunks' and the number of characters
#  required (buffer) to fill the last one.
def chunk_string(text, n):
    output = []
    buffer = 0
    for index in range(0, len(text)):
        if index % n == 0:
            chunk = text[index: index + n]

            # This while loop adds the buffer characters to the final chunk, in the case where n does not divide the
            #  length of the text.
            while len(chunk) < n:
                chunk += 'X'
                buffer += 1

            output.append(chunk)
    return output, buffer


# Creates a binary tree from a given file. The characters parameter specifies how many characters to encode per binary
#  string.
def get_tree(text, n):
    # Break the text up into chunks of n characters, and count each 'chunk's frequency.
    print("Counting frequencies.")
    word_frequencies = Counter(chunk_string(text, n)[0])

    # Create the binary tree from the frequencies.
    print("Creating binary tree.")
    binary_tree = attach_binary(create_tree(word_frequencies))
    return binary_tree


# Converts a binary tree to a dictionary, for character lookup.
def tree_to_dict_code(tree, dictionary):
    if not tree.has_children():
        dictionary[tree.code] = tree.binary
        return dictionary
    else:
        if tree.child_a is not None:
            dictionary = tree_to_dict_code(tree.child_a, dictionary)
        if tree.child_b is not None:
            dictionary = tree_to_dict_code(tree.child_b, dictionary)
        return dictionary


# Converts a binary tree to a dictionary, for binary lookup.
def tree_to_dict_bin(tree, dictionary):
    if not tree.has_children():
        dictionary[tree.binary] = tree.code
        return dictionary
    else:
        if tree.child_a is not None:
            dictionary = tree_to_dict_bin(tree.child_a, dictionary)
        if tree.child_b is not None:
            dictionary = tree_to_dict_bin(tree.child_b, dictionary)
        return dictionary


# Takes a tree and some text to encode, returning the binary.
def search_tree_encode(key, tree):
    if tree.code == key:
        return tree.binary
    elif key in tree.child_a.code:
        return search_tree_encode(key, tree.child_a)
    else:
        return search_tree_encode(key, tree.child_b)


# Takes a tree and some binary text, and returns the decoded plaintext.
def search_tree_decode(binary, tree):
    print("Decoding binary...")

    # Convert the tree to a dictionary, for quicker decoding.
    dictionary = tree_to_dict_bin(tree, {})

    output = []
    string = ''
    for i in range(0, len(binary)):
        # Add another 0/1 to the lookup string.
        string += binary[i]

        # If the dictionary doesn't contain the string, another 0/1 is added. If it does, the character that the binary
        #  maps to is added to the output array and the lookup string is reset.
        try:
            char = dictionary[string]
            output.append(char)
            string = ''
        except KeyError:
            pass
    return ''.join(output)


# Returns the encoded representation of the binary tree.
def write_tree(tree):
    # For each node, a 0 represents that its child is not a leaf, in which case the child node's encoding is added to
    #  the string. A 1 represents that its child is a leaf, in which case the child's character is added to the string.

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


# Encodes a .txt file, writing the result to a .hc file.
def encode(name, characters):
    # Extract the text from the file.
    text = read_text(name + ".txt")

    # Create a binary tree from the text, with 'characters' as the number of characters to encode per leaf.
    binary_tree = get_tree(text, characters)

    # Convert the tree to a dictionary, for quicker encoding.
    dictionary = tree_to_dict_code(binary_tree, {})

    # Get the encoded representation of the tree.
    tree_list = write_tree(binary_tree)

    # Prepend the number of characters per encoding to the beginning of the string as a flag.
    tree_list.insert(0, str(characters))

    # Break the text into chunks.
    print("Encoding text.")
    chunks, buffer = chunk_string(text, characters)

    # Prepend the number of buffer characters to the beginning of the string as a flag.
    tree_list.insert(0, str(buffer))

    # Encode each chunk into a binary string.
    output = [dictionary[chunk] for chunk in chunks]

    # Convert the flags and tree encoding to a single string, and encode it.
    tree = ''.join(tree_list)
    tree = tree.encode()

    # Write the result to a file
    write_binary(name + ".hc", ''.join(output), tree)
    print(name + " encoded.\n")


# Writes plain text to a file.
def write_text(name, data):
    print("Writing text to " + name)
    filename = name
    write = open(filename, "w")
    write.write(data)
    write.close()


# Writes the .hc file, including both the encoded tree and text.
def write_binary(name, data, tree_data):
    print("Writing binary to " + name)
    filename = name
    write = open(filename, "wb")

    # Write the flags and encoded tree to the file.
    write.write(tree_data)

    # Break the binary string up into bytes.
    array = [data[i:i + 8] for i in range(0, len(data), 8)]

    to_write = bytearray()

    # Handles the last byte having less than 8 bits.
    final_byte = array[-1]
    buffer_flag = bytearray()
    # Pads out the byte, and counts how many bits were added.
    buffer = 0
    while len(final_byte) < 8:
        final_byte += '0'
        buffer += 1
    # Sets the buffer flag to the correct value.
    buffer_flag.append(buffer)

    # Trims the array down, removing the final byte which has now been handled.
    array = array[:-1]
    # Converts each binary byte to an int, and adds that to the byte array.
    for chunk in array:
        num = int(chunk, 2)
        to_write.append(num)

    # Adds the final byte to the array.
    num = int(final_byte, 2)
    to_write.append(num)

    # Writes the buffer flag and the byte array to the file.
    write.write(buffer_flag + to_write)
    write.close()


# Used in reconstruct_tree - this function decodes UTF and returns a single character, as well as the modified bytes.
def retrieve_character(bytes_in):
    collection = bytearray()
    num = bytes_in[0]

    # If the byte value is less than 128, it represents a single character.
    if num < 128:
        collection.append(bytes_in[0])
        del bytes_in[0]
    else:
        # If the byte value is greater than 239, the character is composed of 4 bytes.
        if num >= 240:
            count = 4

        # Else, if the byte value is greater than 223, the character is composed of 3 bytes.
        elif num >= 224:
            count = 3

        # Otherwise, the character is composed of 2 bytes.
        else:
            count = 2

        # Add all of the character's bytes to a single byte array, and return it.
        while count > 0:
            collection.append(bytes_in[0])
            del bytes_in[0]
            count -= 1

    return collection, bytes_in


# Reconstructs the binary tree from the encoded file.
def reconstruct_tree(bytes_in, characters):
    byte_obj = bytearray(bytes_in)

    # Establishes the number of characters to look for, per leaf (initially gets this from the flag, then passes is to
    #  all recursive calls.
    if characters is None:
        characters = int(chr(byte_obj[0]))
        del byte_obj[0]

    # Initialise a new node.
    tree = Node(None, None)

    # For each child...
    for i in range(2):
        flag = chr(byte_obj[0])
        del byte_obj[0]

        # If the 'flag' is a 0, the child is not a leaf - recurse to it.
        if flag == '0':
            if tree.child_a is None:
                tree.child_a, byte_obj = reconstruct_tree(byte_obj, characters)
            else:
                tree.child_b, byte_obj = reconstruct_tree(byte_obj, characters)

        # If the 'flag' is a 1, the child is a leaf.
        elif flag == '1':
            collection = bytearray()
            # Build up the character(s) from the bytes encoded, and decode it (them).
            for j in range(0, characters):
                char, byte_obj = retrieve_character(byte_obj)
                collection.extend(char)
            char = collection.decode()

            # Attach the character(s) to a child node.
            if tree.child_a is None:
                tree.child_a = Node(None, char)
            else:
                tree.child_b = Node(None, char)
        else:
            print('Error reconstructing the encoded tree.')
    return tree, byte_obj


# Reads a .hc file, returning the reconstructed tree, the text to decode and a buffer.
def read_binary(name):
    print("Reading binary from " + name)
    file = open(name, "rb")
    read = file.read()
    file.close()

    # This is the flag that indicates how many characters were added to the input plaintext so that each chunk was the
    #  same size.
    character_buffer = int(chr(read[0]))
    read = read[1:]

    # Reconstructs the tree, returning the result and the remaining binary.
    tree, read = reconstruct_tree(read, None)
    tree = attach_binary(tree)

    # This is the flag that indicates how many characters were added to the final byte (and should be removed).
    binary_buffer = read[0]
    read = read[1:]

    # Break the bytes up into 8 bit binary strings.
    length = len(read)
    string = ['{0:08b}'.format(read[i]) for i in range(length-1)]

    # Extract the final byte, removing any padding.
    binary = '{0:08b}'.format(read[-1])
    if binary_buffer != 0:
        binary = binary[:-binary_buffer]
    string.append(binary)

    return tree, ''.join(string), character_buffer


# Decodes a .hc file, and writes the result.
def decode(name):
    # Read the file, and extract the binary tree, the text to decode, and a flag.
    binary_tree, string, buffer = read_binary(name + ".hc")

    # Decode the file.
    output = search_tree_decode(string, binary_tree)

    # If necessary, remove any padding from the decoded text.
    if buffer != 0:
        output = output[:-buffer]

    # Write the result to a file.
    write_text(name + ".txt", output)
    print(name + " decoded.\n")


# Gets the compression ratio of the encoded file.
def get_ratio(name):
    text = os.path.getsize(name + ".txt")
    print("Original size: " + str(text))
    code = os.path.getsize(name + ".hc")
    print("Encoded size: " + str(code))
    print("Ratio: " + str(code/text) + "\n")


# Returns the optimum block size for file encoding.
def best_blocks(file):
    print("Calculating optimum block size.")
    text = read_text(file + '.txt')

    trees = []
    frequencies = []
    dictionaries = []

    # Initialise a frequency dictionary and code dictionary for each block size.
    blocks = [1, 2, 3, 4]
    for i in blocks:
        frequencies.append(Counter(chunk_string(text, i)[0]))
        tree = attach_binary(create_tree(frequencies[blocks.index(i)]))
        trees.append(tree)
        dictionaries.append(tree_to_dict_code(tree, {}))

    # Find the block size with smallest average word length (frequency * code length, per block)
    # 1829819, 1639805, 1593621, 2402505
    totals = []
    for i in range(len(blocks)):
        total = 0
        dictionary = dictionaries[i]
        frequency = frequencies[i]
        keys = dictionary.keys()
        for key in keys:
            total += len(dictionary[key]) * frequency[key]
        total /= 8
        tree = ''.join(write_tree(trees[i]))
        total += len(tree)
        totals.append(total)

    best = blocks[totals.index(min(totals))]
    print(best)
    return best
