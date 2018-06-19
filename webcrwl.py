import argparse
from bs4 import BeautifulSoup
from memory_profiler import memory_usage
import re
import time
import sqlite3
import sys
from urllib.request import URLError, urlopen
from urllib.error import HTTPError

# Regex for protocol check
regex = re.compile(
    r'^(?:http|ftp)s?://'
)

# Database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()


# Progress bar
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = 'x' * filled_len + '.' * (bar_len - filled_len)
    current = '({} of {})'.format(count,total)
    sys.stdout.write('[%s] %s%s ...%s%s\r' % (bar, percents, '%',status,current))
    sys.stdout.flush()


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
    except (URLError, HTTPError, ValueError, AttributeError):
        return False
        # Page file parsing
    html = BeautifulSoup(page.read(), 'lxml')
    return html


# Pages loader function
@runtime
def loader(url):
    html = get_page(url)
    title = html.title.text
    # Deleting all CSS and JS from page
    for script in html(["script", "style"]):
        script.extract()

    cursor.execute("SELECT url,id FROM urls WHERE url =? LIMIT 1", (url,))
    result = cursor.fetchone()
    # If this URL wasn't loaded yet
    if result is None or str(result[0]) != url:
        cursor.execute("INSERT INTO urls (url,title,html) VALUES (?,?,?)", (url, title, str(html)))
        cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,))
        url_id = cursor.fetchone()
        counter = 0
        # Create list of sublinks
        suburls_list = [link.get('href') for link in html.find_all('a') if link.get('href') is not None and str(link).startswith('/') is False
                        and str(link).endswith(('.jpg','.pdf','.docx','.jpeg')) is False and str(link).startswith(('mailto','tel:')) is False and str(link)!='#']
        for link in suburls_list:
            progress(counter,len(suburls_list), status='Loading all dependent pages')
            # and if link match url regex
            suburl = link
            link = get_page(suburl)
            if link is not None and link is not False:
                # insert to db
                try:
                    sub_title = link.find("title").text
                except AttributeError as e:
                    pass
                cursor.execute("INSERT OR IGNORE INTO suburls  (url_id,url,title) VALUES (?,?,?)",
                            (url_id[0],suburl, sub_title,))
            counter += 1
        print("\n Success! Now you can use `get url -n x`")
    else:
        print("Page already was loaded to database. Wanna update it?'")
        cursor.execute("SELECT id FROM urls WHERE url =? LIMIT 1", (url,))
        url_id = cursor.fetchone()
        answer = input('y/n: ')
        if answer.lower() == 'y':
            cursor.execute("DELETE FROM urls WHERE id = ? ",url_id)
            cursor.execute("DELETE FROM suburls WHERE url_id = ?", url_id)
            loader(url)
            return False

        else:
            return False
    conn.commit()
    conn.close()


# Get info from DB
@runtime
def get(url,count=1):
    cursor.execute("SELECT s.url,s.title FROM suburls s LEFT JOIN urls u ON u.id = s.url_id WHERE u.url = ? LIMIT ?",(url,count))
    result = cursor.fetchall()
    if not result:
        print("This url wasn't load yet or sublinks wasn't found. \nTry webcrwl.py load `url` ")
    for row in result:
        print('{}: "{}"'.format(row[0],row[1]))
    conn.close()


# Delete all from database
def clear():
    if input("Are you sure? \ny/n: ") == 'y':
        cursor.execute("DELETE FROM urls")
        cursor.execute("DELETE FROM suburls")
        cursor.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        print('Data was succesfully delete')
    conn.close()




