import sys
import os
sys.path.append(os.getcwd())
from utils.read_config import ConfigLoader
from utils.file_downloader import FileDownloader
from utils.html_parser import TestReportParser
import time

class Controller(object):

    def __init__(self):
        self.config = ConfigLoader().load_config('config/product_config.json')


    def download_logs(self):
        parser = TestReportParser('a', ['name'])
        parser.parse_from_file(self.config.get_logurl())
        case_list = parser.get_values()['name']
        timestamp = parser.get_timestamp()
        timearray = time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        timestamp = time.strftime('%Y%m%d', timearray)
        downloader = FileDownloader(self.config, timestamp)
        for case in case_list:
            if (self.config.get_cr_prefix() is not None) & (self.config.get_cr_prefix() != ''):
                case = case.split(self.config.get_cr_prefix())[-1]
            downloader.download(case)
        downloader.close()

if __name__ == '__main__':
    controller = Controller()
    controller.download_logs()
