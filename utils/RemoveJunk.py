# coding: utf-8

import re


# configuration

#User defined spliters to split words from logs
re_word_spliter_conf = r':| |\n|\.|,|;|\?|=|\]|\[|\t|\(|\)|/'

re_date = '2\d\d\d-[0-1][1-9]-[0-3][0-9]\s*?[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.\d\d\d\s*?'
re_tid = '\[TID#\d*?\]'
re_log_info = 'Info'
re_log_debug = 'Debug'
re_log_error = 'Error'
re_digits = '\d+'
re_hex = '\b[A-F0-9]{2}\b'
re_ascii = '\b.{16}\b'

#Configuration of stop words and keep words.
#The word will be kept if it matches any of the keep words.
re_keep_words_conf = [re_log_error]

#stop words
re_stop_words_conf = [re_date, re_tid, re_log_info, re_log_debug, re_digits, re_hex, re_ascii, '\bkey\b', '\bvalue\b']

#column names to clean
columns_conf = ['spu', 'glc']
#The lines which match this format are considered only.
re_line_format_conf = '2\d\d\d-[0-1][1-9]-[0-3][0-9]\s*?[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.\d\d\d\s*?\[TID#\d*?\]\
\s*?\[(.*?)\]\s(.*)'

def get_clean_words_each_line(log, word_spliter,re_keep_words, re_stop_words):
    result = ''
    words = re.split(word_spliter, log)
    for word in words:
        keep_found = 0
        stop_not_found = 1
        #Add keep words
        for re_keep_word in re_keep_words:
            m = re.search(re_keep_word, word)
            if m != None:
                keep_found = 1
                break
        if keep_found:
            result += (word + ' ')
            continue
        #Remove stop words
        for re_stop_word in re_stop_words:
            m = re.search(re_stop_word, word)
            if m != None:
                stop_not_found = 0
                break
        if stop_not_found:
            result += (word + ' ')
    return result

def get_clean_words(log, re_line_format, word_spliter,re_keep_words, re_stop_words):
    result = ''
    all_lines = re.split('\n', log)
    for each_line in all_lines:
        m = re.search(re_line_format, each_line)
        if m == None:
            continue
        result += get_clean_words_each_line(each_line, word_spliter,re_keep_words, re_stop_words) + '\n'
    return result


import types
def remove_junk(df, columns, re_line_format, re_word_spliter,re_keep_words, re_stop_words):
    new_df = df
    for column in columns:
        line = 0
        df_column = new_df[column]
        for log in df_column:
            if type(log) == types.StringType:
                new_log = get_clean_words(log, re_line_format, re_word_spliter,re_keep_words, re_stop_words)
                new_df[column][line] = new_log
            else:
                print column + '[' + str(line) + ']' + ' is not string!'
            line = line + 1
    return new_df


# Testing

log_test_01 = '2017-03-23 06:08:32.460 [TID#5418] \
[Error] [LE1F2870323060832021][SessionID: 274726934]\
startConcurrentSession: start concurrent session success. \
concurrent key: value:hsscache5EF5D868E97147959B71273EC3CDA6FA, \
dest id: D, set id type: 6, set id: 10.68.101.20, \
concurrent key: value:hsscache5EF5D868E97147959B71273EC3CDA6FA, \
session interval: 33, utc finish=1490249340, now: 1490249312'


log_test_02 = '2017-03-23 06:08:50.683 [TID#5420]\
[Debug] UpEventProcessor::suplDecode\n\
HEX		                                                ASCII\n\
00 A8 02 00 02 C0 00 40 08 C4 18 00 00 07 C7 FC 		.......@........\n\
41 80 00 59 0B E3 AD 71 07 3E 33 06 8D 32 42 02 		A..Y...q.>3..2B.\n\
02 19 00 10 5A 00 AF A5 10 82 00 69 F3 60 CC A1 		....Z......i.`..\n\
43 2B 88 00 80 05 00 42 15 C6 06 62 23 3A AB B0 		C+.....B...b#:..\n\
60 00 A1 80 04 84 00 20 00 7D 07 18 19 88 8C EA 		`...... .}......\n\
AE C1 C0 02 9A 00 12 10 00 80 01 F4 1C 60 66 22 		.............`f"\n\
33 AA BB 08 00 0A B8 00 48 40 02 00 07 D0 71 81 		3.......H@....q.\n\
98 88 CE AA EC 24 00 2C 20 01 21 00 08 00 1F 41 		.....$., .!....A\n\
C6 06 62 23 3A AB B1 00 00 B5 80 04 84 00 20 00 		..b#:......... .\n\
7D 07 18 19 88 8C EA AE C4 40 02 EA 00 12 10 00 		}........@......\n\
80 01 F4 00 08 08 00 00                         		.......'


print get_clean_words(log_test_01, re_line_format_conf, re_word_spliter_conf, re_keep_words_conf, re_stop_words_conf)

print get_clean_words(log_test_02, re_line_format_conf, re_word_spliter_conf, re_keep_words_conf, re_stop_words_conf)


import pandas as pd
import re
import os.path
from glob import glob
from tensorflow.python.platform import gfile

def get_file_list(log_dir):
    extensions = ['log','LOG']
    if not gfile.Exists(log_dir):
        print("Log directory '" + log_dir + "' not found.")
        return None
    case_list = {}
    sub_dirs = [x[0] for x in gfile.Walk(log_dir)]
    # The root directory comes first, so skip it.
    is_root_dir = True
    for sub_dir in sub_dirs:
        file_list = []
        if is_root_dir:
            is_root_dir = False
            continue
        dir_name = os.path.basename(sub_dir)
        if dir_name == log_dir:
           continue
        #print("Looking for logs in '" + dir_name + "'")
        for extension in extensions:
            file_glob = os.path.join(log_dir, dir_name, '*.' + extension + "*")
            file_list.extend(gfile.Glob(file_glob))
        if not file_list:
            print('No files found')
            continue
        case_list[dir_name]= {
            'list' : file_list
            }
    return case_list

def log2_dataframe(case_list):
    proc_count = len(case_list.keys())
    if proc_count == 0:
        print ('No process log found.')
        return -1
    proc_list = ['glc','spu']
    log_df = pd.DataFrame(columns=proc_list)
    log_proc = pd.DataFrame(columns=['case'])
    count = 0
    for dir_name, file_lists in case_list.items():
        file_list = file_lists['list']
        for file in file_list:
            base = os.path.basename(file)
            proc_name = os.path.splitext(base)[0]
            print proc_name
            name = re.search(r'(\w+)',proc_name)
            if name is not None:
                proc = name.group(1)
                if proc in proc_list:
                    #print proc
                    with open(file) as f:
                        each_log = ''
                        for each_line in f:
                            each_log = each_log + each_line
                            #print each_log
                        log_df.set_value(count, proc, each_log)
                        log_proc.loc[count] = [dir_name]
        count = count + 1
    log_df['case_id'] = log_proc.case
    print ('Number of logs read into data frame: %d' %(len(log_proc.index)))
    print ('The name of the data frame %s' %(log_df.shape,))
    print log_df.columns
    return log_df
    '''
        with open (file) as f:
            each_log = ''
            log_dict = {}
            for each_line in f:
                each_log = each_log + each_line
            base = os.path.basename(file)
            procid = os.path.splitext(base)[0]
            log_df.loc[count] = [each_log, procid]
            count = count+1
    '''
    #print ('Number of logs read into data frame: %d' %(len(log_df.index)))
    #return log_df


case_list = get_file_list('data/')
data_frame = log2_dataframe(case_list)
print data_frame['spu'][1]


new_df = remove_junk(data_frame, columns_conf, re_line_format_conf, re_word_spliter_conf,re_keep_words_conf, re_stop_words_conf)


new_df
data_frame




