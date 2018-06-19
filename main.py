import argparse
from bs4 import BeautifulSoup
import time
from memory_profiler import memory_usage
import sqlite3
import re
from urllib.request import URLError, urlopen


# ArgsParser initialise
parser = argparse.ArgumentParser(prog='Crawler')
subparsers = parser.add_subparsers(dest='subparse')
# ArgsParser for load data
parser_a = subparsers.add_parser('load', help='load page and urls to database')
parser_a.add_argument('url', help='url for crawling')
#  ArgsParser for get data
parser_b = subparsers.add_parser('get', help='get page info from database')
parser_b.add_argument('url', help='url for loading data')
parser_b.add_argument('-n', help='strings amount')
# ArgsParser for update data
parser_c = subparsers.add_parser('update', help='update database content on existing page')
parser_c.add_argument('url', help='url for loading data')
args = parser.parse_args()

# Regex for protocol check
regex = re.compile(
    r'^(?:http|ftp)s?://'
)

# Database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()


# Decorator for execution time and memory usage counting
def runtime(func):
    def time_and_memory_count(*args):
        time_start = time.time()
        result = func(*args)
        if result is False:
            return None
        time_end = time.time()
        memory = max(memory_usage())
        print("execution time: {0} sec ||| peak memory usage: {1} MiB".format(str((time_end - time_start))[:4], str(memory)[:5]))
        return result
    return time_and_memory_count


def get_page(url):
    # Catching page
    try:
        page = urlopen(url)
    except (URLError, ValueError):
        raise URLError('Invalid URL')
    # Page file parsing
    html = BeautifulSoup(page.read(), 'html.parser')
    # Deleting all CSS and JS from page
    for script in html(["script", "style"]):
        script.extract()
    return html


# Main function for web crawler
@runtime
def loader(url):
    html = get_page(url)
    title = html.title.text
    cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,))
    result = cursor.fetchone()
    if result is None or str(result[0]) != url:
        cursor.execute("INSERT INTO urls (url,title,html) VALUES (?,?,?)", (url, title, str(html)))
    else:
        print("Page already was loaded to database. You can update it with 'main.py update url'")
        return False


    # Finish insertion to suburls database here
    # Looking for urls
    for link in html.find_all('a'):
        link = link.get('href')
        if link and str(link) is not '/':
            if re.match(regex, link) is not None:
                try:
                    subpage = urlopen(link)
                except (URLError, ValueError):
                    raise URLError('Invalid URL')

                subpage = BeautifulSoup(subpage.read(), 'html.parser')
                cursor.execute("INSERT INTO suburls (url_id,url,title) VALUES (?,?,?)", (cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,)).fetchone(), link, (BeautifulSoup.find("title"))))
            else:
                pass
                # print(url+link)
    # print(cursor.execute("SELECT id FROM urls u WHERE rowid > 0").fetchall())


def main():
    if args.subparse == 'get':
        pass
    if args.subparse == 'load':
        loader(args.url)
    # Commit and close database
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()