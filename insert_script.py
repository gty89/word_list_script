import csv
from configparser import ConfigParser
import requests
from datetime import datetime
from tqdm import tqdm

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

def initial_word_list(input_file_path):
    word_list = []
    with open(input_file_path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            new_word = Word()
            new_word.word_text = row[0].lower()
            new_word.chinese = row[1]
            word_list.append(new_word)
    return word_list

def fetch_from_mw(word_list: list[Word], api_key, dictionary_url, thesaurus_url, timeout = 30, max_word_length = 400):
    if len(word_list) == 0:
        return []
    if len(word_list) > max_word_length:
        word_list = word_list[:max_word_length]
    for word in tqdm(word_list):
        response = requests.get(url = dictionary_url + word.word_text, params = {"key": api_key}, timeout = timeout)
        data = response.json()
        if data and isinstance(data[0], dict):
            definitions = data[0].get("shortdef", [])
            word.english = "; ".join(definitions)
        response = requests.get(url = thesaurus_url + word.word_text, params = {"key": api_key}, timeout = timeout)
        data = response.json()
        if data and isinstance(data[0], dict):
            synonym_words = data[0].get("syns", [])
            if synonym_words is not None and len(synonym_words) > 0:
                word.sys_list = "; ".join(synonym_words)
            antonym_words = data[0].get("syns", [])
            if antonym_words is not None and len(antonym_words) > 0:
                word.ant_list = "; ".join(antonym_words)
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
    api_key = config['api']['key']
    dictionary_url = config['api']['mw_dictionary_url']
    thesaurus_url = config['api']['mw_thesaurus_url']
    timeout = int(config['api']['timeout'])

    input_file_path = config['file']['input_file_path_name']
    output_file_path_pattern = config['file']['out_put_path_pattern']
    timestamp_format = config['file']['timestamp_format']
    word_list = initial_word_list(input_file_path)
    word_list = fetch_from_mw(word_list, api_key, dictionary_url, thesaurus_url, timeout)
    output_file = create_output_csv(word_list, output_file_path_pattern, timestamp_format)
    print(f"Succussfully create the output file {output_file}")
    return

if __name__ == '__main__':
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
    