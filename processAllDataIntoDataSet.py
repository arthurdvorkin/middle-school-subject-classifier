import collections

import pandas as pd
import csv
import numpy as np
import glob
import os
from textwrap import wrap
import random
import csv
from subjects import label2id
from subjects import subjects as master_list_subjects
from subjects import label2id
from sklearn.model_selection import train_test_split

synthetic_data_path = os.getcwd() + "/generated-data"
synthetic_csv_files = glob.glob(os.path.join(synthetic_data_path, "*.csv"))
khan_data_path = os.getcwd() + "/khan-academy-data"
khan_csv_files = glob.glob(os.path.join(khan_data_path, "*.csv"))
def split_string_at_sentence(string, max_length=512):
    sentences = string.split('. ')  # Split the string into sentences
    result = []
    current_chunk = ''
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_length:
            current_chunk += sentence + '. '
        else:
            result.append(current_chunk.rstrip())
            current_chunk = sentence + '. '
    if current_chunk:
        result.append(current_chunk.rstrip())
    return result


synthetic_combined_data = []
for f in synthetic_csv_files:
    with open(f, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["subject"] in master_list_subjects:
                split_text = split_string_at_sentence(row["text"])
                for txt in split_text:
                    if (txt != ""):
                        synthetic_combined_data.append({"subject": row["subject"],"text": txt, "source": "synthetic"})


khan_pre_combined_data = []
for f in khan_csv_files:
    with open(f, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["subject"] in master_list_subjects:
                split_text = split_string_at_sentence(row["text"])
                for txt in split_text:
                    if (txt != ""):
                        khan_pre_combined_data.append({"subject": row["subject"], "text": txt, "source": "real"})

random.shuffle(khan_pre_combined_data)
result = collections.defaultdict(list)
for each in khan_pre_combined_data:
    result[each['subject']].append(each)
subjects = list(result.values())

khan_combined_data = []
for subject in subjects:
    random.shuffle(subject)
    khan_combined_data += random.choices(subject, k=int((len(synthetic_combined_data)/len(master_list_subjects)))*2)

combined_data = synthetic_combined_data + khan_combined_data

random.shuffle(combined_data)

keys = combined_data[0].keys()

result = collections.defaultdict(list)
for each in combined_data:
    result[each['subject']].append(each)
sep_subjects = list(result.values())

list_len = [len(i) for i in sep_subjects]
shortest_subject = min(list_len)
max_per_subject = int(1.4*shortest_subject)-1

final_combined_data = []
for each in sep_subjects:
    each_len = len(each)
    if each_len <= max_per_subject:
        final_combined_data += each
    else:
        final_combined_data += random.choices(each, k=max_per_subject)

with open('dataset1.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(final_combined_data)

combined_data_texts = []
for text in final_combined_data:
    combined_data_texts.append(text["text"])

combined_data_subjects_text_label = []
for sub in final_combined_data:
    combined_data_subjects_text_label.append(sub["subject"])

combined_data_subjects = []
for each in combined_data_subjects_text_label:
    combined_data_subjects.append(label2id[each])

train_texts, test_texts, train_subjects, test_subjects = train_test_split(combined_data_texts, combined_data_subjects, test_size=0.3, random_state=42)
validation_texts, test_texts, validation_subjects, test_subjects = train_test_split(test_texts, test_subjects, test_size=0.5, random_state=42)
train_dataframe = pd.DataFrame(
    {
        "label": train_subjects,
        "text": train_texts,
    }
)

test_dataframe = pd.DataFrame(
    {
        "label": test_subjects,
        "text": test_texts,
    }
)

validation_dataframe = pd.DataFrame(
    {
        "label": validation_subjects,
        "text": validation_texts,
    }
)


train_dataframe.to_csv("train_dataset.csv", index=False)
test_dataframe.to_csv("test_dataset.csv", index=False)
validation_dataframe.to_csv("validation_dataset.csv", index=False)
