##
## Poisson case
##

from math import *

def pmf(k, mean):
    return pow(mean, k) * exp(-mean) / factorial(k)

def cdf(k, mean):
    sum = 0
    for i in range(0, k + 1):
        sum += pmf(i, mean)
    return sum

def lower_quantile_cd(prob, mean):
    i = 0
    while (pmf(i, mean) <= prob and i <= mean):
        i = i+1
    return cdf(i-1, mean)

def upper_quantile_cd(prob, mean):
    i = mean
    while (pmf(i, mean) > prob):
        i = i+1
    return 1 - cdf(i, mean)

def log_principal_anomaly(k, mean):
    prob = pmf(k, mean)
    lower_q = lower_quantile_cd(prob, mean)
    upper_q = upper_quantile_cd(prob, mean)
    return -log(lower_q + upper_q)

def principal_anomaly(k, mean):
    prob = pmf(k, mean)
    lower_q = lower_quantile_cd(prob, mean)
    upper_q = upper_quantile_cd(prob, mean)
    return 1 - (lower_q + upper_q) #losing precision!

def main():
    for i in range(0, 20):
        print i, pmf(i, 5)
    print "========"
    for i in range(0, 20):
        print i, cdf(i, 5)
    print "========"
    for i in range(0, 20):
        print i, 1-cdf(i, 5)
    print "========"
    print "prob ", pmf(5, 5)
    print "lower ", lower_quantile_cd(pmf(5, 5), 5)
    print "upper ", upper_quantile_cd(pmf(5, 5), 5)
    print principal_anomaly(5, 5)

if __name__ == '__main__': 
    main() 
