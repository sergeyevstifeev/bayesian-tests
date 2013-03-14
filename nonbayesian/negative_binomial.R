#!/usr/bin/Rscript

inf_substitute <- 2147483647

pmf <- function(k, size, prob) {
    dnbinom(k, size=size, prob=prob)
}

cdf <- function(k, size, prob) {
    pnbinom(k, size=size, prob=prob)
}

neg_bin_max <- function(size, prob) {
    i <- 0
    pmv <- pmf(i, size, prob)
    while(pmf(i + 1, size, prob) > pmv) {
        pmv <- pmf(i + 1, size, prob)
        i <- i + 1
    }
    i
}

lower_quantile_cd <- function(val, size, prob) {
    i <- 0
    max <- neg_bin_max(size, prob)
    if (pmf(i, size, prob) > val) {
        0
    } else {
        while((pmf(i, size, prob) <= val) & (i <= max)) {
            i <- i + 1
        }
        cdf(max(0, i - 1), size, prob)
    }
}

upper_quantile_cd <- function(val, size, prob) {
    i <- neg_bin_max(size, prob)
    while(pmf(i, size, prob) > val) {
        i <- i + 1
    }
    1 - cdf(i, size, prob)
}

log_principal_anomaly <- function(k, size, prob) {
    val <- pmf(k, size, prob)
    lower_q <- lower_quantile_cd(val, size, prob)
    upper_q <- upper_quantile_cd(val, size, prob)
    result <- -log(lower_q + upper_q)
    ifelse(result == Inf, inf_substitute, result)
}

get_size <- function(dataframe) {
    sum(dataframe$value)
}

get_prob <- function(dataframe) {
    N <- length(dataframe$value)
    N / (N + 1)
}

main <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    train_data <- args[1]
    test_data  <- args[2]
    train_dataframe <- read.table(train_data, header=TRUE)
    size <- get_size(train_dataframe)
    prob <- get_prob(train_dataframe)
    test_dataframe <- read.table(test_data, header=TRUE)
    pa_list <- lapply(test_dataframe$value, function(elem) { log_principal_anomaly(elem, size, prob) })
    cat(unlist(pa_list), sep="\n")
}

main()
