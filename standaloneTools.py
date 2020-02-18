# -*- coding: utf-8 -*-
import os, time, random, smtplib, shutil
from random import *
import inspect
from time import sleep
import random
import codecs
import sys
import unicodedata
import logging
import ftfy
from datetime import date
import calendar
import datetime
from django.utils import timezone

import os.path
import socket
from datetime import datetime


def get_time_string():
    #named_tuple = time.localtime() # get struct_time
    now = timezone.now()
    #now = datetime.datetime.utcnow().replace(tzinfo=utc)
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", named_tuple))
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", now))
    return (now)

# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

def get_list_from_file(filepath):
    listFromFile = []
    listFromFile.clear()
    working = True
    #with open(path, 'rb') as f:
        #text = f.read()
    with open(str(filepath), 'r', encoding='utf8') as fh:
        while working == True:
            for line in fh:
                line = ftfy.fix_encoding(str(line))
                #eventlog('get_list_from_file: ' + str(line.rstrip()))
                listFromFile.append(line.rstrip())
            working = False
            
    #fh.close()
    return listFromFile

def shuffle_list(inputlist):
    for i in range(len(inputlist)):
        swap = randint(0,len(inputlist)-1)
        temp = inputlist[swap]
        inputlist[swap] = inputlist[i]
        inputlist[i] = temp
    return inputlist

#@pysnooper.snoop('/home/gordon/p3env/alice/alice/spiders/auto_cleared_history/get_list_files_folders_in_path.history', prefix='get_list_files_folders_in_path', depth=1)
def get_list_files_folders_in_path(path):
    list_fp = []
    list_dp = []
    b_fp = False
    b_dp = False
    for i in os.scandir(path):
        if i.is_file():
            #eventlog('File: ' + i.path)
            list_fp.append(i.path)
            b_fp = True
        elif i.is_dir():
            #eventlog('Folder: ' + i.path)
            list_dp.append(i.path + '/')
            b_dp = True
    return b_dp, b_fp, list_dp, list_fp


def get_ascii_art():
    b_dp, b_fp, list_dp, list_fp = get_list_files_folders_in_path('stringkeeper/landing_page_ascii_art')
    list_of_ascii_art_files = list_fp
    shuffled_art_files = shuffle_list(list_of_ascii_art_files)
    chosen_art_file = shuffled_art_files[0]
    list_of_ascii_art_strings = get_list_from_file(chosen_art_file)
    art_string = '\n'
    for line in list_of_ascii_art_strings:
        art_string += str(line)
        art_string += str('\n')
    return str(art_string)



# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
print('PROJECT_ROOT:', PROJECT_ROOT)
BASE_DIR = os.path.dirname(PROJECT_ROOT)
print('BASE_DIR:', BASE_DIR)

filepath_hostname = str(socket.gethostname())
final_filepath_hostname = ''
for ch in filepath_hostname:
    if ch != '.':
        final_filepath_hostname += str(ch)

# log_directory_path = str(BASE_DIR + '/logs/' + str(datetime.today().strftime('%Y-%m-%d')) + '/' + final_filepath_hostname)

# if not os.path.exists(log_directory_path):
#     os.makedirs(log_directory_path)

def get_list_files_folders_in_path(path):
    list_fp = []
    list_dp = []
    b_fp = False
    b_dp = False
    for i in os.scandir(path):
        if i.is_file():
            #eventlog('File: ' + i.path)
            list_fp.append(i.path)
            b_fp = True
        elif i.is_dir():
            #eventlog('Folder: ' + i.path)
            list_dp.append(i.path + '/')
            b_dp = True
    return b_dp, b_fp, list_dp, list_fp

log_files = []

s = socket.gethostname()

# s = '321rfdslso..we24'

LOGGING_FILEPATH = str(os.path.join(PROJECT_ROOT, str('remotedebug_' + str(''.join(filter(str.isalpha, s))) + '.log')))
# LOGGING_FILEPATH = getattr(settings, 'LOGGING_FILEPATH', False)
def eventlog(logstring):
    previous_frame = inspect.currentframe().f_back
    (filename, line_number, 
     function_name, lines, index) = inspect.getframeinfo(previous_frame)

    del previous_frame  # drop the reference to the stack frame to avoid reference cycles
    caller_filepath = filename

    caller_filepath = os.path.abspath(caller_filepath)
    caller_filename = ''
    for ch in caller_filepath:
        if not ch.isalnum():
            caller_filename += str('-')
        else:
            caller_filename += str(ch)
    if len(caller_filename) > 25:
        caller_filename = caller_filename[-25:]
    caller_filename += '_log.txt'
    debug_line_number = line_number
    if line_number < 10:
        debug_line_number = str('0000' + str(line_number))        
    elif line_number < 100:
        debug_line_number = str('000' + str(line_number))
    elif line_number < 1000:
        debug_line_number = str('00' + str(line_number))
    elif line_number < 10000:
        debug_line_number = str('0' + str(line_number))

    print('|==| ' + str(debug_line_number) + ' |==| ' + str(filename)[-25:] + ' | ' + str(function_name) + ' | ' + str(logstring) + ' |==|')


    f = open(LOGGING_FILEPATH, "a+")
    f.write('|==| ' + str(debug_line_number) + ' |==| ' + str(filename)[-25:] + ' | ' + str(function_name) + ' | ' + str(logstring) + ' |==|')
    f.write('\n')
    f.close()
    if os.path.getsize(LOGGING_FILEPATH) > 1000000:
        f = open(LOGGING_FILEPATH, "w")
        f.write('')
        f.close()        




def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ''