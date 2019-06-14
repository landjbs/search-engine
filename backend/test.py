import models.knowledge.knowledgeFinder as knowledgeFinder
import models.knowledge.knowledgeBuilder as knowledgeBuilder
from dataStructures.objectSaver import load
from dataStructures.thicctable import Thicctable
import models.binning.docVecs as docVecs
import crawlers.htmlAnalyzer as htmlAnalyzer
from models.processing.cleaner import clean_text

from crawlers.crawler import scrape_urlList

database = scrape_urlList(['www.harvard.edu', 'https://en.wikipedia.org/wiki/Harvard_University'])

searchLambda = lambda item : item[:2]
print(f"{'-'*73}\nWelcome to Boogle\t\t\t\t\t\t\t|\n{'-'*73}")
while True:
    try:
        search = input("Search: ")
        clean_search = clean_text(search)
        results = database.search_index(clean_search, searchLambda)
        print("\tResults:")
        for i, elt in enumerate(results):
            print(f"\t\t{i}: {elt}")
    except Exception as e:
        print(f'ERROR: {e}')

## Document vectorization ##
# from flashtext import KeywordProcessor
# from gensim.models.doc2vec import Doc2Vec
#
# knowledgeSet = {'harvard'}
#
# knowledgeProcessor = knowledgeBuilder.build_knowledgeProcessor(knowledgeSet)
#
# db = Thicctable(knowledgeSet)
#
# imdbModel = Doc2Vec.load('data/outData/binning/imdbModel.sav')
#
# urlList = ['www.harvard.edu', 'https://en.wikipedia.org/wiki/Harvard_University',
#             'https://simple.wikipedia.org/wiki/Harvard_University',
#             'https://twitter.com/Harvard?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor',
#             'https://twitter.com/HarvardHBS?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor',
#             'https://www.hbs.edu/Pages/default.aspx', 'http://www.harvard.com',
#             'https://www.allrecipes.com/recipes/76/appetizers-and-snacks/?internalSource=hub%20nav&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202']
#
# urlList = [urlList[1], urlList[4], urlList[-1]]
#
# docDict = {}
#
# import numpy as np
#
# vecMatrix = np.zeros((len(urlList), 300))
#
# for i, url in enumerate(urlList):
#     try:
#         pageText = htmlAnalyzer.get_pageText(url)
#         pageVec = docVecs.vectorize_document(pageText, imdbModel)
#         docDict.update({url:pageVec})
#         vecMatrix[i] = np.asarray(pageVec)
#         print(f"COMPLETE: {url}")
#     except Exception as e:
#         print(e)
#
# import matplotlib.pyplot as plt
#
# dists1, dists2 = [], []
#
# for i, col in enumerate(vecMatrix.T):
#     dist1 = np.abs(col[0] - col[1])
#     dist2 = np.abs(col[0] - col[2])
#     print(f"{i} dist1: {dist1} dist2: {dist2}")
#     if dist1 <0.5 and dist2 < 0.5:
#         print(f'\t\t\t{i}')
#     dists1.append(np.abs(dist1))
#     dists2.append(np.abs(dist2))
#
# # docVecs.visualize_vecDict(docDict)
# plt.plot(dists1)
# plt.plot(dists2)
# plt.show()
#
#
# pass
