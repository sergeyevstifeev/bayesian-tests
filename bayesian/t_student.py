#!/usr/bin/python
import os
import sys
from math import log
from math import sqrt
from scipy.stats import t
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], '..'))
from lib.common_utils import verify_file_exists, read_data_file


def log_principal_anomaly(x, N, Q, S):
    assert N > 3, "N must be more than 3, is %r" % N
    mean = float(S) / N
    val = mean - abs(mean - x)
    scale = sqrt(max(0, (float(N) * Q - pow(S, 2))) / ((N + 1) * (N - 3)))
    t_cdf = t.cdf(val, N - 1, loc=mean, scale=scale)
    return -log(2 * t_cdf)


def main():
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "<train_data_file> <test_data_file>"
        exit(1)
    train_data_file = sys.argv[1]
    verify_file_exists(train_data_file)
    test_data_file = sys.argv[2]
    verify_file_exists(test_data_file)
    train_data_list = read_data_file(train_data_file, lambda x: float(x))
    N = len(train_data_list)
    Q = reduce(lambda acc, x: acc + pow(x, 2), train_data_list)
    S = sum(train_data_list)
    test_data_list = read_data_file(test_data_file, lambda x: float(x))
    print '\n'.join(map(lambda elem: str(log_principal_anomaly(elem, N, Q, S)), test_data_list))


if __name__ == '__main__':
    main()
