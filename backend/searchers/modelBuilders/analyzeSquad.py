import json
import numpy as np
from math import inf
from tqdm import tqdm, trange
from nltk.tokenize import word_tokenize

class TrainingPadding(object):
    """ Pads training data to be a multiple of batch size. """


class TrainingInstance(object):
    """ Instance of question and answer span upon which to train """
    def __init__(self, qId, cId, answerable):
        """
        qId:            Unique string id of question
        cId:            Unique int id of context paragraph
        answerable:     Boolean; whether the question is answerable

        """

SQUAD_PATH = '../../data/inData/squad/train-v2.0.json'

class LanguageConfig(object):
    """
    Class storing information about the language such as wordId index,
    vocabulary size, and maximum sequence lengths.
    """
    def __init__(self, name, questionLength, contextLength, tokenizer):
        # assertions
        assert isinstance(name, str), f'name expected type string, but found type {type(name)}'
        assert isinstance(questionLength, int), f'questionLength expected type int but found type {type(name)}'
        assert isinstance(contextLength, int), f'contextLength expected type int, but found type {type(name)}'
        assert callable(tokenizer), f'tokenize must be callable'
        # initializations
        self.name = name
        self.questionLength = questionLength
        self.contextLength = contextLength
        self.tokenizer = tokenizer
        self.wordIdx = None
        self.vocabSize = 0
        self.observationNum = 0

    def __repr__(self):
        return (f"<LanguageObject NAME={self.name} "
                f"QUESTION_LENGTH={self.questionLength} "
                f"CONTEXT_LENGTH={self.contextLength} "
                f"VOCAB_SIZE={self.vocabSize} "
                f"OBSERVATION_NUM={self.observationNum}>")

    def initialize_from_squad(self, squadPath):
        """ Reads squad file to initialize Language attributes """
        # set for storing unique tokens
        tokenSet = set()
        # helper for building token set
        def clean_tokenize_and_add(rawString):
            """ Cleans and tokenizess raw string and adds tokens to tokenSet """
            cleanString = rawString.strip().lower()
            textTokens = self.tokenizer(cleanString)
            for token in textTokens:
                tokenSet.add(token)
        # read squad file, gathering number of observations and unique words
        observationNum = 0
        with open(squadPath, 'r') as squadFile:
            for category in tqdm(json.load(squadFile)['data']):
                clean_tokenize_and_add(category['title'])
                for paragraph in category['paragraphs']:
                    clean_tokenize_and_add(paragraph['context'])
                    for question in paragraph['qas']:
                        clean_tokenize_and_add(question['question'])
                        observationNum += 1
        # build word id index and store vocab size and observation num
        wordIdx = {word : i for i, word in enumerate(tokenSet)}
        self.vocabSize = len(wordIdx)
        self.wordIdx = wordIdx
        self.observationNum = observationNum
        return True

    def reverse_idx(self):
        """ Builds reverse index for word lookup from id """
        self.reverseIdx = {i : word for word, i  in self.wordIdx.items()}
        return True

    def token_to_id(self, token):
        """ Converts token to token id using wordIdx dict """
        return self.wordIdx[token]

    def token_list_to_id_list(self, tokenIds):
        """ Uses token_to_id dict to map a token list into an id list """
        to_id_lambda = lambda token : self.token_to_id(token)
        return list(map(to_id_lambda, tokenIds))

    def raw_text_to_id_list(self, rawText):
        """ Uses tokenizer to tokenize raw text and convert to id list """
        textTokens = self.tokenizer(rawText.strip().lower())
        return self.token_list_to_id_list(textTokens)


def squad_to_training_data(squadPath, config, outFolder=None):
    """
    Converts data from squadPath to...
    A 3rd rank feature tensor of shape:
    (observation_num, (question_length + context_length), 3) where 3 is the
    number of features for each token in an observation (input_ids, input_masks,
    segment_ids) and input_ids are scalar token ids for each token, input_masks
    are binary indicators of whether a token should be analyzed, and
    segment_ids are binary indicators of whether a token belongs to the question
    or context in packed sequence.
    And to a 3rd rank target tensor of shape:
    (observation_num, context_length, 2) where 2 is the number of target arrays.
    Both target arrays are binary one-hot vectors encoding start location and
    end location of answer span respectively.
    """
    assert isinstance(config, LanguageConfig), f'config expected type LanguageConfig but got type {type(config)}'

    # cache config info
    questionLength = config.questionLength
    contextLength = config.contextLength
    observationNum = config.observationNum
    packedLength = questionLength + contextLength
    # instantiate zero arrays for features and targets
    featureArray = np.zeros(shape=(observationNum, packedLength, 3))
    targetArray = np.zeros(shape=(observationNum, contextLength, 2))
    # iterate over squad file, filling feature and target arrays
    observation = 0
    with open(squadPath, 'r') as squadFile:
        for category in tqdm(json.load(squadFile)['data']):
            for paragraph in category['paragraphs']:
                paragraphText = paragraph['context']
                paragraphIds = config.raw_text_to_id_list(paragraphTokens)
                for question in paragraph['qas']:
                    questionText = question['question']
                    questionIds = config.raw_text_to_id_list(questionText)
                    # pack question and paragraph ids
                    packedIds = questionIds + paragraphIds
                    packLength = len(packedIds)
                    # update input_id dimension of featureArray
                    featureArray[observation, 0:packLength, 0] = packedIds
                    # update input_mask dimension of featureArray
                    featureArray[curObservation, 0:packLength, 1] = 1
                    # impossible questions have only 0s in targets
                    if question['is_impossible']:
                        pass
                    else:
                        # not sure why but answer and plausible_answers are
                        # used interchangably across squad
                        try:
                            answerList = question['answers']
                        except KeyError:
                            answerList = question['plausible_answers']
                        answerText = answerList[0]['text']
                        # find answer span of answerText
                        answerIds = config.raw_text_to_id_list(answerText)
                        spanLen = len(answerIds)
                        for idLoc, firstId in enumerate(paragraphIds):
                            if (firstId == answerIds[0]):
                                endLoc = idLoc + spanLen
                                if paragraphIds[idLoc : endLoc] == answerIds:
                                    targetArray[observation, idLoc, 0] = 1
                                    targetArray[observation, endLoc, 1] = 1
                    observation += 1

    if outFolder:



with open(SQUAD_PATH, 'r') as squadFile:
    for category in tqdm(json.load(squadFile)['data']):
        for paragraph in category['paragraphs']:
            paragraphText = paragraph['context']
            for question in paragraph['qas']:
                questionText = question['question']
                if question['is_impossible']:
                    pass
                else:
                    # not sure why but answer and plausible_answers are
                    # used interchangably across squad
                    try:
                        answerList = question['answers']
                    except KeyError:
                        answerList = question['plausible_answers']
                    answerText = answerList[0]['text']
                    print(answerText)