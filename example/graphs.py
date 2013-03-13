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


def graph_predictive_normal(args):
    dist_entries = map(float, args[1:])
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
    print "Plot[{PDF[StudentTDistribution[", Mean, ",", \
        math.sqrt(student_variance(N, Q, S)), ",", N - 1, "], x], PDF[NormalDistribution[", \
        Mean, ",", normal_stand_deviation(dist_entries), "], x], PDF[NormalDistribution[0, 1], x]}, {x, -4, 4}]"


def graph_predictive_poisson(args):
    dist_entries = map(float, args[1:])
    print "Distribution entries:", dist_entries
    N = len(dist_entries)
    S = sum(dist_entries)
    Mean = S / N
    print "N =", N
    print "S =", S
    print "Mean =", Mean
    print "DiscretePlot[" \
          "{PDF[PoissonDistribution[", Mean, "], k], " \
          "PDF[PoissonDistribution[20], k], " \
          "PDF[NegativeBinomialDistribution[", int(S), ", ", float(N) / (N + 1), "], k]}, " \
          "{k, 0, 60}, " \
          "PlotRange -> All, " \
          "PlotMarkers -> Automatic]"


if __name__ == '__main__':
    graph_predictive_poisson(sys.argv)

