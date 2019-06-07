import pandas as pd
import sys, os

for folder in ['dataStructures', 'crawlers', 'data']:
    sys.path.append(os.path.abspath(os.path.join('..', folder)))

from urlAnalyzer import url_to_pageString
from htmlAnalyzer import get_pageText, detect_language
import re
from threading import Thread
from queue import Queue
from simpleStructures import Simple_List, Metrics
from objectSaver import save, load

### Match objects compiled for quick calls in functions ###
# matcher for url in dmozDF line
urlString = r'(?<=").+(?="\t)'
urlMatcher = re.compile(urlString)

# matcher for folder in dmozDF line
folderString = r'(?<=Top/)\S+(?=")'
folderMatcher = re.compile(folderString)

# matcher for top folder in dmozDF line
topString = r'(?<="Top/)[^/]+'
topMatcher = re.compile(topString)

# indexed list of top of path for mapping to number
topList = ['Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'News',
            'Recreation', 'Reference', 'Regional', 'Science', 'Shopping',
            'Society', 'Sports', 'Kids_and_school']


### Functions to scrape dmoz tsv file into dataframe for model training ###
def encode_top(top):
    """ Helper to convert top folder of path to index in topList """
    return topList.index(top)


def scrape_dmoz_line(line):
    """ Helper to convert line dmoz tsv file to dict of url, folder path,  """
    # find url, top, and folder with regexp match
    url = (urlMatcher.findall(line))[0]
    folder = (folderMatcher.findall(line))[0]
    top = (topMatcher.findall(line))[0]
    # fetch pageString from url
    pageString = url_to_pageString(url)
    # get rendered text on pageString
    pageText = get_pageText(pageString)
    # skip page if not in english
    assert (detect_language(pageText) == 'en'), f"{url} not in English"
    # create list of training data to append to Simple struct
    outList = [url, top, folder, pageText]
    return outList


def scrape_dmoz_file(file, queueDepth=15, workerNum=25, outPath=""):
    """
    Scrapes dmoz tsv file of urls and folders to return dataframe of
    url, folder path, top folder, and readable pageText. Saves dataframe as
    tsv in outPath if specifed.
    """
    # queue to hold lines of file
    lineQueue = Queue(queueDepth)
    # struct (list) to hold scraped data
    outStore = Simple_List()
    # struct to keep track of metrics
    scrapeMetrics = Metrics()

    def worker():
        """ Analyzes popped line from lineQueue and stores data in outStore() """
        while True:
            line = lineQueue.get()
            try:
                # call helper to scrape line
                pageDict = scrape_dmoz_line(line)
                # add scraped pageDict to outStore list
                outStore.add(pageDict)
                # update scrape metrics
                scrapeMetrics.add(error=False)
            except:
                # update scrape metrics
                scrapeMetrics.add(error=True)
            # log progress
            print(f"\t{scrapeMetrics.count} URLs analyzed with {scrapeMetrics.errors} errors!", end="\r")
            # signal completion
            lineQueue.task_done()

    # spawn workerNum workers
    for _ in range(workerNum):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    # load lines from file into lineQueue
    with open(file, 'r') as FileObj:
        for line in (FileObj):
            lineQueue.put(line)

    # ensure all lineQueue processes are complete before proceeding
    lineQueue.join()
    print(f"\nAnalysis complete! Data scraped from {len(outStore.data)} URLs.")
    # save Simple_List() object in outPath if specifed
    if not (outPath == ""):
        save(outStore.data, outPath)

    return(outStore)


scrape_dmoz_file(file="data/inData/test.tab.tsv", outPath="data/outData/outStore2.obj")


#### MODEL STUFF ####

# from keras.models import Sequential

# dmozDF = pd.DataFrame(dmozSimple.data, columns=["url", "top", "path", "pageText"])
#
# print("DMOZ HEAD:\n:", dmozDF.head, end=f"\n{'-'*40}\n")
#
# dmozDF['pageText'] = dmozDF['pageText'].apply(lambda text : tv.tokenize(text))
#
# dmozDF['pageText'] = dmozDF['pageText'].apply(lambda tokenList : tv.vectorize(tokenList))
#
# dmozDF['top'] = dmozDF['top'].apply(lambda top : encode_top(top))
#
# from keras.utils import to_categorical
#
# dmozDF['top'] = to_categorical(dmozDF['top'])
#
# print(dmozDF['top'])


# print(f"\n\n{'-'*60}\nDMOZ MODIFIED:\n{dmozDF.head}\n{'-'*60}")

# print(f"{'-'*40}Top:\n{dmozDF['top']}")








pass