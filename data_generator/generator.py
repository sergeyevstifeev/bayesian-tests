#!/usr/bin/python
import csv
import sys
from scipy.stats import norm
from scipy.stats import poisson
import numpy as np
import os

def read_specification(spec_file):
    with open(spec_file, 'rb') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        spec = reader.next()  # expecting single row
        return spec


def generate_data(type, number, mean, sd):
    if type == 'gaussian':
        return norm.rvs(loc=mean, scale=sd, size=number)
    elif type == 'poisson':
        return poisson.rvs(mean, size=number)
    else:
        raise("wrong distribution type", type)


def write(with_intervals, data, out_filename):
    if with_intervals:
        fieldnames=['value', 'interval']
    else:
        fieldnames=['value']
    with open(out_filename, 'wb') as out_file:
        csv_writer = csv.DictWriter(out_file, delimiter='\t', fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in data:
            if with_intervals:
                csv_writer.writerow(dict(value=row, interval=1))
            else:
                csv_writer.writerow(dict(value=row))


def generate_dataset(spec, out_dir):
    description = spec['Description']
    should_add_intervals = spec['NormalType'] == "poisson" or spec['AnomaliesType'] == "poisson"
    normal_type = spec['NormalType']
    normal_count = int(spec['NormalCount'])
    normal_mean = float(spec['NormalMean'])
    normal_sd = float(spec['NormalSd'])
    anomalies_type = spec['AnomaliesType']
    anomalies_count = int(spec['AnomaliesCount'])
    anomalies_mean = float(spec['AnomaliesMean'])
    anomalies_sd = float(spec['AnomailesSd'])
    normal_data = generate_data(normal_type, normal_count, normal_mean, normal_sd)
    anomalies_data = generate_data(anomalies_type, anomalies_count, anomalies_mean, anomalies_sd)
    dest_dir = os.path.join(out_dir, description)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    write(should_add_intervals, normal_data, os.path.join(dest_dir, 'normal'))
    write(should_add_intervals, anomalies_data, os.path.join(dest_dir, 'anomalous'))
    write(should_add_intervals, np.append(normal_data, anomalies_data), os.path.join(dest_dir, 'merged'))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "<spec_file> <out_dir>"
        exit(1)
    spec_file = sys.argv[1]
    out_dir = sys.argv[2]
    generate_dataset(read_specification(spec_file), out_dir)