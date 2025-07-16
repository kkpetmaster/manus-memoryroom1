
import os
import hashlib

def generate_file_hash(filepath, blocksize=65536):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
    return hasher.hexdigest()

def find_duplicate_files(directory):
    hashes = {}
    duplicates = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                file_hash = generate_file_hash(filepath)
                if file_hash in hashes:
                    duplicates.append((filepath, hashes[file_hash]))
                else:
                    hashes[file_hash] = filepath
    return duplicates

if __name__ == "__main__":
    target_directory = "/home/ubuntu/manus-memoryroom"
    duplicate_files = find_duplicate_files(target_directory)

    if duplicate_files:
        print("Duplicate files found:")
        for file1, file2 in duplicate_files:
            print(f"- {file1} and {file2}")
    else:
        print("No duplicate files found.")


