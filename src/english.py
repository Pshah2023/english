#!/usr/bin/env poetry run python3
import random
import re
import subprocess
import nltk
from datetime import datetime
import sys
from nltk.tokenize.treebank import TreebankWordDetokenizer
import glob
import os
import importing
# from Code.old.old import Old


class LearnEnglish:
    """The Main Function"""
    learning = "\n+ Positives; Differences; Cues; Efficiency: "

    def __init__(self, x, number=0):
        inp = x.clipboard()
        if len(inp) < 500:
            inp = x.docs()
        inp = re.sub("\n\n", " ¶ ", inp)
        inp = re.sub(" ¶ ", "¶ ¶", inp)
        inp = re.sub(r"\n", " ", inp)
        inp = re.sub(r"\s\s+", " ", inp)
        self.token_text = nltk.tokenize.sent_tokenize(inp)
        self.itr = iter(enumerate(self.token_text))
        text = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        comprehension = [self.highlights]
        # practice = [Old.quickWords, Old.emotions, Old.sentenceStructure, Old.punctuation,
        #             Old.fillingIn, Old.endToBeginning, Old.paragraphStructure, Old.wordByWord, Old.beginningWords]
        for num, s in self.itr:
            text += [random.choice(comprehension), comprehension[number-1]
                     ][number != 0](s, num)
        x.write(text)
        x.json(self.token_text)

    def highlights(self, s, num, out=""):
        """Guess the important words and classify them
        The format is storage, category, and emotion."""
        out += "\n" + "\n+ " + str(num) + " highlights " + \
            "P's, D's, C's, or E's: "
        out += "\n" + s
        out += "\nHighlights: "
        out += "\n" + "\n[]() + C: "
        out += "\n"
        return out


class ImproveEnglish:

    def __init__(self, x, levels=3):
        if levels > 0:
            self.highlights(x)
        if levels > 1:
            self.numericAnalysis(x)
        if levels > 2:
            self.processAnalysis(x)

    def findall(self, startString, endString, fullstring):
        allInstances = []
        startPosition = fullstring.find(startString)
        endPosition = fullstring.find(endString)
        while startPosition != -1:
            allInstances.append((startPosition+len(startString), endPosition))
            startPosition = fullstring.find(startString, startPosition+1)
            endPosition = fullstring.find(endString, endPosition+1)
        return allInstances

    def highlights(self, x):
        listOfWords = x.yaml()
        listOfWords = [item for item in listOfWords if isinstance(item, str)]
        inp = x.write()
        for startPoint, endPoint in self.findall("\nHighlights: ", "\n[]() + C:", inp):
            words = re.split(", ", inp[startPoint:endPoint])
            for word in words:
                word = word.strip()
                if word != "" and word not in listOfWords:
                    listOfWords.append(word)
        x.yaml(listOfWords)

    def numericAnalysis(self, x):
        listOfWords = x.yaml()
        listOfWords = [item for item in listOfWords if isinstance(item, str)]
        organizedList = [[], [], []]
        for each in listOfWords:
            if isinstance(each, str):
                if "0" in each:
                    organizedList[0].append(each)
                if "1" in each:
                    organizedList[1].append(each)
                if "2" in each:
                    organizedList[2].append(each)
        organizedList = [li for li in organizedList if len(li) != 0]
        x.yaml(listOfWords + organizedList)

    def processAnalysis(self, x):
        listOfWords = x.yaml()
        wordsOnly = [item for item in listOfWords if isinstance(item, str)]
        wordDictionary = dict()
        for num, word in enumerate(wordsOnly):
            try:
                wordDictionary[word] = wordsOnly[num+1]
            except IndexError:
                pass
        listOfWords.append(wordDictionary)
        x.yaml(listOfWords)


def main(approach=0):
    try:
        approach = int(sys.argv[1])
    except IndexError:
        pass
    assert (approach != 0)
    if approach == 2:
        x = importing.System(False)
        x.chineseFixer("highlights", False)
        ImproveEnglish(x)
        x.chineseFixer("highlights", True)
        x.log("[System] Analysis complete")
    elif approach == 1:
        x = importing.System(["data", "learning", "highlights"])
        LearnEnglish(x)
        x.log("[System] New learning began")
        x.openFiles(learning=True, highlights=True)


if __name__ == "__main__":
    main()
