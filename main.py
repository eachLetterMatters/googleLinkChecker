import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import random


# this program is designed to search for any dead links leading to a particular website
# finding them allows to maintain good positioning in google results

# it requires providing xlsx file containing list of popular google search queries
# after reading it, queries are run to search for any links that return 404 status code

PAGE_NAME = "pagename.pl"
QUERIES_FILENAME = "pagename-search.xlsx"
START_INDEX = 900


def generate_full_url(query):
    url = 'https://www.google.com/search?q=' + PAGE_NAME.split(".", 1)[0] + "+" + query.replace(" ", "+")
    # remove_polish_characters
    # trans = str.maketrans('ŻżÓóŃńĄąĘęŚśŹź', 'ZzOoNnAaEeSsZz')
    # url = url.translate(trans)
    return url


def get_queries_from_excel():
    excel_file = pd.ExcelFile(QUERIES_FILENAME)
    df = pd.read_excel(excel_file, sheet_name=0)
    first_column = df.iloc[:, 0]
    return first_column


def convert_html_to_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all <a> tags
    all_a_tags = soup.find_all('a')
    # Filter the list to include only links with page name
    links = [a['href'] for a in all_a_tags if PAGE_NAME in a.get('href', '')]
    return links


# saves dead links into 404_links.txt
def check_links(links):
    with open('all_404_links.txt', 'a') as txt_file:
        for link in links:
            try:
                r = requests.head(link)
                print(r.status_code)
                if r.status_code == 404:
                    print("FOUND 404")
                    txt_file.write(link.strip() + '\n')
            except requests.ConnectionError:
                print("failed to connect")


# shortens returned txt file
def remove_empty_results():
    with open('all_404_links.txt', 'r') as input_file, open('404_links.txt', 'w') as output_file:

        lines = []
        results = []
        previous_line = None

        for line in input_file:
            lines.append(line.strip())

        for line in reversed(lines):
            if line != previous_line:
                if len(line) > 5:
                    results.append(line)
                elif len(previous_line) > 5:
                    results.append(line)
                previous_line = line

        for result in reversed(results):
            output_file.write(result + '\n')


def run_checker():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    queries = get_queries_from_excel()
    # limit amount of queries to 100
    queries = queries[START_INDEX:START_INDEX+100]
    iterator = START_INDEX + 2
    for q in queries:
        with open('all_404_links.txt', 'a') as txt_file:
            txt_file.write(str(iterator) + '\n')
            iterator += 1
        url = generate_full_url(q)
        print(url)
        driver.get(url)
        time.sleep(2)
        links = convert_html_to_links(driver.page_source)
        check_links(links)
        # random sleep time to decrease chance of google noticing this program as bot
        sleep_time = random.uniform(0, 1)
        time.sleep(sleep_time)


run_checker()
remove_empty_results()
