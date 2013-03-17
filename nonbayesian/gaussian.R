#!/usr/bin/Rscript

pa_gaussian <- function(x, mean, sd) {
    val <- mean - abs(x - mean)
    -log(2*pnorm(val, mean=mean, sd=sd))
}

get_mean <- function(dataframe) {
    mean(dataframe$value)
}

get_sd <- function(dataframe) {
    sd(dataframe$value)
}

main <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    train_data <- args[1]
    test_data  <- args[2]
    train_dataframe <- read.table(train_data, header=TRUE)
    mean <- get_mean(train_dataframe)
    sd <- get_sd(train_dataframe)
    test_dataframe <- read.table(test_data, header=TRUE)
    pa_list <- lapply(test_dataframe, function(elem) { pa_gaussian(elem, mean, sd) })
    cat(unlist(pa_list), sep="\n")
}

main()
