#!/usr/bin/python

#############################################################################
# Program to run openeye pipeline from filter to rocs.
#############################################################################

import shutil
from itertools import repeat
from time import sleep
import argparse, sys
from pathlib import Path
import os
import re

out_filename_map = {
        'basic' : 'filtered_basic.smi',
        'pains' : 'filtered_pains.smi',
        'blockbuster': 'filtered_blockbuster.smi',
        'oeomega' : 'oeomega_conformers.oeb.gz'
        }

def read_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", type = str, 
                    help="Input file to be filtered. Smiles format recommended.")
    parser.add_argument("-upto", type = str, 
                    help="Run pipeline upto [basic filter,pains filter, oeomega, rocs].")
    parser.add_argument("-only", type = str, 
                    help="Run only step pipeline [basic filter,pains filter, oeomega, rocs].")
    parser.add_argument("-from", type = str, 
                    help="Run step pipeline from[basic filter,pains filter, oeomega, rocs].")
    parser.add_argument("-filter", type = str, 
                    help="Filter criteria file or argument.")
    parser.add_argument("-mpi_np", type = str, 
                    help="How many cores to use? Default 8.")
    parser.add_argument("-query", type = str, 
                    help="Query moelcule for running ROCS.")
    args=vars(parser.parse_args())
    
    return args

args = read_cmdline()
print("filter type {}, {}".format(args.keys(),args.values()))
    
arguments = [arg for arg in args.values() if arg is not None]

if len(arguments) < 2:
    print(
        """Please enter the correct number of arguments.
    Usage: python pipeline.py -in INFILE -upto [basic|pains|oeomega|rocs] -only [basic|pains|oeomega|rocs] 
    -from [basic|pains|oeomega|rocs] -filter FILTERFILE [optional] -mpi_np CORES [optional: default 8] -oeomega [optional]
    or run python pipeline.py -h for further help
    """)
    sys.exit(1)

def error_message(key, file):
    return("-{} {} file does not exist.".format(key,file))

def check_condition(key, value):
        if key == 'filter' and value not in ['basic','pains','blockbuster'] and not os.path.isfile(value):
            return True
        elif key == 'upto' and value not in ['basic']:
            return True
        elif key == 'only' and value in ['basic']:
            return True
        elif key == 'from' and value in ['basic']:
            return True
        else:
            return False

def check_file(key, value):
    if key == 'in' and not os.path.isfile(value):
        print(error_message(key,value))
        sys.exit(1)
    elif key == 'query' and not os.path.isfile(value):
        print(error_message(key,value))
        sys.exit(1)
    elif check_condition(key,value):
        print("creating default filter file {}".format('basic'))
        create_filter = """
MIN_CARBONS 5 "Minimum number of carbons"
MAX_CARBONS 40 "Maximum number of carbons"
AGGREGATORS true "Eliminate know aggregators"
PRED_AGG true "Eliminate predicted aggregators"
MIN_MOLWT 130 "Minimum molecular weight"
MAX_MOLWT 650 "Maximum molecular weight"
MAX_UNBRANCHED 10 "Maximum number of connected unbranched non-ring atoms"
MIN_XLOGP -3.0 "Minimum XLogP"
MAX_XLOGP 6.5 "Maximum XLogP"
MIN_RING_SIZE 5 "Minimum atoms in any ring system"
TYPECHECK true "Screen for unusual valences or charges"
MMFFTYPECHECK true "Screen for atoms with unknown MMFF atom types"
ELIMINATE_METALS true "Eliminate metals"        
            """
        f = open('basic',"w")
        f.write(create_filter)
        f.close()


def check_tool(prog='filter', pattern='openeye/bin/filter'):
    pattern = pattern

    path = shutil.which(prog) 
    if path is None:
        print("Please install OpenEye " + prog + " program with valid license first")
    elif pattern in path: 
        print("Ok. OpenEye filter installed")
    else:
        print("OpenEye filter executable not found")

def animate(n=5):
    n_points = n
    points_l = repeat('.',n_points)
    for points in points_l:
        print(points, end='')
        sleep(0.1)

def call_animate(calls = 3):
    print("Checking for OpenEye installation.")
    for call in range(calls):
        animate(n=call+3)
        print("\r")


call_animate()
sleep(1)
check_tool()


def run_filter(in_file,out_file, filter):
    filter_cmd = "filter -in" + " " + in_file + " " + "-out" + \
    " " + out_file + " " + "-filter" + " " + filter + \
    " " + "-unique true -mmff true"

    os.system(filter_cmd)

def run_oeomega(in_file, out_file, progress= 'percent', mpi_np = 8):
    omega_cmd = "oeomega rocs -in" + " " + in_file + " "  + "-out" + \
    " " + out_file + " " + "-mpi_np" + " " + str(mpi_np) + " " + "-progress" + " " + progress + " " + "-strictstereo false"
    print(omega_cmd)
    os.system(omega_cmd)

def run_rocs(in_file, query, mpi_np):
    rocs_cmd = "rocs -dbase" + " " + in_file + " " + "-query" + " " + query + " " + "-mpi_np" + " " + str(mpi_np)
    os.system(rocs_cmd)

def create_dir(dirname):
    os.makedirs(dirname, exist_ok = True)


def move_files_to(dirname):
    file_regex = r"^filter[ed.]*|oeomega_*|^basic$"
    cwd = os.getcwd()
    fnames = [f for f in os.listdir(cwd) if os.path.isfile(f) and re.search(file_regex,f,re.IGNORECASE)]
    source = cwd + "/" + dirname + "/"
    create_dir(dirname = dirname)
    
    for fname in fnames:
        shutil.move(os.path.join(cwd,fname),os.path.join(source,fname))
    

def get_path(dirname,file):
    cwd = os.getcwd()
    return(os.path.join(cwd,dirname,file))

def assign_mpi_np(mpi):
    return 8 if mpi is None else mpi


#print("Running Filter...")
if args['upto'] == 'basic':
    for key,value in (args.items()):
        if key in ['in','filter']:
            check_file(key.lower(), str(value))
    
    filter_type = 'basic'
    print("Running the {} filter".format(filter_type))
    run_filter(in_file = args['in'], out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    move_files_to(dirname="basic_filter")
     
elif args['upto'] in ['pains','blockbuster']: 
    for key,value in (args.items()):
        if key in ['in','upto']:
            check_file(key.lower(), str(value))

    filter_type = 'basic'
    print("Running the {} filter".format(filter_type))
    run_filter(in_file = args['in'], out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    move_files_to(dirname="basic_filter")
    if args['filter'] and args['filter'] in ['pains','blockbuster']:
        filter_type = args['filter']
    else:
        filter_type = 'pains'

    print("Running the {} filter".format(filter_type))
    in_file = get_path(dirname="basic_filter", file = out_filename_map['basic'])
    run_filter(in_file = in_file, out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    dirname = filter_type + "_" + "filter"
    move_files_to(dirname=dirname)

elif args['upto'] == 'oeomega':
    for key,value in (args.items()):
        if key in ['in','upto']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])

    print("Running the {} filter".format('basic'))
    run_filter(in_file = args['in'], out_file = out_filename_map['basic'], filter = 'basic')
    sleep(1)
    move_files_to(dirname="basic_filter")

    print("Running the {} filter".format('pains'))
    in_file = get_path(dirname="basic_filter", file = out_filename_map['basic'])
    run_filter(in_file = in_file, out_file = out_filename_map['pains'], filter = 'pains')
    sleep(1)
    move_files_to(dirname="pains_filter")
    in_file = get_path(dirname="pains_filter", file = out_filename_map['pains'])
    print("Generating conformers")
    run_oeomega(in_file = in_file, out_file = out_filename_map['oeomega'], mpi_np = mpi_np)
    move_files_to(dirname="oeomega")

elif args['upto'] in ['rocs','all']:
    for key,value in (args.items()):
        if key in ['in','upto','query']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])

    run_filter(in_file = args['in'], out_file = out_filename_map['basic'], filter = 'basic')
    sleep(1)
    move_files_to(dirname="basic_filter")
    print("Running the {} filter".format('pains'))
    sleep(1)
    in_file = get_path(dirname="basic_filter", file = out_filename_map['basic'])
    run_filter(in_file = in_file, out_file = out_filename_map['pains'], filter = 'pains')
    move_files_to(dirname="pains_filter")
    in_file = get_path(dirname="pains_filter", file = out_filename_map['pains'])
    print("Generating conformers")
    run_oeomega(in_file=in_file, out_file = out_filename_map['oeomega'] ,mpi_np = mpi_np)
    move_files_to(dirname="oeomega")
    sleep(1)
    print("Running ROCS")
    in_file = get_path(dirname="oeomega", file = out_filename_map['oeomega'])
    run_rocs(in_file = in_file, query = args['query'], mpi_np = mpi_np)

elif args['only'] == 'basic': 
    for key,value in (args.items()):
        if key in ['in','filter']:
            check_file(key.lower(), str(value))
    
    filter_type = 'basic'
    print("Running the {} filter".format(filter_type))
    run_filter(in_file = args['in'], out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    move_files_to(dirname="basic_filter")

elif args['only'] in ['pains','blockbuster']:
    for key,value in (args.items()):
        if key in ['in']:
            check_file(key.lower(), str(value))

    if args['filter'] not in ['pains','blockbuster']:
        print("Filter option is not defined. Please use -filter pains/blockbuster")
        sys.exit(1)
    else: 
        filter_type = args['filter']

    print("Running the {} filter".format(filter_type))
    run_filter(in_file = args['in'], out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    dirname = filter_type + "_" + "filter"
    move_files_to(dirname=dirname)

elif args['only'] == 'oeomega':
    for key,value in (args.items()):
        if key in ['in']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])

    print("Generating conformers")
    run_oeomega(in_file = args['in'], out_file = out_filename_map['oeomega'], mpi_np = mpi_np)
    move_files_to(dirname="oeomega")

elif args['only'] in ['rocs']:
    for key,value in (args.items()):
        if key in ['in','query']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])

    print("Running ROCS")
    run_rocs(in_file = args['in'], query = args['query'], mpi_np = mpi_np)

elif args['from'] == 'basic':
    for key,value in (args.items()):
        if key in ['in','from','query']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])
    
    run_filter(in_file = args['in'], out_file = out_filename_map['basic'], filter = 'basic')
    sleep(1)
    move_files_to(dirname="basic_filter")
    print("Running the {} filter".format('pains'))
    sleep(1)
    in_file = get_path(dirname="basic_filter", file = out_filename_map['basic'])
    run_filter(in_file = in_file, out_file = out_filename_map['pains'], filter = 'pains')
    move_files_to(dirname="pains_filter")
    in_file = get_path(dirname="pains_filter", file = out_filename_map['pains'])
    print("Generating conformers")
    run_oeomega(in_file=in_file, out_file = out_filename_map['oeomega'] ,mpi_np = mpi_np)
    move_files_to(dirname="oeomega")
    sleep(1)
    print("Running ROCS")
    in_file = get_path(dirname="oeomega", file = out_filename_map['oeomega'])
    run_rocs(in_file = in_file, query = args['query'], mpi_np = mpi_np)

elif args['from'] in ['pains','blockbuster']:
    for key,value in (args.items()):
        if key in ['in','from','query']:
            check_file(key.lower(), str(value))
    
    mpi_np = assign_mpi_np(args['mpi_np'])

    if args['filter'] not in ['pains','blockbuster']:
        print("Filter option is not defined. Please use -filter pains/blockbuster")
        sys.exit(1)
    else: 
        filter_type = args['filter']

    print("Running the {} filter".format(filter_type))
    run_filter(in_file = args['in'], out_file = out_filename_map[filter_type], filter = filter_type)
    sleep(1)
    dirname = filter_type + "_" + "filter"
    move_files_to(dirname=dirname)
    in_file = get_path(dirname=dirname, file = out_filename_map[filter_type])
    print("Generating conformers")
    run_oeomega(in_file=in_file, out_file = out_filename_map['oeomega'] ,mpi_np = mpi_np)
    move_files_to(dirname="oeomega")
    sleep(1)
    print("Running ROCS")
    in_file = get_path(dirname="oeomega", file = out_filename_map['oeomega'])
    run_rocs(in_file = in_file, query = args['query'], mpi_np = mpi_np)

elif args['from'] == 'oeomega':
    for key,value in (args.items()):
        if key in ['in','query']:
            check_file(key.lower(), str(value))

    mpi_np = assign_mpi_np(args['mpi_np'])

    print("Generating conformers")
    run_oeomega(in_file=args['in'], out_file = out_filename_map['oeomega'] ,mpi_np = mpi_np)
    move_files_to(dirname="oeomega")
    sleep(1)
    print("Running ROCS")
    in_file = get_path(dirname="oeomega", file = out_filename_map['oeomega'])
    run_rocs(in_file = in_file, query = args['query'], mpi_np = mpi_np)

elif args['from'] in ['rocs','all']:
    for key,value in (args.items()):
        if key in ['in','query']:
            check_file(key.lower(), str(value))
    
    mpi_np = assign_mpi_np(args['mpi_np'])
    
    print("Running ROCS")
    run_rocs(in_file = args['in'], query = args['query'], mpi_np = mpi_np)

else:
    print("Exiting. Nothing to do. -upto/-only/-from argument not provided")
