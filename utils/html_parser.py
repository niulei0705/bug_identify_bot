from HTMLParser import HTMLParser


class TestReportParser(HTMLParser):

    def __init__(self, tag, attributes):
        HTMLParser.__init__(self)
        self.value_dict = {}
        self.match_tag = tag
        self.attributes_list = attributes
        self.in_table_flag = False
        self.in_th_tag = False
        self.in_td_tag = False
        self.tr_index = 0
        self.timestamp_index = 0
        self.td_index = 0
        self.timestamp = ""

    def handle_starttag(self, tag, attrs):
        if tag == self.match_tag or tag == "table":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable in self.attributes_list and tag == self.match_tag:
                        if self.value_dict.has_key(variable):
                            self.value_dict[variable].append(value)
                        else:
                            self.value_dict[variable] = [value]
                    elif variable == "class" and value == "details" and tag == "table":
                        self.in_table_flag = True
        if tag == "th" and self.in_table_flag:
            self.in_th_tag = True
        if tag == "td" and self.in_table_flag:
            self.in_td_tag = True

    def handle_endtag(self, tag):
        if tag == "table" and self.in_table_flag:
            self.in_table_flag = False
        if tag == "th" and self.in_table_flag:
            self.in_th_tag = False
        if tag == "td" and self.in_table_flag:
            self.in_td_tag = False

    def handle_data(self, data):
        if self.in_th_tag:
            self.tr_index += 1
            if data == "Time Stamp":
                self.timestamp_index = self.tr_index
        if self.in_td_tag:
            self.td_index += 1
            if self.td_index == self.timestamp_index:
                self.timestamp = data

    def get_timestamp(self):
        return self.timestamp

    def get_values(self):
        return self.value_dict

    def parse_from_file(self, file_path):
        file = open(file_path)
        data = file.read()
        self.feed(data)


if __name__ == '__main__':
    parser = TestReportParser('a', ['name'])
    parser.parse_from_file('/mnt/bnb_bot_shared/com/nokia/mals/taf/tests/0_CI155LBSTests-errors.html')
    values = parser.get_timestamp()
    print values

