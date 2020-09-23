from math import gcd, sqrt
from fractions import Fraction

#Function to convert float into fraction that is readable on a ruler
def rulerfrac(floatnum):
    if isinstance(floatnum, str):
        return floatnum
    else:
        d = 16; n = 1
        intnum = int(floatnum); decnum = floatnum - intnum
        if decnum > 0:
            while n / d < decnum:
                n += 1
            if n / d != decnum:
                if (n / d) - decnum > decnum - ((n - 1) / d):
                    n -= 1
            if gcd(n, d) > 0:
                gcdnum = gcd(n, d)
                n = n / gcdnum
                d = d / gcdnum
                if n == 0:
                    return intnum
                else:
                    if d == 1:
                        return intnum + 1
                    elif intnum > 0:
                        return ("{} {}/{}".format(intnum, int(n), int(d)))
                    else:
                        return ("{}/{}".format(int(n), int(d)))
        else:
            return intnum

#Function to write results onto a new created file
def print2newfile(filename, name1, data1, name2, data2, name3, data3):
    with open(filename, "w+") as printfile:
        add_space = 32 - len("{} {}".format(name1, data1))
        printfile.write("{} {}".format(name1, data1))
        for x in range(0, add_space):
            printfile.write(" ")
        add_space = 22 - len("{} {}".format(name2, data2))
        printfile.write("{} {}".format(name2, data2))
        for x in range(0, add_space):
            printfile.write(" ")
        printfile.write("{} {}{}".format(name3, data3, "\n"))

#Function to write results onto a pre-existing file
def print2file(filename, name1, data1, name2, data2, name3, data3):
    with open(filename, "a") as printfile:
        add_space = 32 - len("{} {}".format(name1, data1))
        printfile.write("{} {}".format(name1, data1))
        for x in range(0, add_space):
            printfile.write(" ")
        add_space = 22 - len("{} {}".format(name2, data2))
        printfile.write("{} {}".format(name2, data2))
        for x in range(0, add_space):
            printfile.write(" ")
        printfile.write("{} {}{}".format(name3, data3, "\n"))

#Function to find chord length of a pipe diameter
def ChordLength(radius, fromcenter):
    return(2 * (sqrt((radius * radius) - (fromcenter * fromcenter))))

#Function to convert fraction into float
def MakeFloat(stringfrac):
    return float(sum(Fraction(s) for s in stringfrac.split()))

#Function to find x of first row
def XofRow1(sideroom, firstpipe):
    return sideroom+(firstpipe/2)

#Function to find x of second row
def XofRow2(x1, middle, firstpipe, secondpipe):
    return x1+(firstpipe/2)+middle+(secondpipe/2)

#Function to convert string to boolean
def str2bool(str):
    return str.lower() in "true"

