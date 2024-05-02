import csv

def init_portcsv(dpid):
    fname = "switch_" + str(dpid) + "_data.csv"
    writer = csv.writer(open(fname, 'a', buffering=1), delimiter=',')
    header = ["time", "sfe","ssip","rfip","type"]
    writer.writerow(header)

    
def init_flowcountcsv(dpid):
    fname = "switch_" + str(dpid) + "_flowcount.csv"
    writer = csv.writer(open(fname, 'a', buffering=1), delimiter=',')
    header = ["time", "flowcount"]
    writer.writerow(header)



def update_flowcountcsv(dpid, row):
    fname = "switch_" + str(dpid) + "_flowcount.csv"
    writer = csv.writer(open(fname, 'a', buffering=1), delimiter=',')
    writer.writerow(row)


def update_portcsv(dpid, row):
    fname = "switch_" + str(dpid) + "_data.csv"
    writer = csv.writer(open(fname, 'a', buffering=1), delimiter=',')
    writer.writerow(row)



def update_resultcsv(row,TEST_TYPE):
    fname = "result.csv"
    writ = csv.writer(open(fname, 'a', buffering=1), delimiter=',')
    row.append(str(TEST_TYPE))
    writ.writerow(row)




