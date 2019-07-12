"""
Loads files that have been crawled into a thicctable
"""
from os import listdir
from termcolor import colored

from dataStructures.objectSaver import load, save
from dataStructures.pageObj import Page
from dataStructures.thicctable import Thicctable
from models.knowledge.knowledgeBuilder import build_knowledgeProcessor

def load_crawled_pages(filePath):
    """
    Loads crawled pages under filePath into a Thicctable().
    Returns:
        -database:          Thicctable() obj of page data
        -uniqueWords:       set of the unique words of token buckets in
                            the database and their lengths
        -searchProcessor:   knowledgeProcessor to find words in database
    """
    # initialize database with knowledgeSet buckets
    print(colored('Loading Knowledge Set', 'red'), end='\r')
    knowledgeSet = load('backend/data/outData/knowledge/knowledgeSet.sav')
    print(colored('Complete: Loading Knowledge Set', 'cyan'))
    database = Thicctable(knowledgeSet)
    del knowledgeSet
    # bucket each page in each file in filePath
    for i, file in enumerate(listdir(filePath)):
        try:
            pageList = load(f'{filePath}/{file}')
            for pageDict in pageList:
                database.bucket_page(Page(pageDict))
            print(colored(f'Building Database: {i}', 'red'), end='\r')
        except Exception as e:
            print(f'{e} at "{file}".')
    print(colored('Complete: Building Database', 'cyan'))
    # clean and sort the database
    print(colored('Cleaning Database', 'red'), end='\r')
    database.kill_empties()
    print(colored('Complete: Cleaning Database', 'cyan'))
    print(colored('Sorting Database', 'red'), end='\r')
    database.sort_all()
    print(colored('Complete: Sorting Database', 'cyan'))
    # find all unique, non-empty words in the database and the length of thier posting list
    print(colored('Finding Unique Words', 'red'), end='\r')
    nonemptyTokens = database.all_lengths()
    uniqueWords = nonemptyTokens.copy()
    for token, length in nonemptyTokens.items():
        words = token.split()
        for word in words:
            if not word in nonemptyTokens:
                uniqueWords.update({word:length})
    print(colored('Complete: Finding Unique Words', 'cyan'))
    # flashtext processor to find keywords in search
    # searchProcessor = build_knowledgeProcessor(uniqueWords)
    searchProcessor = load('backend/data/outData/knowledge/knowledgeProcessor.sav')
    return(database, uniqueWords, searchProcessor)
