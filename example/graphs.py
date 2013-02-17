#!/usr/bin/python

import sys
import math


def student_variance(N, Q, S):
    return (N * Q - math.pow(S, 2)) * (N - 1) / (N * (N + 1) * (N - 3))


def normal_variance(dist_entries):
    average = sum(dist_entries) / len(dist_entries)
    return sum(map(lambda x: math.pow(x - average, 2), dist_entries)) / len(dist_entries)


def normal_stand_deviation(dist_entries):
    return math.sqrt(normal_variance(dist_entries))


if __name__ == '__main__':
    dist_entries = map(float, sys.argv[1:])
    print "Distribution entries:", dist_entries
    N = len(dist_entries)
    S = sum(dist_entries)
    Q = sum(map(lambda x: math.pow(x, 2), dist_entries))
    Mean = S / N
    print "N =", N
    print "S =", S
    print "Q =", Q
    print "S/N =", Mean
    print "Student variance =", student_variance(N, Q, S)
    print "Normal standard deviation=", normal_stand_deviation(dist_entries)
    print "Plot[{PDF[StudentTDistribution[", Mean, ",",\
        math.sqrt(student_variance(N, Q, S)), ",", N - 1, "], x], PDF[NormalDistribution[", \
        Mean, ",", normal_stand_deviation(dist_entries), "], x], PDF[NormalDistribution[0, 1], x]}, {x, -4, 4}]"

