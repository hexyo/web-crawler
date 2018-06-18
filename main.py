import argparse
from bs4 import BeautifulSoup
import time
from memory_profiler import memory_usage
import sqlite3
import re
from urllib.request import URLError, urlopen




# FINISH ARGPARSER ALL COMMANDS (ADD UPDATE FUNC)
# args_parser init
parser = argparse.ArgumentParser()
#parser.add_argument('load', help='load page and urls to database')
#parser.add_argument('get', help='get page info from database')
parser.add_argument('url', help='url for crawling')
#parser
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
def crawler(url):
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
    cursor.execute("SELECT * FROM urls WHERE url =? LIMIT 1", (url,))
    result = cursor.fetchone()
    if result is None or str(result[1]) != url:
        cursor.execute("INSERT INTO urls (url,title,html) VALUES (?,?,?)", (url, title, str(html)))
    else:
        print("Page already was loaded to database. Use main.py -get url command instead")
        return False
    conn.commit()
    conn.close()

    # Finish insertion to suburls database here
    # Looking for urls
    for link in html.find_all('a'):
        link = link.get('href')
        if link is not None and str(link) is not '/':
            if re.match(regex,link) is not None:
                pass
                #subpage = urlopen(link)
                #subpage = subpage.title
            else:
                pass
                #print(url+link)
    #print(cursor.execute("SELECT id FROM urls u WHERE rowid > 0").fetchall())


if __name__ == "__main__":
    crawler(args.url)
    #if args.load:
       # pass
    #if args.get:
       # pass