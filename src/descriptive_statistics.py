from lxml import etree

import csv
import sys

# Returns the minimum value in a list of integers/floats.
def findMin(column):
    minimum = column[0]
    for num in column:
        if num < minimum:
            minimum = num
    return(str(minimum))

# Returns the maximum value in a list of integers/floats.
def findMax(column):
    maximum = column[0]
    for num in column:
        if num > maximum:
            maximum = num
    return(str(maximum))

# Returns the nth quartile in a list of integers/floats.
# Argument 2: 25 = Q1, 50 = median, 75 = Q3
def findQuartile(column, percent):
    from math import floor
    quartile = float((len(column) + 1) * percent) / 100

    # Odd number of numbers in column.
    if floor(quartile) == quartile:
        # First quartile
        if percent < 50:
            return(str(float(column[int(floor(quartile)) - 1]
                    + column[int(floor(quartile))]) / 2))
        # Third quartile
        elif percent > 50:
            return(str(float(column[int(floor(quartile)) - 2]
                    + column[int(floor(quartile)) - 1]) / 2))
        # Median
        return(str(float(column[int(floor(quartile)) - 1])))

    # Even number of numbers in column.
    return(str(float(column[int(floor(quartile)) - 1]
            + column[int(floor(quartile))]) / 2))

# Returns a list of modes of a list of integers/floats.
def findModes(column):
    counter = {}
    modelist = []
    modecount = 2
    # Counts the number of times an item is in the list.
    for item in column:
        if item not in counter:
            counter[item] = 0
        else:
            counter[item] += 1
            if counter[item] >= modecount:
                modecount = counter[item]
    # Determines the highest item count(s).
    for item in counter:
        if counter[item] == modecount:
            modelist.append(str(item))
    return(modelist)

# Returns a sorted list of unique strings in a column.
def findUniques(column):
    uniquelist = list(set(column))
    uniquelist.sort()
    return(uniquelist)

# Determines a suitable type for a column.
def typeIdentify(column):
    for data in column:
        try:
            float(data)
            try:
                int(data)
            except ValueError:
                return("float")
        except ValueError:
            return("string")
    return("integer")

# Converts string data into integers or floats when possible.
def typeConvert(data):
    try:
        float(data)
        try:
            int(data)
            return(int(data))
        except ValueError:
            return(float(data))
    except ValueError:
        return(data)

def main():
    # Parses the input csv file.
    file = open(sys.argv[len(sys.argv) - 1])
    dataset = csv.reader(file)
    header = next(dataset)

    # Extract and converts data into their respective columns.
    columns = []
    for row in dataset:
        for data in row:
            try:
                columns[row.index(data)].append(typeConvert(data))
            except IndexError:
                columns.append([])
                columns[row.index(data)].append(typeConvert(data))

    # Builds xml tree based on the column data.
    root = etree.Element('attributes')
    for col in columns:
        col.sort()
        attr = etree.SubElement(root, 'attribute', type=typeIdentify(col))
        etree.SubElement(attr, 'name').text = header[columns.index(col)].strip()

        # Computes five-number-summary for numerical data.
        if attr.get("type") != "string":
            prop = etree.SubElement(attr, 'properties')
            etree.SubElement(prop, 'property', name='min').text = findMin(col)
            etree.SubElement(prop, 'property', name='q1'
                            ).text = findQuartile(col, 25)
            etree.SubElement(prop, 'property', name='median'
                            ).text = findQuartile(col, 50)
            etree.SubElement(prop, 'property', name='q3'
                            ).text = findQuartile(col, 75)
            etree.SubElement(prop, 'property', name='max').text = findMax(col)

        # Determines the mode(s) of the column.
        modes = etree.SubElement(attr, 'modes')
        modelist = findModes(col)
        for mode in modelist:
            etree.SubElement(modes, 'mode').text = mode

        # Finds unique values for strings.
        if attr.get("type") == "string":
            uniques = etree.SubElement(attr, 'uniques')
            uniquelist = findUniques(col)
            for unique in uniquelist:
                etree.SubElement(uniques, 'unique').text = unique

    # Produces the output.xml file.
    summary = open("summary.dtd").read()
    output = summary + etree.tostring(root, pretty_print=True, encoding="UTF-8")
    open("output.xml", 'w').write(output)
    file.close()

if __name__ == '__main__':
    main()
