# Middle School Subject Text Classifier

## Demo

https://middle-school-subject-classifier-jhgjhbg2b5r3tfuve8uo6z.streamlit.app/

## Overview

This project takes text and classifies it according to the following middle school topics:

- Math
- Science
- Language
- Social Studies
- Physical Education
- Computers
- Health
- Leadership

To achieve this, I fine tuned DistilBERT with the help of HuggingFace's Transformers Library and Pytorch on synthetically
generated data and processed Khan Academy vido transcripts. At the end of the fine tuning process, the resulting model
achieves a ~98% accuracy on the test set. The final model was uploaded on streamlit for web access.

### Tech Stack

##### GPU Accelerated Compute

Lambda Labs (NVIDIA A-10 Instance)

#### ML Framework

HuggingFace Transformers and PyTorch

#### Data Analysis, Metrics, etc

SkLearn, MatPlotLib, Pandas, Numpy

#### Model Deployment

Streamlit

## Dataset

To create the dataset, given the original requirements, I needed to source data for the following subjects:

- Math
- Science
- Language
- History
- Social Studies
- Physical Education
- Computers
- Health
- Leadership

Since social studies and history, at least in US middle schools, are the same subject, I decided to remove history
for the list of subjects, as there would be too significant of anoverlap between the 2 subjects, therefore, throwing off
the model and not being particularly good data.

To source data, I used two methods:

- Synthetic generation using GPT 3.5 Turbo
- Web scrapping Khan Academy video transcripts

The math, science, language, social studies, and health subject texts for the data set are comprised of data obtained
from khan academy and synthetic generation. The texts obtained for computers, physical education, and leadership were
obtained from only from synthetic generation. I opted for synthetic data only for those 3 subjects because 1) there aren't many
free digital resources for those subjects geared towards middle school students 2) these are very simple and well defined
things that gpt can generate very easily and accurately.

### Synthetic Generation

I did synthetic generation in two steps. The first step was to generate topics. I wrote a script(generateTopics.py) that
generated topics for each subject per middle school grade(5th, 6th, 7th, and 8th). To ensure I would not get a bunch
of duplicate topics, I included, in the prompt, in each iteration on a per subject basis, a list of topics it may not
choose from. This list contains already used topics. In step two, I wrote a script (generateTextsFromTopics.py) that took those output topics, the generated texts from them. I used this two step process to ensure I get an accurate and diverse dataset that represents texts you'd find in a
middle school textbook.

I used synthetic generation as the data that needed to be generated is more or less simple and GPT could easily generate
a diverse and accurate dataset. I did have to stop generating at a point due to OPENAI rate limit for gpt-3.5-turbo. It took a few itterations to get the
synthetic data generations to a desirable point.

### Post Processing

For all the data(synthetic and Khan Academy video transcripts), I trimmed all data to be under 512 tokens long. All the splits were done in a way that sentences were
kept intact and not split. This was done to increase the amount of data rows(the original synthetic texts are long and the
khan academy video transcripts are 1 data row per transcript) and minimize truncation during tokenization.
This processing is done in processAllDataIntoDataSet.py.

For the Khan academy video transcripts, the data was cleaned so it would not contain unneeded
text such as current speaker indicator. I also made sure the dataset was balanced in terms of texts per subject. As some of the subjects only had syntheticly
generated texts, some subjects had less data. I made sure that the subject with the smallest amount of texts was
no smaller than 70% of the the subject with the largest amount of texts.

### Data Quality Analysis and Train/Test/Validation Split

#### Train Test Split

- Training Set: 80%
- Validation Set: 10%
- Test Set: 10%

### Data Quality Analysis

A lot of the analysis done was visual inspection of the data. Skimming through a lot of the texts to make sure they
represent the problem. I also generated some charts to help visualize the data(analyzeData.ipynb). I looked at the balance per class
and made sure that the subject with the smallest number of texts is within 70% of the subject with the largest number
of texts. When I looked at the distribution of word length, I noticed most of the texts had between 400 and 500 characters.
This is fine as models like DistilBERT tend to train better for classification tasks with longer texts in the training set.
After digging around on the internet and doing an A/B training test, I confirmed that longer texts indeed perform better.
From my AB test, the accuracy went up by around 5%.

## Model choice

When thinking about model choice, I thought about two different approaches. Traditional ML approaches or fine-tuning pre-trained transformer-based models. My thought here is to figure out the most efficient(meaning the cheapest cost to run) model that can get us accurate(>90%) results. Here’s some models that came to mind:

- Traditional ML
  - SVM (Support Vector Machine)
  - LSTM(Long sort-term memory) network
  - Naive Bayes
  - KNN (K-Nearest Neighbors)
  - Downstream NLP
- Pre-Trained Transformer Based Models
  - BERT Variants
    - BERT
    - DistilBERT
    - RoBERTa
    - ALBERT

Since this project focuses on fine tuning LLMs, I will stick with option 2(Pre-Trained Transformed Based Models).
But I would like to note that some traditional ML constructs such as SVMs have shown that,for fairly simple text classification problems
such as the one I am working on here, performance is very similar to fine tuned pre-trained
transformer based models (check sources 1, 2, & 3 at the bottom of this readme). But as traditional ML constructs lack an understanding context in a text, there
are of course many limiations.

### Base Model(DistilBERT) Test Metrics

#### Summary Metrics

| Metrics            | Value  |
| ------------------ | ------ |
| Queries Per Second | 532.51 |
| Accuracy           | 14.00% |

#### Precision Per Subject

| Subject            | Precision |
| ------------------ | --------- |
| Math               | 0.00%     |
| Science            | 36.36%    |
| Language           | 13.71%    |
| Physical Education | 0.00%     |
| Social Studies     | 0.00%     |
| Health             | 0.00%     |
| Computers          | 0.00%     |
| Leadership         | 0.00%     |

#### Recall Per Subject

| Subject            | Recall |
| ------------------ | ------ |
| Math               | 0.00%  |
| Science            | 4.07%  |
| Language           | 100%   |
| Physical Education | 0.00%  |
| Social Studies     | 0.00%  |
| Health             | 0.00%  |
| Computers          | 0.00%  |
| Leadership         | 0.00%  |

### Fine Tuning

The methodology I took to fine tuning was keeping things as simple as possible and reaching
for something more complicated if needed. This is why I went with the HuggingFace auto trainer with PyTorch.
While native pytorch gives you more control, I thought it would be worth to start with the simplest
possible way to train the model, and see what results I get. The following 3 points led
me to think that the auto trainer would be sufficient for the needs of this problem.

1. The scope of the problem is narrow with simple data that is likely somewhat similar to what the model has been pretrained on
2. The separation between categories is fairly large.
3. The data, from looking at it, is fairly simple, well defined per category, and diverse

Given the above 3 points. I concluded that its more time efficient to forego writing the boiler plate
needed for native pytorch and just start with the auto trainer. If needed, I could easily move to
native pytorch.

To fine tune DistilBERT, I took the supervised learning approach, using LORA(due to its great efficiency)
for parameter training(Check source 6). To ensure fine tuning was producing good results, I started with a baseline configuration and adjusted
hyperparameters and number of epochs as needed based on accuracy, f1, train loss, validation loss,
test loss, and test precision. Since validation loss stabilized at 8 epochs, I stopped fine tuning at 8 epochs to
prevent the model from overfitting. I also used the precision per class and accuracy per class metrics
from the test set to make sure that there were no outliers and that the model is more or less
equally accurate for each class.

I did the fine tuning on Lambda Labs with a NVIDIA A10 GPU(this was the only cheap one available at the moment).
I went Lambda Labs as its reliable, fairly inexpensive, and I've had good experiences with them in the past.

### DistilBERT Fine Tuning Results

#### Summary Metrics

| Metrics            | Value  |
| ------------------ | ------ |
| Queries Per Second | 608.24 |
| Accuracy           | 97.70% |

#### Precision per Subject

| Subject            | Precision |
| ------------------ | --------- |
| Math               | 99.39%    |
| Science            | 97.96%    |
| Language           | 97.37%    |
| Physical Education | 98.56%    |
| Social Studies     | 99.36%    |
| Health             | 96.43%    |
| Computers          | 94.96%    |
| Leadership         | 96.89%    |

#### Recall per Subject

| Subject            | Recall |
| ------------------ | ------ |
| Math               | 99.39% |
| Science            | 97.63% |
| Language           | 99.33% |
| Physical Education | 98.10% |
| Social Studies     | 98.10% |
| Health             | 97.38% |
| Computers          | 97.84% |
| Leadership         | 92.77% |

As expected, the subjects with more data did a little better.

### Sources

Source1: https://arxiv.org/pdf/2211.02563.pdf

Source2: https://medium.com/@claude.feldges/text-classification-with-tf-idf-lstm-bert-a-quantitative-comparison-b8409b556cb3

Source3: https://medium.com/@tam.tamanna18/exploring-the-power-of-nlp-why-embeddings-usually-outperform-tf-idf-98742e7b0bce

Source 3: https://medium.com/@quocnle/how-we-scaled-bert-to-serve-1-billion-daily-requests-on-cpus-d99be090db26

Source 4: https://cdn.techscience.cn/ueditor/files/jqc/TSP_JQC-4-1/TSP_JQC_26658/TSP_JQC_26658.pdf

Source 5: https://su.diva-portal.org/smash/get/diva2:1784346/FULLTEXT01.pdf

Source 6: https://arxiv.org/pdf/2306.07967.pdf
