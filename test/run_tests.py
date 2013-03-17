#!/usr/bin/python

import os
import shutil
import subprocess
import sys
from lib.common_utils import verify_file_exists

THRESHOLD = 6.9

## Helpers


def remove_element(el, l):
    return filter(lambda a: a != el, l)


def check_file_exists(f):
    if not os.path.isfile(f):
        print "File does not exist:", f
        exit(1)


def get_immediate_subdirectories(dir_name):
    return [name for name in os.listdir(dir_name)
            if os.path.isdir(os.path.join(dir_name, name))]


def get_data(data_folder, data_dir, data_type):
    data = os.path.join(data_folder, data_dir, data_type)
    check_file_exists(data)
    return data


def get_normal_data(data_folder, data_dir):
    return get_data(data_folder, data_dir, "normal")


def get_anomalous_data(data_folder, data_dir):
    return get_data(data_folder, data_dir, "anomalous")


def get_merged_data(data_folder, data_dir):
    return get_data(data_folder, data_dir, "merged")


def filter_anomalous(l):
    return filter(lambda x: x > THRESHOLD, l)


def filter_normal(l):
    return filter(lambda x: x <= THRESHOLD, l)


def to_float(datastr):
    return map(float, datastr.rstrip().splitlines())


def false_negatives_percentage(data):
    return len(filter_normal(data)) * 100.0 / len(data)


def false_positives_percentage(data):
    return len(filter_anomalous(data)) * 100.0 / len(data)

## Bayesian


def run_bayesian(normal_entries_distr, train_data, test_data):
    out = None
    os.chdir("../bayesian")
    if normal_entries_distr == "gaussian":
        out = subprocess.check_output(["./t_student.py", train_data, test_data])
    elif normal_entries_distr == "poisson":
        out = subprocess.check_output(["./negative_binomial.R", train_data, test_data])
    os.chdir("../test")
    return out


def execute_bayesian_test(data_folder, normal_entries_distr):
    execute_test(data_folder, lambda x, y: run_bayesian(normal_entries_distr, x, y))


## Nonbayesian


def run_nonbayesian(normal_entries_distr, train_data, test_data):
    os.chdir("../nonbayesian")
    out = None
    if normal_entries_distr == "gaussian":
        out = subprocess.check_output(["./gaussian.R", train_data, test_data])
    elif normal_entries_distr == "poisson":
        out = subprocess.check_output(["./poisson.py", train_data, test_data])
    os.chdir("../test")
    return out


def execute_nonbayesian_test(datafolder, normal_entries_distr):
    execute_test(datafolder, lambda x, y: run_nonbayesian(normal_entries_distr, x, y))


def execute_test(data_folder, f):
    data_dirs = get_immediate_subdirectories(data_folder)
    if len(data_dirs) == 0:
        print "No data subfolders in", data_folder
        exit(1)
    for data_dir in data_dirs:
        for other_data_dir in [data_dir]:
            print data_dir, "against", other_data_dir
            # Get false negatives
            anom_out = to_float(
                f(get_merged_data(data_folder, data_dir), get_anomalous_data(data_folder, other_data_dir)))
            reference_anom_out = to_float(
                f(get_normal_data(data_folder, data_dir), get_anomalous_data(data_folder, other_data_dir)))
            print "False negatives perc:", false_negatives_percentage(anom_out), "% after",\
                "vs", false_negatives_percentage(reference_anom_out), "% before"
            # Get false positives
            norm_out = to_float(f(get_merged_data(data_folder, data_dir), get_normal_data(data_folder, other_data_dir)))
            reference_norm_out = to_float(
                f(get_normal_data(data_folder, data_dir), get_normal_data(data_folder, other_data_dir)))
            print "False positives perc:", false_positives_percentage(norm_out), "% after ",\
                "vs", false_positives_percentage(reference_norm_out), "% before"

## Main


def test_all(data_folder, strategy, normal_entries_distr):
    if strategy == "frequentist":
        execute_nonbayesian_test(data_folder, normal_entries_distr)
    elif strategy == "bayesian":
        execute_bayesian_test(data_folder, normal_entries_distr)
    else:
        print "Unsupported strategy:", strategy
        exit(1)


def generate_data(spec_file, out_dir):
    os.chdir("../data_generator")
    out = None
    subprocess.check_output(["./generator.R", spec_file, out_dir])
    os.chdir("../test")
    return out


def clean_folder(data_folder):
    subdirs = get_immediate_subdirectories(data_folder)
    for subdir in subdirs:
        shutil.rmtree(os.path.join(data_folder, subdir))


def test_spec(out_dir, data_spec):
    normal_entries_distr = "gaussian"
    clean_folder(out_dir)
    generate_data(data_spec, out_dir)
    print "Bayesian:\n======================================="
    test_all(out_dir, "bayesian", normal_entries_distr)
    print "\nFrequentist:\n======================================="
    test_all(out_dir, "frequentist", normal_entries_distr)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Usage:", sys.argv[0], "<data_spec> <normal_entries_distr> <out_dir>\n"
        print "Note that contents of <out_dir> will be wiped out!"
        exit(1)
    data_spec = sys.argv[1]
    normal_entries_distr = sys.argv[2]
    out_dir = sys.argv[3]
    verify_file_exists(data_spec)
    test_spec(out_dir, data_spec)
