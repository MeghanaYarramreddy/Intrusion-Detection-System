import file_parse_utils

args = file_parse_utils.readRawAndLableDataFilePaths()
logFile = args['log_file']
labelDataFile = args['dest_file']
patterns = ['honeypot', '%3b', 'xss', 'sql', 'union', '%3c', '%3e', 'eval','%27;','%20where%20']
# Label data by adding a new raw with two possible values
# 1 for attack or suspecious activity and 0 for normal behavior
def labelHttpAccessLogData(data,labeled_data):
    for w in data:
        attack = '0'
        if any(pattern in w.lower() for pattern in patterns):
           attack = '1'
        data_row = str(data[w]['length']) + ',' + str(data[w]['param_number']) + ',' + str(data[w]['return_code']) + ',' + attack + ',' + w + '\n'
        labeled_data.write(data_row)
    print (str(len(data)) + ' rows have successfully saved to ' + labelDataFile)

labelHttpAccessLogData(file_parse_utils.extractData(logFile),open(labelDataFile, 'w'))