import csv
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

base_url = "https://www.khanacademy.org"
output_dir = "./parsed-khan-academy-transcripts"
output_dict = ["subject", "text"]


def split_string_at_sentence(string, max_length=512):
    sentences = string.split(". ")  # Split the string into sentences
    result = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_length:
            current_chunk += sentence + ". "
        else:
            result.append(current_chunk.rstrip())
            current_chunk = sentence + ". "

    if current_chunk:
        result.append(current_chunk.rstrip())
    return result


class KhanParse:
    def __init__(self, subject):
        self.transcripts = []
        self.visited_links = []
        self.subject = subject
        self.added_videos = []
        self.file_path = f"{output_dir}/khan_{subject.replace(' ', '_').lower()}.csv"
        with open(self.file_path, "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, output_dict)
            dict_writer.writeheader()

    def get_transcript(self, path):
        if path in self.added_videos:
            return
        self.added_videos.append(path)
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # for Chrome >= 109
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)

        driver.get(base_url + path)
        try:
            python_button = driver.find_element(
                "id", "ka-videoPageTabs-tabbedpanel-tab-1-inner"
            )
            python_button.click()
        except:
            try:
                python_button = driver.find_element(
                    "id", "ka-videoPageTabs-tabbedpanel-tab-1"
                )
                python_button.click()
            except:
                return

        python_button.click()
        soup = BeautifulSoup(driver.page_source)
        div = soup.find("div", {"id": "ka-videoPageTabs-tabbedpanel-content"})
        spans = div.find_all("span")
        texts = []
        first_sentence = ""
        for span in spans:
            if (
                span.text != "•"
                and span.text != "Current transcript segment: "
                and len(span.text) > 5
            ):
                span_text = span.text.replace("\n", " ")
                if first_sentence.count(".") < 3:
                    first_sentence += " " + span_text
                else:
                    texts.append(span_text)
        driver.quit()
        output_strings = split_string_at_sentence(" ".join(texts))
        with open(self.file_path, "a", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, output_dict)
            print(f"writing: {path}")
            for output_string in output_strings:
                if output_string != "":
                    dict_writer.writerow(
                        {"subject": self.subject, "text": " ".join(texts)}
                    )

    def find_videos_in_course(self, path):
        if path in self.visited_links:
            return
        self.visited_links.append(path)
        r = requests.get(base_url + path)
        soup = BeautifulSoup(
            r.content, "html5lib"
        )  # If this line causes an error, run 'pip install html5lib' or install html5lib
        body = soup.find("main")
        if body is None:
            return
        a_tags = body.findAll("a")
        hrefs = []
        for a_tag in a_tags:
            hrefs.append(a_tag["href"])
        for href in hrefs:
            if path in href:
                sub_href = href.replace(path, "")
                if (
                    len(sub_href) > 0
                    and "quiz" not in sub_href
                    and "/e/" not in sub_href
                    and "/a/" not in sub_href
                    and "/test/" not in sub_href
                    and not sub_href.endswith("/d")
                ):
                    if "/v/" in sub_href:
                        print(f"found video @ {href}")
                        self.get_transcript(href)
                    else:
                        print(base_url + href)
                        self.find_videos_in_course(href)


khan_parser = KhanParse("Science")
khan_parser.find_videos_in_course("/science/middle-school-earth-and-space-science")
khan_parser.find_videos_in_course("/science/ms-physics")
khan_parser.find_videos_in_course("/science/ms-biology")
khan_parser.find_videos_in_course("/math/cc-fifth-grade-math")
khan_parser.find_videos_in_course("/math/cc-sixth-grade-math")
khan_parser = KhanParse("Math")
khan_parser.find_videos_in_course("/math/cc-sixth-grade-math")
khan_parser.find_videos_in_course("/math/cc-seventh-grade-math")
khan_parser.find_videos_in_course("/math/cc-eighth-grade-math")
khan_parser = KhanParse("Social Studies")
khan_parser.find_videos_in_course("/humanities/us-history")
khan_parser.find_videos_in_course("/humanities/us-government-and-civics")
khan_parser.find_videos_in_course("/humanities/world-history")
khan_parser = KhanParse("Language")
khan_parser.find_videos_in_course("/ela/cc-5th-reading-vocab")
khan_parser.find_videos_in_course("/ela/cc-6th-reading-vocab")
khan_parser.find_videos_in_course("/ela/cc-7th-reading-vocab")
khan_parser.find_videos_in_course("/ela/cc-8th-reading-vocab")
khan_parser = KhanParse("Health")
khan_parser.find_videos_in_course("/science/health-and-medicine")
khan_parser = KhanParse("Computers")
khan_parser.find_videos_in_course("/computing/computer-programming/programming")
khan_parser.find_videos_in_course("/computing/computers-and-internet")
