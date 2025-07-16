
import os
import re
import datetime

def merge_text_files(directory, output_filename="merged_backup.txt"):
    text_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt") and file != output_filename:
                text_files.append(os.path.join(root, file))

    # Sort files by date in filename if possible, otherwise by last modified time
    def get_file_sort_key(filepath):
        filename = os.path.basename(filepath)
        match = re.search(r'backup(\d{8}).txt', filename)
        if match:
            return match.group(1) # YYYYMMDD string
        else:
            # Use modification time as a fallback, formatted as a string for consistent comparison
            mod_time = os.path.getmtime(filepath)
            return datetime.datetime.fromtimestamp(mod_time).strftime('%Y%m%d%H%M%S')

    text_files.sort(key=get_file_sort_key)

    output_filepath = os.path.join(directory, output_filename)
    with open(output_filepath, "w", encoding="utf-8") as outfile:
        for filepath in text_files:
            try:
                with open(filepath, "r", encoding="utf-8") as infile:
                    outfile.write(f"\n\n--- Content from {os.path.basename(filepath)} ---\n\n")
                    outfile.write(infile.read())
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"All text files merged into {output_filepath}")

if __name__ == "__main__":
    target_directory = "/home/ubuntu/manus-memoryroom"
    merge_text_files(target_directory)


