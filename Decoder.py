import argparse
from Huffman import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decode .hc files.')
    parser.add_argument('filename', action='store', help="name of the file to decode, excluding the '.hc' extension")
    args = parser.parse_args()
    file_name = args.filename
    try:
        decode(file_name)
        check_success(file_name)
        get_ratio(file_name)
    except FileNotFoundError:
        print("File " + file_name + ".hc not found.")
