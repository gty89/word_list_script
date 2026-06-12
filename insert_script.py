import csv
from configparser import ConfigParser
import requests
from datetime import datetime
from tqdm import tqdm
from itertools import islice

class Word:
    def __init__(self):
        self.word_text = ""
        self.english = ""
        self.chinese = ""
        self.sys_list = ""
        self.ant_list = ""
        self.category_mask = 1
        self.note = ""

CSV_HEADER = [
    "word",
    "mean_en",
    "mean_cn",
    "note",
    "word_category_mask",
    "synonym_words",
    "antonym_words"
]

START_LINE = 900
END_LINE = 903

def initial_word_list(input_file_path, start_line = START_LINE, end_line = END_LINE) -> list[Word]:
    word_list = []
    with open(input_file_path, mode = 'r', encoding = "utf-8-sig") as csvfile:
        reader = csv.reader(csvfile)
        for row in list(islice(reader, start_line, end_line)):
            new_word = Word()
            new_word.word_text = row[0].lower()
            new_word.chinese = row[1]
            word_list.append(new_word)
    return word_list

def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

def fetch_from_mw(word_list: list[Word], dictionary_key, dictionary_url, thesaurus_key, thesaurus_url, timeout = 30, max_word_length = 400):
    if len(word_list) == 0:
        return []
    if len(word_list) > max_word_length:
        word_list = word_list[:max_word_length]
    print("Fetching the word list:")
    failed_word_list = []
    for word in tqdm(word_list):
        response = requests.get(url = dictionary_url + word.word_text, params = {"key": dictionary_key}, timeout = timeout)
        data = response.json()
        if data and isinstance(data[0], dict):
            definitions = data[0].get("shortdef", [])
            word.english = "; ".join(definitions)
        response = requests.get(url = thesaurus_url + word.word_text, params = {"key": thesaurus_key}, timeout = timeout)
        data = response.json()
        if data and isinstance(data[0], dict):
            entry = data[0]
            synonym_words = entry["meta"].get("syns", [])
            if synonym_words is not None and len(synonym_words) > 0:
                word.sys_list = "; ".join(flatten(synonym_words))
            antonym_words = entry["meta"].get("ants", [])
            if antonym_words is not None and len(antonym_words) > 0:
                word.ant_list = "; ".join(flatten(antonym_words))
    if len(failed_word_list) > 0:
        print("Here is the list of failed words: ")
        print(word.word_text for word in failed_word_list)
    return word_list

def create_output_csv(word_list: list[Word], output_file_path_pattern, timestamp_format):
    time_stamp = datetime.now().strftime(timestamp_format)
    file_path_name = output_file_path_pattern.format(time_stamp = time_stamp)
    with open(file_path_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        for word in word_list:
            row = [word.word_text, word.english, word.chinese, word.note, word.category_mask, word.sys_list, word.ant_list]
            writer.writerow(row)
    return file_path_name

def main():
    config = ConfigParser()
    config.read('config.ini')
    dictionary_key = config['api']['dictionary_key']
    dictionary_url = config['api']['mw_dictionary_url']
    thesaurus_key = config['api']['thesaurus_key']
    thesaurus_url = config['api']['mw_thesaurus_url']
    timeout = int(config['api']['timeout'])

    input_file_path = config['file']['input_file_path_name']
    output_file_path_pattern = config['file']['out_put_path_pattern']
    timestamp_format = config['file']['timestamp_format']
    word_list = initial_word_list(input_file_path)
    word_list = fetch_from_mw(word_list, dictionary_key, dictionary_url, thesaurus_key, thesaurus_url, timeout)
    output_file = create_output_csv(word_list, output_file_path_pattern, timestamp_format)
    print(f"Succussfully create the output file {output_file}")
    return

def test_output():
    print(f"test in {datetime.now()}")
    test_word = Word()
    test_word.word_text = "example"
    test_word.english = "a representative form"
    test_word.chinese = "例子"
    test_word.sys_list = "sample;instance"
    test_word.ant_list = "opposite"
    test_word.category_mask = 0

    config = ConfigParser()
    config.read('config.ini')

    output_file_path_pattern = config['file']['out_put_path_pattern']
    timestamp_format = config['file']['timestamp_format']

    test_file_path = create_output_csv([test_word], output_file_path_pattern, timestamp_format)
    print(f"Test complete, check file {test_file_path}")

def test_read_csv():
    config = ConfigParser()
    config.read('config.ini')

    input_file_path = config['file']['input_file_path_name']
    word_list = initial_word_list(input_file_path, 1, 5)
    for word in word_list:
        print(word.word_text + '\t\t' +  word.chinese)



if __name__ == '__main__':
    main()
    '''
    test_read_csv()
    test_output()
    '''