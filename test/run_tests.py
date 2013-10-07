#!/usr/bin/python

import os
import shutil
import subprocess
import sys
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], '..'))
from lib.common_utils import verify_file_exists

BASE_DIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')

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


def filter_anomalous(l, threshold):
    return filter(lambda x: x > threshold, l)


def filter_normal(l, threshold):
    return filter(lambda x: x <= threshold, l)


def to_float(datastr):
    return map(float, datastr.rstrip().splitlines())


def false_negatives_rate(data, threshold):
    return len(filter_normal(data, threshold)) / float(len(data))


def false_positives_rate(data, threshold):
    return len(filter_anomalous(data, threshold)) / float(len(data))

## Bayesian


def run_bayesian(normal_entries_distr, train_data, test_data):
    out = None
    os.chdir(os.path.join(BASE_DIR, "bayesian"))
    if normal_entries_distr == "gaussian":
        out = subprocess.check_output(["./t_student.py", train_data, test_data])
    elif normal_entries_distr == "poisson":
        out = subprocess.check_output(["./negative_binomial.R", train_data, test_data])
    os.chdir(os.path.join(BASE_DIR, "test"))
    return out


def calculate_bayesian_rates(data_folder, normal_entries_distr, threshold):
    return calculate_rates(data_folder, lambda x, y: run_bayesian(normal_entries_distr, x, y), threshold)


## Nonbayesian


def run_nonbayesian(normal_entries_distr, train_data, test_data):
    os.chdir(os.path.join(BASE_DIR, "nonbayesian"))
    out = None
    if normal_entries_distr == "gaussian":
        out = subprocess.check_output(["./gaussian.R", train_data, test_data])
    elif normal_entries_distr == "poisson":
        out = subprocess.check_output(["./poisson.py", train_data, test_data])
    os.chdir(os.path.join(BASE_DIR, "test"))
    return out


def calculate_nonbayesian_rates(datafolder, normal_entries_distr, threshold):
    return calculate_rates(datafolder, lambda x, y: run_nonbayesian(normal_entries_distr, x, y), threshold)


def calculate_rates(data_folder, f, threshold):
    data_dirs = get_immediate_subdirectories(data_folder)
    if len(data_dirs) == 0:
        print "No data subfolders in", data_folder
        exit(1)
    for data_dir in data_dirs:
        # Fetch data
        merged_data = get_merged_data(data_folder, data_dir)
        anomalous_data = get_anomalous_data(data_folder, data_dir)
        normal_data = get_normal_data(data_folder, data_dir)
        # Calculate false negative rates
        false_negative_rate_merged = false_negatives_rate(to_float(f(merged_data, anomalous_data)), threshold)
        false_negative_rate_clean = false_negatives_rate(to_float(f(normal_data, anomalous_data)), threshold)
        ## Calculate false positive rates
        false_positive_rate_merged = false_positives_rate(to_float(f(merged_data, normal_data)), threshold)
        false_positive_rate_clean = false_positives_rate(to_float(f(normal_data, normal_data)), threshold)
        return (false_negative_rate_merged,
                false_negative_rate_clean,
                false_positive_rate_merged,
                false_positive_rate_clean)

## Main


def rates(data_folder, strategy, normal_entries_distr, threshold):
    if strategy == "frequentist":
        return calculate_nonbayesian_rates(data_folder, normal_entries_distr, threshold)
    elif strategy == "bayesian":
        return calculate_bayesian_rates(data_folder, normal_entries_distr, threshold)
    else:
        print "Unsupported strategy:", strategy
        exit(1)


def generate_data(spec_file, out_dir):
    os.chdir(os.path.join(BASE_DIR, "data_generator"))
    out = None
    subprocess.check_output(["./generator.R", spec_file, out_dir])
    os.chdir(os.path.join(BASE_DIR, "test"))
    return out


def clean_folder(data_folder):
    subdirs = get_immediate_subdirectories(data_folder)
    for subdir in subdirs:
        shutil.rmtree(os.path.join(data_folder, subdir))


def test_spec(out_dir, data_spec, normal_entries_distr):
    generate_data(data_spec, out_dir)
    threshold = 6.9
    print "Bayesian:\n======================================="
    rates(out_dir, "bayesian", normal_entries_distr, threshold)
    print "\nFrequentist:\n======================================="
    rates(out_dir, "frequentist", normal_entries_distr, threshold)

def average_rates(out_dir, data_spec, normal_entries_distr, threshold, iterations, strategy):
    false_negative_rate_merged_acc = 0
    false_negative_rate_clean_acc = 0
    false_positive_rate_merged_acc = 0
    false_positive_rate_clean_acc = 0
    for i in range(0, iterations):
        sys.stdout.write('.')
        generate_data(data_spec, out_dir)
        (false_negative_rate_merged,
         false_negative_rate_clean,
         false_positive_rate_merged,
         false_positive_rate_clean) = rates(out_dir, strategy, normal_entries_distr, threshold)
        false_negative_rate_merged_acc += false_negative_rate_merged
        false_negative_rate_clean_acc += false_negative_rate_clean
        false_positive_rate_merged_acc += false_positive_rate_merged
        false_positive_rate_clean_acc += false_positive_rate_clean
    return (false_negative_rate_merged_acc/float(iterations),
            false_negative_rate_clean_acc/float(iterations),
            false_positive_rate_merged_acc/float(iterations),
            false_positive_rate_clean_acc/float(iterations))


if __name__ == '__main__':
    if len(sys.argv) != 7:
        print "Usage:", sys.argv[0], "<data_spec> <normal_entries_distr> <out_dir> <iterations> <threshold> <frequentist|bayesian>\n"
        print "Note that contents of <out_dir> will be wiped out!"
        exit(1)
    data_spec = sys.argv[1]
    normal_entries_distr = sys.argv[2]
    out_dir = sys.argv[3]
    iterations = int(sys.argv[4])
    threshold = float(sys.argv[5])
    strategy = sys.argv[6]
    verify_file_exists(data_spec)
    print average_rates(out_dir, data_spec, normal_entries_distr, threshold, iterations, strategy)
