import argparse
import re
def readRawAndLableDataFilePaths():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log_file', help = 'The raw http log file', required = True)
    parser.add_argument('-d', '--dest_file', help = 'Destination to store the resulting csv file', required = True)
    args = vars(parser.parse_args())
    return args


# Retrieve data from a http (access_log) log file
def extractData(log_file):
    regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (.+) "(.*?)" "(.*?)"'
    data = {}
    log_file = open(log_file, 'r')
    for log_line in log_file:
        log_line=log_line.replace(',','_')
        log_line = re.match(regex,log_line).groups()
        size = str(log_line[4]).rstrip('\n')
        return_code = log_line[3]
        url = log_line[2]
        param_number = len(url.split('&'))
        url_length = len(url)
        if '-' in size:
            size = 0
        else:
            size = int(size)
        if (int(return_code) > 0):
            charcs = {}
            charcs['size'] = int(size)
            charcs['param_number'] = int(param_number)
            charcs['length'] = int(url_length)
            charcs['return_code'] = int(return_code)
            data[url] = charcs
    return data
