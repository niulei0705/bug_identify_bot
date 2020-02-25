#
#
# Nokia Copyright...
############################################################
import pandas as pd
import re
import os.path
from glob import glob
from tensorflow.python.platform import gfile
from read_config import ConfigLoader
class DFCreator():
    def get_file_list(self, log_dir, date):
        extensions = ['log','LOG']
        if not gfile.Exists(log_dir):
            print("Log directory '" + log_dir + "' not found.")
            return None
        case_list = {}
        if (date != 'all'):
            log_dir += date
        sub_dirs = [x[0] for x in gfile.Walk(log_dir)]
        # The root directory comes first, so skip it.
        file_list = []
        is_root_dir = True
        for sub_dir in sub_dirs:
            if is_root_dir:
                is_root_dir = False
                continue
            dir_name = os.path.basename(sub_dir)
            log_dir = os.path.dirname(sub_dir)
            if dir_name == log_dir:
               continue
            #print("Looking for logs in '" + dir_name + "'")
            for extension in extensions:
                file_glob = os.path.join(log_dir, dir_name, '*.' + extension + "*")
                file_list.extend(gfile.Glob(file_glob))
            if not file_list:
               # print('No files found')
                continue
            '''
            case_list[dir_name] = {
                'list' : file_list
                }
            '''
        return file_list
    def log2_dataframe(self, file_list, process_list):
        proc_count = len(file_list)
        if proc_count == 0:
            print ('No process log found at')
            return -1
        proc_list = process_list.split(',')
        proc_list.insert(0,'case')
        proc_list.insert(1,'date')
        log_df = pd.DataFrame(columns=proc_list)
        log_proc = pd.DataFrame(columns=['case','date'])
        count = 0
        for file in file_list:
            base = os.path.basename(file)
            dirname =  os.path.dirname(file)
            base1 = re.search(r'(.*)\/(.*)\/(.*)', dirname).group(3)
            base2 = re.search(r'(.*)\/(.*)\/(.*)', dirname).group(2)
            proc_name = os.path.splitext(base)[0]
            name = re.search(r'(\w+)',proc_name)
            if name is not None:
                proc = name.group(1)
                if proc in proc_list:
                    with open(file) as f:
                        each_log = ''
                        for each_line in f:
                            each_log = each_log + each_line
                        log_df.set_value(count, proc, each_log)
            log_df.set_value(count, 'date', base2)
            log_df.set_value(count, 'case', base1)
            count = count + 1
        print ('Number of logs read into data frame: %d' %(len(log_proc.index)))
       # print ('The name of the data frame %s' %(log_df.shape,))
        print log_df.columns

        log_df.set_index(['case','date'], inplace=True)
        return log_df
        #print ('Number of logs read into data frame: %d' %(len(log_df.index)))

    '''
    This data frame get the process names and associated files names and create a separate dataframe for each
    process.
    '''
    def proc2_dataframe(self, file_list, process_names):
        proc_count = len(file_list)
        if proc_count == 0:
            print ('No process log found at')
            return -1
        df_dic = {} # Holds alls df to be returned
        proc_name = process_names.split(',')
        for each_proc in proc_name:
            proc_list = each_proc.split(':')[1].split(';')
            #proc_list = process_list.split(',')
            proc_list.insert(0,'case')
            proc_list.insert(1,'date')
            log_df = pd.DataFrame(columns=proc_list)
            log_proc = pd.DataFrame(columns=['case','date'])
            count = 0
            for file in file_list:
                base = os.path.basename(file)
                dirname = os.path.dirname(file)
                base1 = re.search(r'(.*)\/(.*)\/(.*)', dirname).group(3)
                base2 = re.search(r'(.*)\/(.*)\/(.*)', dirname).group(2)
                proc_name = os.path.splitext(base)[0]
                name = re.search(r'(\w+)',proc_name)
                if name is not None:
                    proc = name.group(1)
                    if proc in proc_list:
                        with open(file) as f:
                            each_log = ''
                            for each_line in f:
                                each_log = each_log + each_line
                            log_df.set_value(count, proc, each_log)
                log_df.set_value(count, 'date', base2)
                log_df.set_value(count, 'case', base1)
                count = count + 1
            #print ('Number of logs read into data frame: %d' %(len(log_df.index)))
           # print ('The name of the data frame %s' %(log_df.shape,))
            #print log_df.columns
            log_df.set_index(['case','date'], inplace=True)
            df_dic[each_proc.split(':')[0]] = log_df
        return df_dic
        #print ('Number of logs read into data frame: %d' %(len(log_df.index)))
#loader = ConfigLoader()
#config = loader.load_config('../config/product_config.json')
#df_creator = DFCreator()
#file_list = df_creator.get_file_list('../logs/')
#df_list = df_creator.proc2_dataframe(file_list, config.get_processnames())


