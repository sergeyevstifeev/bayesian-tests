import csv
import os


def verify_file_exists(filename):
    if not os.path.isfile(filename):
        print "File does not exist:", filename
        exit(1)


def read_data_file(filename, convert_fun):
    data_list = []
    with open(filename, 'rb') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        csv_reader.next()  # skip header line
        for line in csv_reader:
            if line:
                data_list.append(convert_fun(line[0]))
    return data_list