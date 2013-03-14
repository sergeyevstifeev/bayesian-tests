#!/usr/bin/python

import csv
import sys
import os
from math import *


def pmf(k, mean):
    return pow(mean, k) * exp(-mean) / factorial(k)


def cdf(k, mean):
    acc = 0
    for i in range(0, k + 1):
        acc += pmf(i, mean)
    return acc


def lower_quantile_cd(prob, mean, max_elem):
    i = 0
    while pmf(i, mean) <= prob and i <= max_elem:
        i += 1
    return cdf(max(0, i - 1), mean)


def upper_quantile_cd(prob, mean, max_elem):
    i = int(max_elem)
    while pmf(i, mean) > prob:
        i += 1
    return 1 - cdf(i, mean)


def log_principal_anomaly(k, mean, max_elem):
    prob = pmf(k, mean)
    lower_q = lower_quantile_cd(prob, mean, max_elem)
    upper_q = upper_quantile_cd(prob, mean, max_elem)
    return -log(lower_q + upper_q)


def max_pois_elem(mean):
    i = 0
    max_val = pmf(0, mean)
    while pmf(i + 1, mean) > max_val:
        max_val = pmf(i, mean)
        i += 1
    return i

def verify_file_exists(filename):
    if not os.path.isfile(filename):
        print "File does not exist:", filename
        exit(1)


def read_data_file(filename):
    data_list = []
    with open(filename, 'rb') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        csv_reader.next()  # skip header line
        for line in csv_reader:
            if line:
                data_list.append(int(line[0]))
    return data_list


def main():
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "<train_data_file> <test_data_file>"
        exit(1)
    train_data_file = sys.argv[1]
    verify_file_exists(train_data_file)
    test_data_file = sys.argv[2]
    verify_file_exists(test_data_file)
    train_data_list = read_data_file(train_data_file)
    mean = float(sum(train_data_list)) / len(train_data_list)
    test_data_list = read_data_file(test_data_file)
    max_elem = max_pois_elem(mean)
    print '\n'.join(map(lambda elem: str(log_principal_anomaly(elem, mean, max_elem)), test_data_list))
    print


if __name__ == '__main__':
    main()
