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

    def __init__(self, x, level):
        if level == 0:
            inp = x.clipboard()
            if len(inp) < 500:
                inp = x.write(path="docs")
            text = self.parse(inp)
            toLearn = []
            for num, s in enumerate(text):
                toLearn.append(self.highlights(s, num))
            x.toml(toLearn, path="learning")
            x.database("text", data=toLearn)
        toLearn = x.toml(path="learning")
        toLearn = [item for item in toLearn if len(item) == 3 and "highlights" in item[0] and "predictions" in item[2]]
        listOfWords = []
        listOfListOfWords = []
        for item in toLearn:
            if len(item) == 3 and "highlights" in item[0] and "predictions" in item[2]:
                try:
                    item = item[0].split("s: ")[1]
                    item = re.split(", ", item)
                    item = [string.strip() for string in item if string != "" and isinstance(string, str) and string.strip() != ""]
                    listOfListOfWords.append(item)
                    for each in item:
                        if each != "" and isinstance(each, str) and each.strip() != "":
                            listOfWords.append(each)
                except KeyError:
                    pass
        toLearn.append(listOfWords)
        toLearn.append([" - ".join(listed) for listed in listOfListOfWords])
        toLearn.append(self.processAnalysis(listOfListOfWords))
        toLearn.append(self.processAnalysis(listOfListOfWords))
        toLearn.append(self.numericAnalysis(listOfWords))
        toLearn.append(self.numericProcessAnalysis(listOfWords))
        x.toml(toLearn, path="learning")

    def parse(self, inp):
        language = detect(inp)
        if language == "en":
            inp = re.sub("。", ". ", inp)
            inp = re.sub("[ ]+", " ", inp)
            inp = re.sub("\n\n", " ¶ ", inp)
            inp = re.sub("¶[ ]+¶", "¶", inp)
            inp = re.sub(r"\n", " ", inp)
            inp = re.sub(r"\s\s+", " ", inp)
            inp = re.sub("[ ]+", " ", inp)
            self.text = nltk.tokenize.sent_tokenize(inp)
        if language == "zh-cn":
            inp = StanfordSegmenter()
            print("Chinese text is unimplemented")
            exit()
        return self.text
        

    def highlights(self, s, num, out=""):
        """Guess the important words and classify them
        The format is storage, category, and emotion. Previously.
        Not it is Positives, Differences, Cues, and Efficiency."""
        out = ["highlights: "]
        out.append(s)
        out.append("predictions: ")
        return out

    def numericAnalysis(self, words):
        organizedList = [[], [], []]
        for each in words:
            if isinstance(each, str):
                if "0" in each:
                    organizedList[0].append(each)
                if "1" in each:
                    organizedList[1].append(each)
                if "2" in each:
                    organizedList[2].append(each)
        organizedList = [li for li in organizedList if len(li) != 0]
        return organizedList

    def processAnalysis(self, iterable):
        dictionary = dict()
        for num, thing in enumerate(iterable):
            try:
                if isinstance(thing, list):
                    dictionary[" - ".join(thing)] = " - ".join(iterable[num+1])
                elif isinstance(thing, str):
                    dictionary[thing] = iterable[num+1]
            except IndexError:
                pass
        return dictionary

    def numericProcessAnalysis(self, words):
        wordDictionary = self.processAnalysis(words)
        wordDictionaryList = [dict(), dict(), dict(), dict(), dict(), dict(), dict()]
        for key, value in wordDictionary.items():
            try:
                if int(key[-1]) + int(value[-1]) == 4:
                    number = 6
                elif int(key[-1]) + int(value[-1]) == 3:
                    number = 5
                elif int(key[-1]) + int(value[-1]) == 2:
                    number = 3
                elif int(key[-1]) + int(value[-1]) == 1:
                    number = 1
                elif int(key[-1]) + int(value[-1]) == 0:
                    number = 0
                if int(key[-1]) < int(value[-1]):
                    number += 1
                wordDictionaryList[number][key] = value
            except ValueError:
                pass
        toReturn = []
        for dictionary in wordDictionaryList:
            if len(dictionary):
                toReturn.append(dictionary)
        return toReturn


def main(approach=0):
    try:
        approach = int(sys.argv[1])
    except IndexError:
        pass
    assert (approach != 0)
    if approach == 2:
        x = importing.System(False)
        LearnEnglish(x, 4)
        x.log("[System] Analysis complete at " + str(datetime.now()))
    elif approach == 1:
        x = importing.System(["learning"])
        LearnEnglish(x, 0)
        x.log("[System] New learning began at " + str(datetime.now()))
        x.openFiles(learning=True)


if __name__ == "__main__":
    main()
