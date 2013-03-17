#!/usr/bin/python
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "<first_file> <second_file>"
        exit(1)
    with open(sys.argv[1], 'rb') as file1, open(sys.argv[2], 'rb') as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()
        if len(lines1) != len(lines2):
            print "ERROR: files have different sizes!"
            exit(1)
        max_diff = 0
        for i in range(0, len(lines1) - 1):
            diff = float(lines1[i]) - float(lines2[i])
            if (diff > max_diff):
                max_diff = diff
            print diff
        print "Maximum =", max_diff