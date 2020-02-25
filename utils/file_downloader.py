import logging
from logging import config
import paramiko
import os
import sys
from read_config import *
from datetime import datetime



class FileDownloader(object):
    ip = None
    port = None
    user = None
    password = None
    local_file_path = None
    remote_file_path = None
    abs_file_list = []
    ssh = None
    logger = None
    path_prefix =None


    def __init__(self, config, timestamp):
        logging.config.fileConfig('/var/opt/bnb_bot/config/logging.conf')
        self.logger = logging.getLogger('fileLogger')
        self.ip = config.get_serverip()
        self.port = config.get_serverport()
        self.user = config.get_username()
        self.password = config.get_password()
        self.remote_file_path = config.get_srcdir()
        self.local_file_path = os.path.join(config.get_dstdir(), timestamp)
        self.path_prefix = config.get_path_prefix()
        self.connect()

    def download(self, case_id=''):
        self.abs_file_list = []
        sftp = self.ssh.open_sftp()
        if (self.path_prefix is not None) & (self.path_prefix != ""):
            case_id = self.path_prefix + case_id
        self.list_remote_file(os.path.join(self.remote_file_path, case_id))
        for remote_file in self.abs_file_list:
            sub_path_name = remote_file[remote_file.index(self.remote_file_path) + len(self.remote_file_path):]
            local_file = self.local_file_path + sub_path_name
            dir_name = os.path.dirname(local_file)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            sftp.get(remote_file, local_file)
            self.logger.info('Download ' + remote_file + ' successfully.')

    def list_remote_file(self, remote_folder):
        sftp = self.ssh.open_sftp()
        file_list = []
        try:
            file_list = sftp.listdir(remote_folder)
        except IOError:
            msg = 'File folder ' + remote_folder + ' is not exist'
            self.logger.error(msg)
            sys.stderr.write(msg + '\n')
            return
        if len(file_list) == 0:
            self.logger.warning('File folder' + remote_folder + ' is empty')
            return
        for file in file_list:
            remote_file = os.path.join(remote_folder, file)
            cmd = 'file ' + remote_file + '|grep directory|wc -l'
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            res = stdout.readline().strip()
            if res == "1":
                self.list_remote_file(remote_file)
            else:
                self.abs_file_list.append(remote_file)



    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, int(self.port), self.user, self.password)
        self.logger.info('Connect to ' + self.ip + ' successfully.')

    def close(self):
        self.ssh.close()
        self.logger.info('Disconnect to ' + self.ip + ' successfully.')

if __name__ == '__main__':
    config = ConfigLoader().load_config('config/product_config.json')
    downloader = FileDownloader(config)
    downloader.download()
    downloader.close()

