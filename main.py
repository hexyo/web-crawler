import argparse
from webcrwl import get,loader,clear


# ArgsParser initialise
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='subparse')
# Args for load data
parser_a = subparsers.add_parser('load', help='load page and urls to database')
parser_a.add_argument('url', help='url for crawling')
#  Args for get data
parser_b = subparsers.add_parser('get', help='get page info from database')
parser_b.add_argument('url', help='url for loading data')
parser_b.add_argument('-n','--count', help='strings amount')
# Args for deleting all data from db
parser_c = subparsers.add_parser('clear',help ='drop all data!')
args = parser.parse_args()


def main():
    if args.subparse == 'get':
        get(args.url,args.count)
    if args.subparse == 'load':
        loader(args.url)
    if args.subparse == 'clear':
        clear()


if __name__ == "__main__":
    main()