#!/usr/bin/python

import sys
import os
import subprocess

THRESHOLD = 14

##
## Helpers
##
def remove_element(el, l):
    return filter (lambda a: a != el, l)

def check_file_exists(f):
    if not os.path.isfile(f):
        print "File does not exist:", f
        exit(1)

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]

def get_data(data_dir, data_type):
    data = os.path.join(datafolder, data_dir, data_type)
    check_file_exists(data)
    return data

def get_normal_data(data_dir):
    return get_data(data_dir, "normal")

def get_anomalous_data(data_dir):
    return get_data(data_dir, "anomalous")

def get_merged_data(data_dir):
    return get_data(data_dir, "merged")

def filter_anomalous(l):
    return filter (lambda x: x > THRESHOLD, l)

def filter_normal(l):
    return filter (lambda x: x <= THRESHOLD, l)

def to_float(datastr):
    return map(float, datastr.splitlines())

##
## Bayesian
##
def run_bayesian(dist_type, train_data, test_data):
    os.chdir("../isc2")
    out = subprocess.check_output(["./anomalydetector_poisson", dist_type, train_data, test_data])
    os.chdir("../test")
    return out

def execute_bayesian_test(datafolder):
    execute_test(datafolder, lambda x,y,z: run_bayesian(x,y,z))

##
## Nonbayesian
##
def run_nonbayesian(dist_type, train_data, test_data):
    os.chdir("../nonbayesian")
    if (dist_type == "gaussian"):
        out = subprocess.check_output(["./gaussian.R", train_data, test_data])
    else:
        print "dist_type not supported:", dist_type
        exit(1)
    os.chdir("../test")
    return out

def execute_nonbayesian_test(datafolder):
    execute_test(datafolder, lambda x,y,z: run_nonbayesian(x,y,z))

def execute_test(datafolder, f):
    data_dirs = get_immediate_subdirectories(datafolder)
    for data_dir in data_dirs:
        other_dirs = remove_element(data_dir, data_dirs)
        for other_data_dir in other_dirs:
            # Get false negatives
            anom_out = to_float(f("gaussian", get_merged_data(data_dir), get_anomalous_data(other_data_dir)))
            print "False negatives perc:", len(filter_normal(anom_out))*100.0/len(anom_out), "%"
            # Get false positives
            norm_out = to_float(f("gaussian", get_merged_data(data_dir), get_normal_data(other_data_dir)))
            print "False positives perc:", len(filter_anomalous(norm_out))*100.0/len(norm_out), "%"

##
## Main
##
def main():
    execute_bayesian_test(datafolder)
    #execute_nonbayesian_test(datafolder)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "<datafolder>"
        exit(1)
    datafolder = sys.argv[1]
    if (not os.path.isdir(datafolder)):
        print "Specified data folder", datafolder, "does not exist"
        exit(1)
    main()
