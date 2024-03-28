subjects = [
    "Math",
    "Science",
    "Language",
    "Physical Education",
    "Social Studies",
    "Health",
    "Computers",
    "Leadership"
]

id2label = {}
for index, subject in enumerate(subjects):
    id2label[index] = subject

label2id = {}
for key in id2label:
    label2id[id2label[key]] = key

