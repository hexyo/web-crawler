import argparse
from urllib.error import HTTPError

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
parser_b.add_argument('-n','--count', help='strings amount')
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
        print("\n execution time: {0} sec ||| peak memory usage: {1} MiB".format(str((time_end - time_start))[:4], str(memory)[:5]))
        return result
    return time_and_memory_count


def get_page(url):
    # Catching page
    try:
        page = urlopen(url)
    except (URLError,HTTPError, ValueError):
        raise URLError('Invalid URL')
    # Page file parsing
    html = BeautifulSoup(page.read(), 'html.parser')
    # Deleting all CSS and JS from page
    for script in html(["script", "style"]):
        script.extract()
    return html


def links_insert(html):
   for link in html.find_all('a'):
        link = link.get('href')
        if link != 'None' and str(link) is not '/':
            return None


# Main function for web crawler
@runtime
def loader(url):
    html = get_page(url)
    title = html.title.text
    cursor.execute("SELECT url,id FROM urls WHERE url =? LIMIT 1", (url,))
    result = cursor.fetchone()
    if result is None or str(result[0]) != url:
        cursor.execute("INSERT INTO urls (url,title,html) VALUES (?,?,?)", (url, title, str(html)))
        cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,))
        url_id = cursor.fetchone()
        counter = 0
        for link in html.find_all('a'):
            link = link.get('href')
            if link is not None and str(link) is not '/':
                counter += 1
                if re.match(regex,link) is not None:
                    print("{} iteration. (Valid URL)".format(counter))
                    suburl = link
                    link = get_page(suburl)
                    cursor.execute("INSERT OR IGNORE INTO suburls  (url_id,url,title) VALUES (?,?,?)",
                                   (url_id[0],suburl, link.title.text,))
                else:
                    print("{} iteration. (Handmade URL)".format(counter))
                    suburl = url+link
                    link = get_page(suburl)
                    cursor.execute("INSERT OR IGNORE INTO suburls  (url_id,url,title) VALUES (?,?,?)",
                                   (url_id[0],suburl, link.title.text,))


        print("Page was loaded successful")
        # Finish insertion to suburls database here
        # Looking for urls
        ''' for link in html.find_all('a'):
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
            # print(cursor.execute("SELECT id FROM urls u WHERE rowid > 0").fetchall())'''
    else:
        print("Page already was loaded to database. You can update it with 'webcrwl.py update url'")
        return False
    conn.commit()
    conn.close()

@runtime
def get(url,count=1):
    cursor.execute("SELECT s.url,s.title FROM suburls s LEFT JOIN urls u ON u.id = s.url_id WHERE u.url = ? LIMIT ?",(url,count))
    result = cursor.fetchall()
    if not result:
        print("This url wasn't load yet or sublinks wasn't found. \nTry webcrwl.py load `url` ")
    for row in result:
        print('{}: "{}"'.format(row[0],row[1]))


def main():
    if args.subparse == 'get':
        get(args.url,args.count)
    if args.subparse == 'load':
        loader(args.url)

    # Commit and close database



if __name__ == "__main__":
    main()