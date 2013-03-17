#!/usr/bin/python
import os
import sys
from math import *
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], '..'))
from lib.common_utils import verify_file_exists, read_data_file

INFINITY_SUBSTITUTE = 2147483647


def pmf(k, mean):
    return pow(mean, k) * exp(-mean) / factorial(k)


def cdf(k, mean):
    acc = 0
    for i in range(0, k + 1):
        acc += pmf(i, mean)
    return acc


def lower_quantile_cd(prob, mean, max_elem):
    i = 0
    if pmf(0, mean) > prob:
        return 0
    else:
        while pmf(i, mean) <= prob and i <= max_elem:
            i += 1
        return cdf(max(0, i - 1), mean)


def upper_quantile_cd(prob, mean, max_elem):
    i = int(max_elem)
    while pmf(i, mean) > prob:
        i += 1
    res = 1 - cdf(i, mean)
    if res < 0:  # precision errors
        return 0
    else:
        return res


def log_principal_anomaly(k, mean, max_elem):
    prob = pmf(k, mean)
    lower_q = lower_quantile_cd(prob, mean, max_elem)
    upper_q = upper_quantile_cd(prob, mean, max_elem)
    accum_quantile = lower_q + upper_q
    if accum_quantile == 0:
        return INFINITY_SUBSTITUTE
    else:
        return -log(accum_quantile)


def max_pois_elem(mean):
    i = 0
    max_val = pmf(0, mean)
    while pmf(i + 1, mean) > max_val:
        max_val = pmf(i, mean)
        i += 1
    return i


def main():
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "<train_data_file> <test_data_file>"
        exit(1)
    train_data_file = sys.argv[1]
    verify_file_exists(train_data_file)
    test_data_file = sys.argv[2]
    verify_file_exists(test_data_file)
    train_data_list = read_data_file(train_data_file, lambda x: int(x))
    mean = float(sum(train_data_list)) / len(train_data_list)
    test_data_list = read_data_file(test_data_file, lambda x: int(x))
    max_elem = max_pois_elem(mean)
    print '\n'.join(map(lambda elem: str(log_principal_anomaly(elem, mean, max_elem)), test_data_list))


if __name__ == '__main__':
    main()
