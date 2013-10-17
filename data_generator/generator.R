#!/usr/bin/Rscript

#
# Called as:
#   generator.R <spec_file> <output_dir>
#

#Description,NormalType,AnomaliesType,NormalCount,AnomaliesCount,NormalMean,AnomaliesMean,NormalSd,AnomailesSd
description <- function(x) { x[1] }
normal_type <- function(x) { x[2] }
anomalies_type<- function(x) { x[3] }
normal_count <- function(x) { x[4] }
anomalies_count <- function(x) { x[5] }
normal_mean <- function(x) { x[6] }
anomalies_mean <- function(x) { x[7] }
normal_sd <- function(x) { x[8] }
anomalies_sd <- function(x) { x[9] }

read_specification <- function(filename) {
    read.table(filename, sep=",", header=TRUE)
}

generate_data <- function(type, number, mean, sd) {
    if (type == 'gaussian') {
        values <- rnorm(number, mean=mean, sd=sd)
        data.frame(value=values)
    } else if (type == 'poisson') {
        values <- rpois(number, lambda=mean)
        data.frame(value=values)
    } else {
        stop("wrong distribution type")
    }
}

maybe_add_intervals <- function(should_add, data) {
    if (should_add) {
        rows <- nrow(data)
        intervals <- rep(1, rows)
        new_values <- sapply(data$value, as.integer)
        data.frame(value=new_values, interval=intervals)
    } else {
        data
    }
}

generate_dataset <- function(x, out_dir="generated/") {
    should_add_intervals <-
        normal_type(x)    == "poisson" ||
        anomalies_type(x) == "poisson"
    normal_data <-
        maybe_add_intervals(should_add_intervals,
                            generate_data(normal_type(x),
                                          as.numeric(normal_count(x)),
                                          as.numeric(normal_mean(x)),
                                          as.numeric(normal_sd(x))))
    normal_data2 <-
        maybe_add_intervals(should_add_intervals,
                            generate_data(normal_type(x),
                                          as.numeric(normal_count(x)),
                                          as.numeric(normal_mean(x)),
                                          as.numeric(normal_sd(x))))

    anomalous_data <-
        maybe_add_intervals(should_add_intervals,
                            generate_data(anomalies_type(x),
                                          as.numeric(anomalies_count(x)),
                                          as.numeric(anomalies_mean(x)),
                                          as.numeric(anomalies_sd(x))))
    if (! file.exists(out_dir)) {
        dir.create(out_dir)
    }
    dirname <- file.path(out_dir, description(x))
    if (! file.exists(dirname)) {
        dir.create(dirname)
    }
    #message(paste("Writing", description(x), "into", dirname))
    write.table(normal_data, paste(dirname, "/normal", sep=""), row.names=FALSE, sep="\t", quote=FALSE)
    write.table(normal_data2, paste(dirname, "/normal2", sep=""), row.names=FALSE, sep="\t", quote=FALSE)
    write.table(anomalous_data, paste(dirname, "/anomalous", sep=""), row.names=FALSE, sep="\t", quote=FALSE)
    write.table(rbind(normal_data, anomalous_data), paste(dirname, "/merged", sep=""), row.names=FALSE, sep="\t", quote=FALSE)
}

main <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    spec_file <- args[1]
    out_dir   <- args[2]
    whatever  <- apply(read_specification(spec_file), 1, function(x) { generate_dataset(x, out_dir=out_dir) })
}

main()