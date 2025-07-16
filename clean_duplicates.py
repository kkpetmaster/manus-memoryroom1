
import os

def clean_duplicate_files(directory):
    # List of known duplicate patterns and their original counterparts
    duplicates_map = {
        'chavion (1).com 도메인 연결 및 SSL 적용 가이드라인': 'chavion.com 도메인 연결 및 SSL 적용 가이드라인',
        'index (1).html': 'index.html',
        'App (1).jsx': 'App.jsx',
        'Dockerfile (1)': 'Dockerfile',
        'Dockerfile (2)': 'Dockerfile',
        'main (1).py': 'main.py',
        'AIIN 자연어 처리 및 튜닝 가이드라인 (Manus 유사) (1).md': 'AIIN 자연어 처리 및 튜닝 가이드라인 (Manus 유사).md'
    }

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename in duplicates_map:
                original_filename = duplicates_map[filename]
                original_filepath = os.path.join(dirpath, original_filename)
                duplicate_filepath = os.path.join(dirpath, filename)

                if os.path.exists(original_filepath):
                    print(f"Deleting older duplicate: {duplicate_filepath}")
                    os.remove(duplicate_filepath)
                else:
                    print(f"Original file not found for {duplicate_filepath}, skipping deletion.")

if __name__ == "__main__":
    target_directory = "/home/ubuntu/manus-memoryroom"
    clean_duplicate_files(target_directory)
    print("Duplicate file cleaning process completed.")


