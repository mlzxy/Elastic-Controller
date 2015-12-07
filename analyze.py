#!/usr/bin/python
import csv
import math
import os
import sys
from os import listdir
from os.path import isfile, join,basename
    
global basic_restime_path, basic_throughput_path, migration_path
migration_path = 'chart_migration.csv'
basic_throughput_path = 'chart_basic_throughput.csv'
basic_restime_path = 'chart_basic_restime.csv'
import ipdb



def csvFiles(mypath):   

    onlyfiles = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
    return [f for f in onlyfiles if f.endswith('.csv')]

def usage():
    print "usage: "
    print "analyze.py /path/to/input/data"
    print "analyze.py /path/to/input/data /path/to/output/data"


def main(src_path, dst_path, interval):
    try:        
        global basic_restime_path, basic_throughput_path, migration_path
        basic_restime_path = join(dst_path, basic_restime_path)
        basic_throughput_path = join(dst_path, basic_throughput_path)
        migration_path = join(dst_path, migration_path)
        basic_restime_file = open(basic_restime_path, 'w')
        basic_throughput_file = open(basic_throughput_path, 'w')
        migration_file = open(migration_path, 'w')
        basic_restime_csv = csv.DictWriter(basic_restime_file,
                                           fieldnames=['Sending Rate',
                                                       '4-4-6633',
                                                       '4-4-6634',
                                                       '5-3-6633',
                                                       '5-3-6634'])
        basic_throughput_csv = csv.DictWriter(basic_throughput_file,
                                              fieldnames=['Sending Rate',
                                                          '4-4-6633',
                                                          '4-4-6634',
                                                          '5-3-6633',
                                                          '5-3-6634'])
        migration_csv = csv.DictWriter(migration_file,
                                       fieldnames=['Time',
                                                   '6633-restime',
                                                   '6634-restime',
                                                   '6633-throughput',
                                                   '6634-throughput'])
        
        csv_files = csvFiles(src_path)
        migration_dict = {}
        basic_throughput_dict = {}
        basic_restime_dict = {}
        
        for f in csv_files:
            with open(f) as csv_file:
                fname = basename(csv_file.name)
                if fname.startswith('migration'):
                    analyze_migrate(csv_file, migration_dict, interval)
                elif fname.startswith('5-3') or fname.startswith('4-4'):                    
                    analyze_restime(csv_file, basic_restime_dict)
                    analyze_throughput(csv_file, basic_throughput_dict)

        # ipdb.set_trace()
        dump(migration_csv, migration_dict, 'Time')
        dump(basic_restime_csv, basic_restime_dict, 'Sending Rate')
        dump(basic_throughput_csv, basic_throughput_dict, 'Sending Rate')        
                    
    finally:
        basic_restime_file.close()
        basic_throughput_file.close()
        migration_file.close()


def dump(writer, d, field):
    writer.writeheader()
    for key, value in d.iteritems():        
        value[field] = key
        # print value
        writer.writerow(value)

# {'time',
#  '6633-restime',
#  '6634-restime',
#  '6633-throughput',
#  '6634-throughput'}
#  one file insert a lot
def port(s, x):
    s = basename(s)
    l = len(s)
    r =  s[l-8:l-4]+'-'+x
    print s
    return r

def analyze_migrate(f,d,interval):        
    cursor  = interval    
    reader = csv.reader(f)
    res_key = port(f.name,'restime')
    throughput_key = port(f.name,'throughput')
    temp_dict = {}
    for row in reader:
        time = math.floor(float(row[0]))
        if temp_dict.has_key(time):
            temp_dict[time] = temp_dict[time] + 1
        else:
            temp_dict[time] = 1.0
    
    for k,v in temp_dict.iteritems():
        x = None
        if d.has_key(k):
            x = d[k]
        else:
            x = {}        
        x[res_key] = interval*2/v
        x[throughput_key] = v/(interval*2)
        d[k] = x

# {'Sending Rate',
# '4-4-6633',
# '4-4-6634',
# '5-3-6633',
# '5-3-6634'}
# one file, insert one
def field(string):
    string = basename(string)
    l = len(string)
    return string[0:4] + string[l-8:l-4]

def rate(string):
    string = basename(string)
    print string
    try:
        return int(string[4:8])
    except:
        return int(string[4:7])

def restime(f):
    reader = csv.reader(f)
    f.seek(0)
    rows = 0
    min_time = 10000
    max_time = -10000
    for row in reader:
        try:
            t = float(row[1])
            if t > max_time:
                max_time = t
            if t < min_time:
                min_time = t            
            rows = rows + 1
        except:
            continue
    return ((max_time - min_time)*2)/float(rows)

def thoughput(f):    
    reader = csv.reader(f)
    f.seek(0)
    rows = 0
    min_time = 10000
    max_time = -10000
    for row in reader:
        try:
            t = float(row[1])
            if t > max_time:
                max_time = t
            if t < min_time:
                min_time = t            
            rows = rows + 1
        except:
            continue
    # ipdb.set_trace()
    return float(rows)/((max_time - min_time)*2)
    
def analyze_restime(f,d):
    sending_rate = rate(f.name)
    key = field(f.name)
    x = None
    if d.has_key(sending_rate):
        x = d[sending_rate]
    else:
        x = {}
        d[sending_rate] = x
    x[key] = restime(f)


def analyze_throughput(f,d):
    sending_rate = rate(f.name)
    key = field(f.name)
    x = None
    if d.has_key(sending_rate):
        x = d[sending_rate]
    else:
        x = {}
        d[sending_rate] = x
    x[key] = thoughput(f)
        
    
if __name__ == '__main__':    
    # try:        
        if len(sys.argv) < 2:
            usage()
        elif len(sys.argv) == 2:
            main(os.path.abspath(sys.argv[1]), os.getcwd(), 1)
        elif len(sys.argv) == 3:
            main(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), 1)
        elif len(sys.argv) == 3:
            main(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), float(sys.argv[3]))            
    # except Exception as e:
    #     print e        
    #     usage()
