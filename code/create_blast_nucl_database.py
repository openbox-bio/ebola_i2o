#!/usr/bin/env python3
'''
A program to create or update a local BLAST nucleotide database.
Be sure to create the environmental variable file, .env, for each database before you run this program.
Usage: create_blast_nucl_database.py [-h] -e ENV -t {create,update}
                                [-d {mdat,pdat,edat}] [-r RELDATE]
optional arguments:
  -h, --help            show this help message and exit
  -e ENV, --env ENV     The environmental variable file lists the key
                        arguments to run program.
  -t {create,update}, --task {create,update}
                        create - creates a new blast database. update -
                        updates an existing blast database; it requires the
                        datetype and reldate options to be set.
  -d {mdat,pdat,edat}, --datetype {mdat,pdat,edat}
                        Type of date used to limit a search. The allowed
                        values vary between Entrez databases, but common
                        values are:mdat (modification date), pdat (publication
                        date) and edat (Entrez date).
  -r RELDATE, --reldate RELDATE
                        When reldate is set to an integer n, the search
                        returns only those items that have a date specified by
                        datetype within the last n days.
'''

from dotenv import load_dotenv
from pathlib import Path
import os
from Bio import Entrez
from collections import defaultdict
from datetime import datetime
import re
import subprocess
import psutil
import argparse
import sys
import time

def sleep_while_BLAST_is_running():
    '''
    Monitor running processes.
    If a BLAST job is running, sleep for 20s and re-sample.
    '''
    while True:
        r = re.compile("blastn|megablast")
        proc_name_list = []
        for proc in psutil.process_iter():
            proc_name_list.append(proc.name())
        if any([r.match(proc) for proc in proc_name_list]):
            time.sleep(20)
            continue
        else:
            return

def create_db(**kwargs):
    '''
    Create a local BLAST database.
    '''
    #Query Entrez. Store returned results in 'record'.
    database = kwargs['database']
    query = kwargs['query']
    log_file = kwargs['log_file']
    handle = Entrez.esearch(db="nucleotide", term=query, idtype="acc", usehistory="y")
    record = Entrez.read(handle)
    count = record['Count']
    query_key = record['QueryKey']
    web_env = record["WebEnv"]
    handle.close()

    #Use Efetch to fetch the sequences from records identified in Entrez search.
    log_read_handle = open(log_file, 'r') #open the log file
    current_log_file = log_read_handle.read()
    log_read_handle.close()
    log_write_handle = open(log_file, 'w')

    batch_size = 500
    sequence_count = int(count)
    now = datetime.now()
    year_month_date = now.strftime("%Y_%m_%d")
    out_handle = open(database, "w")
    for start in range(0, sequence_count, batch_size):
        end = min(sequence_count, start + batch_size)
        number_of_attempts = 1
        while number_of_attempts < 4:
            try:
                fetch_handle = Entrez.efetch(
                    db="nucleotide",
                    rettype="fasta",
                    retmode="text",
                    retstart=start,
                    retmax=batch_size,
                    webenv=web_env,
                    query_key=query_key,
                    idtype="acc",
                )
                data = fetch_handle.read()
                fetch_handle.close()
            except (Exception) as e:
                log_write_handle.write('number of attempts: {num_attempts}, {error_msg}.\n'.format(num_attempts = number_of_attempts, error_msg = e))
                number_of_attempts += 1
                time.sleep(5)
                continue
            else:
                out_handle.write(data)
                time.sleep(5)
                break
    out_handle.close()

    # Process downloaded sequences:
    # Convert to oneline FASTA.
    # Remove sequences with badly formatted deflines,
    # with non-ATGCN bases and with error messages.
    # Cleaned up sequences are stored in the original file.
    # Total number of clean sequences downloaded is stored in LOG_FILE.
    sequence_list_dict = defaultdict(list)
    sequence_read_handle = open(database, "r")
    file_lines = [line.strip() for line in sequence_read_handle.readlines()]
    key = ''
    for line in file_lines:
        if line.startswith(">", 0):
            key = line
            continue
        sequence_list_dict[key].append(line)
    sequence_read_handle.close()
    sequence_dict = {k:"".join(sequence_list_dict[k]) for k in sequence_list_dict.keys()}
    clean_sequence_count = 0
    sequence_write_handle = open(database, "w")
    for key in sequence_dict.keys():
        if re.search(r'>.*>', key):
            #del sequence_dict[key]
            continue
        if re.search(r'xml|ESEARCH|ERROR', key, flags=re.IGNORECASE):
            #del sequence_dict[key]
            continue
        if re.search(r'[^ATGCN]', sequence_dict[key], flags=re.IGNORECASE):
            #del sequence_dict[key]
            continue
        sequence_write_handle.write(key + '\n' + sequence_dict[key] + '\n')
        clean_sequence_count += 1
    sequence_write_handle.close()

    #log_read_handle = open(log_file, 'r')
    #log_file_contents= log_read_handle.read()
    #log_read_handle.close()
    #log_write_handle = open(log_file, 'w')
    final_sequence_count = len(sequence_dict.keys())
    log_write_handle.write('{date}: {file} created. {count} nucleotide sequences have been downloaded from NCBI.\n'.format(date = year_month_date, file = database, count = clean_sequence_count))
    log_write_handle.close()

    log_write_handle = open(log_file, 'a')
    log_write_handle.write(current_log_file)
    log_write_handle.close()

    #Monitor running processes. If a BLAST job is running, sleep for 20s and re-sample.
    #If no BLAST job running then create the BLAST database using makeblastdb.
    sleep_while_BLAST_is_running()

    # Run makeblastdb on the downloaded sequences as a subprocess.
    # Return exit status of subprocess.
    makeblastdb_cli = ['makeblastdb', '-in', database, '-dbtype', 'nucl', '-parse_seqids']
    run_makeblastdb = subprocess.call(makeblastdb_cli, stdout = subprocess.PIPE)
    return(run_makeblastdb)

def update_db(**kwargs):
    '''
    Update a local BLAST database.
    '''
    #Query Entrez. Store returned results in 'record'.
    database = kwargs['database']
    query = kwargs['query']
    log_file = kwargs['log_file']
    weekly_download_file = kwargs['weekly_download_file']
    datetype = kwargs['datetype']
    reldate = kwargs['reldate']
    handle = Entrez.esearch(db="nucleotide", term=query, idtype="acc", usehistory="y", datetype=datetype, reldate=reldate)
    record = Entrez.read(handle)
    count = record['Count']
    query_key = record['QueryKey']
    web_env = record["WebEnv"]
    handle.close()

    sequence_count = int(count)
    if sequence_count > 0:
        #Use Efetch to fetch the sequences from records identified in Entrez search.
        log_read_handle = open(LOG_FILE, 'r')
        current_log_file = log_read_handle.read()
        log_read_handle.close()
        log_write_handle = open(log_file, 'w')

        batch_size = 500
        sequence_count = int(count)
        now = datetime.now()
        year_month_date = now.strftime("%Y_%m_%d")
        weekly_download_file = year_month_date + weekly_download_file
        out_handle = open(weekly_download_file, "w")
        for start in range(0, sequence_count, batch_size):
            end = min(sequence_count, start + batch_size)
            number_of_attempts = 1
            while number_of_attempts < 4:
                try:
                    fetch_handle = Entrez.efetch(
                        db="nucleotide",
                        rettype="fasta",
                        retmode="text",
                        retstart=start,
                        retmax=batch_size,
                        webenv=web_env,
                        query_key=query_key,
                        idtype="acc",
                    )
                    data = fetch_handle.read()
                    fetch_handle.close()
                except (Exception) as e:
                    log_write_handle.write('number of attempts: {num_attempts}, {error_msg}.\n'.format(num_attempts = number_of_attempts, error_msg = e))
                    number_of_attempts += 1
                    time.sleep(5)
                    continue
                else:
                    out_handle.write(data)
                    time.sleep(5)
                    break
        out_handle.close()

        # Process downloaded sequences:
        # Convert to oneline FASTA.
        # Remove sequences with badly formatted deflines,
        # with non-ATGCN bases and error messages.
        # Cleaned up sequences are stored in the original file, .
        # Total number of clean sequences downloaded is stored in LOG_FILE.
        sequence_list_dict = defaultdict(list)
        sequence_read_handle = open(weekly_download_file, "r")
        file_lines = [line.strip() for line in sequence_read_handle.readlines()]
        key = ''
        for line in file_lines:
            if line.startswith(">", 0):
                key = line
                continue
            sequence_list_dict[key].append(line)
        sequence_read_handle.close()
        sequence_dict = {k:"".join(sequence_list_dict[k]) for k in sequence_list_dict.keys()}
        clean_sequence_count = 0
        sequence_write_handle = open(weekly_download_file, "w")
        for key in sequence_dict.keys():
            if re.search(r'>.*>', key):
                #del sequence_dict[key]
                continue
            if re.search(r'xml|ESEARCH|ERROR', key, flags=re.IGNORECASE):
                #del sequence_dict[key]
                continue
            if re.search(r'[^ATGCN]', sequence_dict[key], flags=re.IGNORECASE):
                #del sequence_dict[key]
                continue
            sequence_write_handle.write(key + '\n' + sequence_dict[key] + '\n')
            clean_sequence_count += 1
        sequence_write_handle.close()
        #log_read_handle = open(LOG_FILE, 'r')
        #log_file = log_read_handle.read()
        log_write_handle = open(log_file, 'w')
        final_sequence_count = len(sequence_dict.keys())
        log_write_handle.write('{date}: {file} updated. {count} nucleotide sequences have been downloaded from NCBI.\n'.format(file = database, date = year_month_date, count = clean_sequence_count))
        log_write_handle.close()
        log_write_handle = open(log_file, 'a')
        log_write_handle.write(current_log_file)
        log_write_handle.close()

        #Append the cleaned-up downloaded sequences to the master database file.
        database_append_handle = open(database, "a")
        sequence_read_handle = open(weekly_download_file, "r")
        for file_line in sequence_read_handle:
            database_append_handle.write(file_line)
        sequence_read_handle.close()
        database_append_handle.close()
        #Monitor running processes. If a BLAST job is running, sleep for 20s and re-sample.
        sleep_while_BLAST_is_running()

        # Run makeblastdb on the downloaded sequences as a subprocess.
        # Return exit status of subprocess.
        makeblastdb_cli = ['makeblastdb', '-in', database, '-dbtype', 'nucl', '-parse_seqids']
        run_makeblastdb = subprocess.call(makeblastdb_cli, stdout = subprocess.PIPE)
        return(run_makeblastdb)
    else:
        log_read_handle = open(LOG_FILE, 'r')
        log_file = log_read_handle.read()
        log_write_handle = open(LOG_FILE, 'w')
        log_write_handle.write('{date}: {file} not updated. {count} nucleotide sequences have been released in the last {reldate} days from NCBI.\n'.format(file = database, date = year_month_date, count = sequence_count, reldate = reldate))
        log_write_handle.close()
        log_write_handle = open(LOG_FILE, 'a')
        log_write_handle.write(log_file)
        log_write_handle.close()
        return 0


def main():
    #a dictionary to store user input as key and corresponding function to run as a value.
    function_map = {
    'create': create_db,
    'update': update_db
    }
    email_message = "" #initialize a string to store message to be sent to user via email.
    cli_parser = argparse.ArgumentParser(description = 'A program to create or update a local BLAST nucleotide database.',
                                         epilog = 'Contact openboxbio@gmail.com for questions.')
    cli_parser.add_argument('-e', '--env', required = True, help = 'Relative or absolute path to the environmental variable file lists the key arguments to run program.')
    cli_parser.add_argument('-t', '--task', required = True, choices = function_map.keys(), help = 'create - creates a new blast database.'+'\n'+'update - updates an existing blast database; it requires the datetype and reldate options to be set.')
    cli_parser.add_argument('-d', '--datetype', choices=['mdat', 'pdat', 'edat'], help = 'Type of date used to limit a search. The allowed values vary between Entrez databases, but common values are:mdat (modification date), pdat (publication date) and edat (Entrez date).')
    cli_parser.add_argument('-r', '--reldate', type = int, help = 'When reldate is set to an integer n, the search returns only those items that have a date specified by datetype within the last n days.')

    #Read and store cli arguments.
    cli_args_dict = vars(cli_parser.parse_args())
    env_file = Path(cli_args_dict['env'])
    datetype = cli_args_dict['datetype']
    reldate = cli_args_dict['reldate']
    task = cli_args_dict['task']

    # Check if enviromnent variable file exists.
    # If it does, read and store environment variables.
    # If not, print error message and exit.
    try:
        env_file_path = env_file.resolve(strict = True)
    except FileNotFoundError:
        print("Exiting program." + "\n"+ "Environment file does not exist." + "\n"+ "Please enter the name of a valid environment file." )
        email_message += "Invalid environment variable file."
        sys.exit()
    else:
        load_dotenv(dotenv_path=env_file_path)
        NCBI_API_KEY = os.getenv("NCBI_API_KEY")
        EMAIL = os.getenv("EMAIL")
        QUERY = os.getenv("QUERY")
        LOG_FILE = os.getenv("LOG")
        DB = os.getenv("DB")
        WEEKLY_DOWNLOAD_FILE = os.getenv("WEEKLY_DOWNLOAD_FILE")

    #Establish connection with Entrez with API key and email.
    Entrez.api_key = NCBI_API_KEY
    Entrez.email = EMAIL

    # Run a function based on user input.
    # Store exit status of function in task_status.
    # Update email message.
    task_status = function_map[task](query=QUERY,
                                    database=DB,
                                    log_file=LOG_FILE,
                                    weekly_download_file=WEEKLY_DOWNLOAD_FILE,
                                    datetype=datetype,
                                    reldate=reldate)
    email_message += "exit status of your task- "+task+" database is "+str(task_status)+"."

if __name__ == '__main__':
    main()
