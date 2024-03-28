import os

from openai import OpenAI
import csv
from argparse import ArgumentParser
from subjects import subjects

arg_parser = ArgumentParser()
arg_parser.add_argument("output_folder_path", type=str)
arg_parser.add_argument('--limit_per_topic', required=False, type=int, default=25,
                        help='limit per topic')
arg_parser.add_argument('--mode', required=False, type=str, default="write",
                        help='append or write')
args = arg_parser.parse_args()
output_folder_path = args.output_folder_path
try:
    limit_per_topic = args.limit_per_topic[0]
except:
    limit_per_topic = args.limit_per_topic

append_or_write = args.mode
if append_or_write != "append" and append_or_write != "write":
    raise BaseException("--mode must be 'append' or 'write")

print(f"Output Path: {output_folder_path}")
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

client = OpenAI()

header = ["subject", "grade", "topic"]
gen_dict_list = []

for subject in subjects:
    file_path = f"{output_folder_path}/{subject.replace(' ', '_').lower()}.csv"
    if append_or_write == "write":
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, header)
            dict_writer.writeheader()
    if append_or_write == "write":
        usedTopics = []
    else:
        usedTopics = []
        with open(file_path, 'r') as existing_csv_file:
            existing_csv_reader = csv.DictReader(existing_csv_file)
            for existing_row in existing_csv_reader:
                usedTopics.append(existing_row["topic"])
    for grade in range(5, 9):
        for x in range(0, limit_per_topic):
            prompt = f"You are a middle school curriculum curator. Choose a topic for the {grade}th grade {subject}. Make sure this is a real topic taught that is actually taught in an {grade}th grade {subject} class. reply only with the topic name. "
            if len(usedTopics) > 0:
                prompt += " You may NOT choose from the following topics: \n"
                for topic in usedTopics:
                    prompt += f"{topic}\n"
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            text = completion.choices[0].message.content.replace("\n", " ")
            while text in usedTopics:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                text = completion.choices[0].message.content.replace("\n", " ")

            output_dict = {"subject": subject, "grade": grade,
                           "topic": completion.choices[0].message.content.replace("\n", " ")}
            with open(file_path, 'a', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, output_dict)
                dict_writer.writerow({"subject": subject, "grade": grade, "topic": text})
            usedTopics.append(text)
            print(f"{grade}th grade {subject}: {text}")

print("Topic generation complete.")
