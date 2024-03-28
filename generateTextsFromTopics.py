import glob
from argparse import ArgumentParser

from openai import OpenAI
import csv
from multiprocessing import Process
import os
import collections
from subjects import subjects as master_subjects_list
arg_parser = ArgumentParser()
arg_parser.add_argument("input_folder_path", type=str)
arg_parser.add_argument("output_folder_path", type=str)
arg_parser.add_argument('--limit_per_topic', required=False, type=int, default=3,
                        help='limit per topic')
args = arg_parser.parse_args()
input_directory = args.input_folder_path
directory = args.output_folder_path
try:
    limit_per_topic = args.limit_per_topic[0]
except:
    limit_per_topic = args.limit_per_topic
if not os.path.exists(directory):
    os.makedirs(directory)

client = OpenAI()

def generate_for_subject(subject_topics):
    subject = subject_topics[0]["subject"]
    file_path = f'{directory}/{subject.replace(" ", "_")}.csv'
    output_dict = ["subject", "grade", "topic", "text"]
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, output_dict)
        dict_writer.writeheader()
    curr = 0
    counter = 0
    while curr < limit_per_topic:
        for each_topic in subject_topics:
            topic = each_topic["topic"]
            grade = each_topic["grade"]
            prompt = f"""Generate a random excerpt from a {grade}th grade {subject} textbook on the subject of {topic}. The excerpt should be approximately 3-5 sentences long and cover key concepts or information relevant to the subject. Include explanations, examples, definitions, and other types of content to ensure variety. Ensure that the excerpts are not summaries or section introductions, but provide a diverse representation of the section's content."
            """
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=384
            )
            text = completion.choices[0].message.content.replace("\n", " ")
            with open(file_path, 'a', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, output_dict)
                dict_writer.writerow({"subject": subject, "grade": grade, "topic": topic, "text": text})
            counter += 1
            print(f"text {counter} of {limit_per_topic * len(subject_topics)} for {subject}")
        curr += 1

if __name__ == "__main__":
    process_list = []
    print(f"Output Path: {directory}")
    csv_files = glob.glob(os.path.join(input_directory, "*.csv"))
    for f in csv_files:
        with open(f, 'r') as file:
            csv_reader = csv.DictReader(file)
            data = [row for row in csv_reader]
        result = collections.defaultdict(list)
        for d in data:
            result[d['subject']].append(d)
            if d['subject'] not in master_subjects_list:
                raise BaseException(f"Subject {d['subject']} not found in subjects list in subjects.py")
        subjects = list(result.values())  # Python 3
        for s in subjects:
            p = Process(target=generate_for_subject, args=(s,))
            process_list.append(p)
    for p in process_list:
        p.start()
    for p in process_list:
        p.join()