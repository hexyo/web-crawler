import argparse
from bs4 import BeautifulSoup
import time
from memory_profiler import memory_usage
import sqlite3
import re
from urllib.request import URLError, urlopen



# FINISH ARGPARSER ALL COMMANDS (ADD UPDATE FUNC)
# args_parser init
parser = argparse.ArgumentParser(prog='Crawler')
subparsers = parser.add_subparsers(dest='subparse')
# Parser for load data
parser_a = subparsers.add_parser('load', help='load page and urls to database')
parser_a.add_argument('url', help='url for crawling')
# Parser for get data
parser_b = subparsers.add_parser('get', help='get page info from database')
parser_b.add_argument('url', help='url for loading data')
parser_b.add_argument('-n', help='strings amount')
args = parser.parse_args()


# Regex for protocol check
regex = re.compile(
    r'^(?:http|ftp)s?://'
)


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


# Main function for web crawler
@runtime
def loader(url):
    # Catching page
    try:
        page = urlopen(url)
    except (URLError, ValueError):
        raise URLError('Invalid URL')

    html = BeautifulSoup(page.read(), 'html.parser')
    title = html.title.text
    for script in html(["script", "style"]):
        script.extract()
    # Database connection
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,))
    result = cursor.fetchone()
    if result is None or str(result[0]) != url:
        cursor.execute("INSERT INTO urls (url,title,html) VALUES (?,?,?)", (url, title, str(html)))
    else:
        print("Page already was loaded to database. Use main.py -get url command instead")
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

                subpage = BeautifulSoup(page.read(), 'html.parser')
                cursor.execute("INSERT INTO suburls (url_id,url,title) VALUES (?,?,?)", (cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,)).fetchone(), link, (BeautifulSoup.find(["title"]))))
            else:
                pass
                #print(url+link)
    #print(cursor.execute("SELECT id FROM urls u WHERE rowid > 0").fetchall())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if args.subparse == 'get':
        pass
    if args.subparse == 'load':
        loader(args.url)