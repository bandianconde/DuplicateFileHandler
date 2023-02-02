# write your code here
import argparse
import os
from collections import defaultdict
from hashlib import md5


def get_sorting_option():
    print("""Size sorting options:
    1. Descending
    2. Ascending""")
    print()
    while True:
        print('Enter a sorting option:')
        sorting_option = input()
        if sorting_option not in ('1', '2'):
            print()
            print('Wrong option')
            print()
        else:
            sorting_option = int(sorting_option)
            return sorting_option


class DirectoryNotFound(Exception):
    pass


def get_filenames_by_size(directory):
    mapping_size_to_file = defaultdict(list)
    if directory is None:
        raise DirectoryNotFound()
    print("Enter file format:")
    file_format = input()
    sorting_option = get_sorting_option()
    filenames = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            filename = os.path.join(root, name)
            if file_format != '' and os.path.splitext(filename)[-1] == f".{file_format}" or file_format == '':
                file_size = os.path.getsize(os.path.abspath(filename))
                filenames.append(filename)
                mapping_size_to_file[file_size].append(filename)

    sizes = list(mapping_size_to_file.keys())
    if sorting_option == 2:
        sizes.sort()
    else:
        sizes.sort(reverse=True)
    for size in sizes:
        print(f'{size} bytes')
        print()
        for filename in mapping_size_to_file[size]:
            print(filename)
    return mapping_size_to_file, sizes


def get_check_duplicates_input():
    while True:
        print("Check for duplicates? ")
        check_for_duplicates = input()
        if check_for_duplicates not in ('yes', 'no'):
            print('Wrong option')
        else:
            break
    return check_for_duplicates


def get_delete_files_input():
    while True:
        print("Delete files? ")
        delete_file_input = input()
        if delete_file_input not in ('yes', 'no'):
            print('Wrong option')
        else:
            break
    return delete_file_input


def file_hash(filename):
    with open(filename, 'r') as file:
        text = file.read()
        return md5(text.encode(encoding='utf-8')).hexdigest()


def group_by_hash(mapping_size_to_file, sizes):
    counter = 0
    mapping_index_to_file = {}
    for size in sizes:
        print(f'{size} bytes')
        mapping_hash_to_file = defaultdict(list)
        filenames_of_given_size = mapping_size_to_file[size]
        for filename in filenames_of_given_size:
            mapping_hash_to_file[file_hash(filename)].append(filename)

        for hash, filename_by_hash in mapping_hash_to_file.items():
            duplicates = len(filename_by_hash)
            if duplicates > 1:
                print(f'Hash: {hash}')
                for filename in filename_by_hash:
                    counter += 1
                    mapping_index_to_file[counter] = filename
                    print(f'{counter}. {filename}')
                print()
    return mapping_index_to_file


def get_file_number_to_delete(mapping_index_to_file):
    duplicates_counter = len(mapping_index_to_file)
    while True:
        print("Enter file numbers to delete:")
        file_numbers_to_delete = input()
        if not file_numbers_to_delete.strip():
            print('Wrong format')
        else:
            try:
                file_numbers_to_delete = list(map(int, file_numbers_to_delete.split()))
            except (TypeError, ValueError):
                print("Wrong format")
                print()
            else:
                wrong_list_format = any(x > duplicates_counter for x in file_numbers_to_delete)
                if not wrong_list_format and len(file_numbers_to_delete) <= 5:
                    return file_numbers_to_delete
                print('Wrong format')
                print()


def delete_files(mapping_index_to_file, file_numbers_to_delete):
    removed_space = 0
    for counter in file_numbers_to_delete:
        filename = mapping_index_to_file[counter]
        removed_space += os.path.getsize(os.path.abspath(filename))
        os.remove(mapping_index_to_file[counter])
    return removed_space


def main(directory):
    try:
        mapping_size_to_file, sizes = get_filenames_by_size(directory)
        get_check_duplicates_input()
        mapping_index_to_file = group_by_hash(mapping_size_to_file, sizes)
        delete_file_choice = get_delete_files_input()
        if delete_file_choice == 'yes':
            file_numbers_to_delete = get_file_number_to_delete(mapping_index_to_file)
            removed_space = delete_files(mapping_index_to_file, file_numbers_to_delete)
            print()
            print(f'Total freed up space: {removed_space} bytes')

    except DirectoryNotFound:
        print("Directory is not specified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', nargs='?')
    args = parser.parse_args()
    directory = args.directory
    main(directory)
