#!/usr/bin/env poetry run python3
import random
import re
import subprocess
import nltk
from datetime import datetime
import sys
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
import glob
import os
import importing
from langdetect import detect


class LearnEnglish:
    """The Main Function"""
    learning = "\n+ Positives; Differences; Cues; Efficiency: "

    def __init__(self, x, number=0):
        inp = x.clipboard()
        if len(inp) < 500:
            inp = x.write(path="docs")
        language = detect(inp)
        if language == "en":
            inp = re.sub("", ". ", inp)
            inp = re.sub("\n\n", " ¶ ", inp)
            inp = re.sub(" ¶ ", "¶ ¶", inp)
            inp = re.sub(r"\n", " ", inp)
            inp = re.sub(r"\s\s+", " ", inp)
            self.token_text = nltk.tokenize.sent_tokenize(inp)
            self.itr = iter(enumerate(self.token_text))
        if language == "zh-cn":
            inp = StanfordSegmenter()
            
        text = []
        comprehension = [self.highlights]
        for num, s in self.itr:
            text = text + [random.choice(comprehension), comprehension[number-1]
                     ][number != 0](s, num)
        x.toml(text, path="learning")
        x.toml(self.token_text, path="data")

    def highlights(self, s, num, out=""):
        """Guess the important words and classify them
        The format is storage, category, and emotion. Previously.
        Not it is Positives, Differences, Cues, and Efficiency."""
        out = [str(num) + " highlights: "]
        out.append(s)
        out.append("")
        return [out]

class ImproveEnglish:

    def __init__(self, x, levels=4):
        if levels > 0:
            self.highlights(x)
        if levels > 1:
            self.numericAnalysis(x)
        if levels > 2:
            self.processAnalysis(x)
        if levels > 3:
            self.numericProcessAnalysis(x)


    def highlights(self, x):
        listOfWords = x.toml(path="highlights")
        listOfWords = [item for item in listOfWords if isinstance(item, str)]
        inp = x.write()
        for startPoint, endPoint in self.findall("\nHighlights: ", "\n[]() + C:", inp):
            words = re.split(", ", inp[startPoint:endPoint])
            for word in words:
                word = word.strip()
                if word != "" and word not in listOfWords:
                    listOfWords.append(word)
        x.toml(listOfWords, path="highlights")

    def numericAnalysis(self, x):
        listOfWords = x.toml(path="highlights")
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
        listOfWords = x.toml(listOfWords + organizedList, path="highlights")

    def processAnalysis(self, x):
        listOfWords = x.toml(path="highlights")
        wordsOnly = [item for item in listOfWords if isinstance(item, str)]
        wordDictionary = dict()
        for num, word in enumerate(wordsOnly):
            try:
                wordDictionary[word] = wordsOnly[num+1]
            except IndexError:
                pass
        listOfWords.append(wordDictionary)
        x.toml(listOfWords, path="highlights")
    
    def numericProcessAnalysis(self, x):
        listOfWords = x.toml(path="highlights")
        wordsOnly = [item.strip() for item in listOfWords if isinstance(item, str)]
        wordDictionary = dict()
        for num, word in enumerate(wordsOnly):
            try:
                wordDictionary[word] = wordsOnly[num+1]
            except IndexError:
                pass
        wordDictionaryList = [dict(), dict(), dict(), dict(), dict(), dict(), dict()]
        for key, value in wordDictionary.items():
            
            try:
                if int(key[-1]) + int(value[-1]) == 4:
                    number = 6
                elif int(key[-1]) + int(value[-1]) == 3:
                    number == 5
                elif int(key[-1]) + int(value[-1]) == 2:
                    number == 3
                elif int(key[-1]) + int(value[-1]) == 1:
                    number == 1
                elif int(key[-1]) + int(value[-1]) == 0:
                    number == 0
                if int(key[-1]) < int(value[-1]):
                    number += 1
                wordDictionaryList[number][key] = value
            except ValueError:
                pass
        listOfWords.append(wordDictionaryList)
        x.toml(listOfWords, path="highlights")


def main(approach=0):
    try:
        approach = int(sys.argv[1])
    except IndexError:
        pass
    assert (approach != 0)
    if approach == 2:
        x = importing.System(False)
        ImproveEnglish(x)
        x.log("[System] Analysis complete")
    elif approach == 1:
        x = importing.System(["data", "learning", "highlights"])
        LearnEnglish(x)
        x.log("[System] New learning began")
        x.openFiles(learning=True, highlights=True)


if __name__ == "__main__":
    main()
