from os import mkdir, listdir
from os.path import exists
import re
from threading import Thread
from queue import Queue
from dataStructures.scrapingStructures import Metrics
from crawlers.htmlAnalyzer import get_pageText, detect_language


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

# # make the folders
# for folder in topList:
#     mkdir("data/outData/dmozProcessed/" + folder)

### Functions to scrape dmoz tsv file into dataframe for model training ###
def encode_top(top):
    """ Helper to convert top folder of path to index in topList """
    return topList.index(top)


def scrape_dmoz_line(line):
    """ Helper to convert line dmoz tsv file to file of pageText """
    # find url, top, and folder with regexp match
    url = (urlMatcher.findall(line))[0]
    # folder = (folderMatcher.findall(line))[0]
    top = (topMatcher.findall(line))[0]
    # get outPath to which file would be written
    outPath = f"data/outData/dmozProcessed/{top}/{url}.sav"
    if not exists(outPath):
        # fetch pageText from url
        pageText, _ = get_pageText(url)
        # skip page if not in english
        assert (detect_language(pageText) == 'en'), f"{url} not in English"
        # open file in top folder and write pageText in
        with open(outPath, 'w+') as file:
            file.write(pageText)
    else:
        pass
    return True


def scrape_dmoz_file(file, queueDepth=15, workerNum=25, outPath=""):
    """
    Scrapes dmoz tsv file of urls and folders to return dataframe of
    url, folder path, top folder, and readable pageText. Saves dataframe as
    tsv in outPath if specifed.
    """
    # queue to hold lines of file
    lineQueue = Queue(queueDepth)
    # struct to keep track of metrics
    scrapeMetrics = Metrics()

    def worker():
        """ Analyzes popped line from lineQueue and stores data in outStore() """
        while True:
            line = lineQueue.get()
            try:
                # call helper to scrape line
                scrape_dmoz_line(line)
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
        for i, line in enumerate(FileObj):
            if line > 1005724:
                lineQueue.put(line)
            else:
                print(f"Skipping: {i}")

    # ensure all lineQueue processes are complete before proceeding
    lineQueue.join()
    print(f"\nAnalysis complete! Data scraped from {len(outStore.data)} URLs.")
    # save Simple_List() object in outPath if specifed
    if not (outPath == ""):
        save(outStore.data, outPath)


# scrape_dmoz_file(file="/Users/landonsmith/Desktop/DESKTOP/Code/personal-projects/search-engine/backend/data/inData/dmoz_domain_category.tab.tsv")

def make_dmoz_all(path):
    for folder in listdir(path):
        print(folder)
        if not folder in ['All', '.DS_Store']:
            for i, file in enumerate(listdir(f"{path}/{folder}")):
                with open(f'{path}/{folder}/{file}', 'r') as oldFile:
                    text = oldFile.read()
                    with open(f'{path}/All/{file}', 'w+') as newFile:
                        newFile.write(text)
                print(f"\tMoving: {i}", end='\r')
    allLen = len(listdir(f'{path}/All'))
    print(f'{allLen} files moved to {path}/All')

make_dmoz_all('data/outData/dmozProcessed')

print("Done")













pass
