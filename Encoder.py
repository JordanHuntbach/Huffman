import argparse
from Huffman import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compress .txt files using Huffman encoding.')
    parser.add_argument('--quick', action='store_true', help='encode more quickly, possibly at cost of file size')
    parser.add_argument('filename', action='store', help="name of the file to encode, excluding the '.txt' extension")
    args = parser.parse_args()
    file_name = args.filename
    quick = args.quick
    try:
        default = 1
        if not quick:
            default = best_blocks(file_name)
        encode(file_name, default)
    except FileNotFoundError:
        print("File " + file_name + ".txt not found.")
