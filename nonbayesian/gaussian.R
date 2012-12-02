#!/usr/bin/Rscript
library('getopt')

pa_gaussian <- function(x, mean=0, sd=1) {
    val = mean - abs(x - mean)
#    1 - 2*pnorm(val, mean=mean, sd=sd)
    -log(2*pnorm(val, mean=mean, sd=sd))
}
