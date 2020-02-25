import re
import types
import hashlib

class text_cleaner(object):
    RE_LINE_FORMAT = '2\d\d\d-[0-1][1-9]-[0-3][0-9]\s*?[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.\d\d\d\s*?\[TID#\d*?\]\
\s*?\[(.*?)\]\s(.*)'

#spliters to split words from logs
    WORD_SPLITER_CONF = r':| |\n|\.|,|;|\?|=|\]|\[|\t|\(|\)|/|-|>|<'

    RE_DATE = '2\d\d\d-[0-1][1-9]-[0-3][0-9]\s*?[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.\d\d\d'
    RE_LOG_TAG_INFO = 'Info'
    RE_LOG_TAG_DEBUG = 'Debug'
    RE_LOG_TAG_ERROR = 'Error'
    RE_DIGITS = '.*?\d+.*?'
    RE_HEX = '\b[a-fA-F0-9]{2}\b'
    RE_ASCII = '\b.{16}\b'
        #an exception of the 'ASCII'
    RE_WORDS_16CS = '[a-zA-Z]]{16}'
    line_format = RE_LINE_FORMAT
    word_spliter = WORD_SPLITER_CONF
    stop_words = [RE_LOG_TAG_INFO, RE_LOG_TAG_DEBUG, RE_LOG_TAG_ERROR, RE_DIGITS, RE_HEX, RE_ASCII]
    stop_word_exceptions = [RE_WORDS_16CS]

    def configure(self, line_format, word_spliter, stop_words, stop_word_exceptions):
        self.line_format = line_format
        self.word_spliter = word_spliter
        self.stop_words = stop_words
        self.stop_word_exceptions = stop_word_exceptions

    def get_clean_words_each_line(self, log):
        result = ''
        words = re.split(self.word_spliter, log)
        for word in words:
            stop_not_found = True
            #Remove stop words
            for re_stop_word in self.stop_words:
                m = re.match(re_stop_word, word)
                if m != None:
                    stop_not_found = False
                    break
            if stop_not_found:
                result += (word + ' ')
            else:
                #Exclude exceptions from stop words.
                if self.stop_word_exceptions != None:
                    for sw_exception in self.stop_word_exceptions:
                        m = re.match(sw_exception, word)
                        if m != None:
                            result += (word + ' ')
                            break
        return result

    def get_clean_words(self, log):
        result = ''
        all_lines = re.split('\n', log)
        for each_line in all_lines:
            if(self.line_format != None):
                m = re.match(self.line_format, each_line)
                if m == None:
                    continue
            result += self.get_clean_words_each_line(each_line) + '\n'
        return result

    @classmethod
    def gen_md5_series(cls, log):
        result = []
        md5_set = set()
        line_num = 0
        all_lines = re.split('\n', log)
        for each_line in all_lines:
            if(cls.line_format != None):
                m = re.match(cls.line_format, each_line)
                if m == None:
                    continue
            clean_words = cls.get_clean_words_each_line(each_line)
            md5code = hashlib.md5()
            md5code.update(clean_words)
            result.append(md5code.hexdigest())
            md5_set.add(md5code.hexdigest())
            line_num += 1

        #print ('md5 set element number is ' + str(len(md5_set)) + '. line number is ' + str(line_num))

        return (result, len(md5_set))

    def clean_data_frame(self, df, columns):
        new_df = df
        for column in columns:
            line = 0
            df_column = new_df[column]
            for log in df_column:
                if type(log) == types.StringType:
                    new_log = self.get_clean_words(log)
                    md5_series = self.gen_md5_series(log)
                    #print (md5_series)
                    new_df[column][line] = (new_log, md5_series)
                line = line + 1
        return new_df


