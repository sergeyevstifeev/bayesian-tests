#!/usr/bin/python

import os
import subprocess
import tempfile

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


def false_negatives_perc(data):
    return len(filter_normal(data)) * 100.0 / len(data)


def false_positives_perc(data):
    return len(filter_anomalous(data)) * 100.0 / len(data)

## Bayesian


def run_bayesian(dist_type, train_data, test_data):
    os.chdir("../isc2")
    out = subprocess.check_output(["./anomalydetector_impl", dist_type, train_data, test_data])
    os.chdir("../test")
    return out


def execute_bayesian_test(datafolder, dist_type):
    execute_test(datafolder, lambda x, y: run_bayesian(dist_type, x, y))


## Nonbayesian


def run_nonbayesian(dist_type, train_data, test_data):
    os.chdir("../nonbayesian")
    out = None
    if dist_type == "gaussian":
        out = subprocess.check_output(["./gaussian.R", train_data, test_data])
    elif dist_type == "poisson":
        out = subprocess.check_output(["./poisson.py", train_data, test_data])
    os.chdir("../test")
    return out


def execute_nonbayesian_test(datafolder, dist_type):
    execute_test(datafolder, lambda x, y: run_nonbayesian(dist_type, x, y))


def execute_test(data_folder, f):
    data_dirs = get_immediate_subdirectories(data_folder)
    if len(data_dirs) == 0:
        print "No data subfolders in", data_folder
        exit(1)
    for data_dir in data_dirs:
        # other_dirs = remove_element(data_dir, data_dirs)
        for other_data_dir in data_dirs:
            print data_dir, "against", other_data_dir
            # Get false negatives
            anom_out = to_float(
                f(get_merged_data(data_folder, data_dir), get_anomalous_data(data_folder, other_data_dir)))
            reference_anom_out = to_float(
                f(get_normal_data(data_folder, data_dir), get_anomalous_data(data_folder, other_data_dir)))
            print "False negatives perc:", false_negatives_perc(anom_out), "% after vs", false_negatives_perc(
                reference_anom_out), "% before"
            # Get false positives
            norm_out = to_float(f(get_merged_data(data_folder, data_dir), get_normal_data(data_folder, other_data_dir)))
            reference_norm_out = to_float(
                f(get_normal_data(data_folder, data_dir), get_normal_data(data_folder, other_data_dir)))
            print "False positives perc:", false_positives_perc(norm_out), "% after vs", false_positives_perc(
                reference_norm_out), "% before"

## Main


def main(data_folder, strategy, dist_type):
    if strategy == "frequentist":
        execute_nonbayesian_test(data_folder, dist_type)
    elif strategy == "bayesian":
        execute_bayesian_test(data_folder, dist_type)
    else:
        print "Unsupported strategy:", strategy
        exit(1)


def generate_data(spec_file, out_dir):
    os.chdir("../isc-test-datasets")
    # negative binomial
    out = None
    subprocess.check_output(["./generator.R", spec_file, out_dir])
    os.chdir("../test")
    return out


def test_spec():
    data_folder = "/Users/sergey/Apps/datasets/out_dir"
    data_spec = r'''Description,NormalType,AnomaliesType,NormalCount,AnomaliesCount,NormalMean,AnomaliesMean,NormalSd,AnomailesSd
data1,poisson,poisson,100,1,20,6,2,2
data2,poisson,poisson,10000,1,20,6,2,2
data3,poisson,poisson,100000,1,20,6,2,2
'''
    dist_type = "poisson"
    #    data_spec = r'''Description,NormalType,AnomaliesType,NormalCount,AnomaliesCount,NormalMean,AnomaliesMean,NormalSd,AnomailesSd
    #data1,gaussian,gaussian,100,1,15,6,2,2
    #data2,gaussian,gaussian,1000,1,15,6,2,2
    #data3,gaussian,gaussian,100000,1,15,6,2,2
    #'''
    #    dist_type = "gaussian"
    #
    #    data_spec = r'''Description,NormalType,AnomaliesType,NormalCount,AnomaliesCount,NormalMean,AnomaliesMean,NormalSd,AnomailesSd
    #data1,poisson,poisson,100,1,20,6,2,2
    #data2,poisson,poisson,10000,1,20,6,2,2
    #data3,poisson,poisson,100000,1,20,6,2,2
    #'''
    #    dist_type = "poisson"
    fd, path = tempfile.mkstemp()
    os.write(fd, data_spec)
    generate_data(path, data_folder)
    print "Bayesian:\n======================================="
    main(data_folder, "bayesian", dist_type)
    print "\nFrequentist:\n======================================="
    main(data_folder, "frequentist", dist_type)
    os.close(fd)
    os.remove(path)


if __name__ == '__main__':
    test_spec()
#    if len(sys.argv) != 4:
#        print "Usage:", sys.argv[0], "datafolder bayesian|frequentist gaussian|poisson"
#        exit(1)
#    datafolder = sys.argv[1]
#    if (not os.path.isdir(datafolder)):
#        print "Specified data folder", datafolder, "does not exist"
#        exit(1)
#    strategy = sys.argv[2]
#    if (strategy != "bayesian" and strategy != "frequentist"):
#        print "Unknown strategy:", strategy
#        exit(1)
#    dist_type = sys.argv[3]
#    if (dist_type != "gaussian" and dist_type != "poisson"):
#        print "Unknown distribution type:", dist_type
#        exit(1)
#    main(datafolder, strategy, dist_type)
