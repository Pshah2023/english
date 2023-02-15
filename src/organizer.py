#!/usr/bin/env poetry run python3
"""This file will provide a class for measuring accuracy and a class for organizing."""
import datetime
import importing
import sys
import openai
import urllib.parse
openai.api_key = "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"


class Accuracy:
    """Will provide accuracy remarks."""

    def __init__(self, x):
        pass

class Organizer:
    """Will attempt to use an AI schedule with taskwarrior to organize homework assignments to increases accuracy faster."""

    tasks = dict()
    calendar = ""
    courseList = []

    def __init__(self, x, noAI = False):
        self.tasks = x.tasks()
        self.schedule(x, noAI=noAI)
        x.clipboard(reading="timew start")
        x.commandline(["google-chrome", "https://calendar.google.com/calendar/u/0/r"])
        print(x.commandline(["gcalcli", "conflicts"]))


    def schedule(self, x, noAI=False):
        date = datetime.datetime.now()
        minute = 15 * round(date.minute/15)
        if minute == 60:
            date = date.replace(hour=date.hour+1)
        elif minute != 60:
            date = date.replace(minute=minute)
        eventLength = datetime.timedelta(hours=1, minutes=15)
        breakLength = datetime.timedelta(minutes=15)
        courseList = []
        if noAI == False:    
            for num, task in enumerate(self.tasks.keys()):
                courseList.append(self.courses(x, task, noAI=noAI))
        elif noAI == True:
            courseList = self.tasks.keys()
        dateTimeCourses = [] # List of lists
        for num, course in enumerate(courseList):
            date = date + num * eventLength + num * breakLength
            dateTimeCourses.append([course, date, eventLength])
            date = date + eventLength
            dateTimeCourses.append(["Break", date, breakLength])
        outputs = []
        for title, date, length in dateTimeCourses:
            url = "https://www.google.com/search?q="+urllib.parse.quote_plus(title)
            arguments = ["gcalcli", "add", "--calendar", "0", "--title", f"'{title}'", "--where", "home", "--when", f"'{date.strftime('%m/%d/%Y %H:%M:%S')}'", "--duration", str(round(length.total_seconds() / 60)), "--reminder", "1", "--description", f"Search {url}"]
            outputs.append(x.commandline(arguments))
        self.calendar = outputs
        return self.calendar

    def courses(self, x, category, examples=0, noAI = False):
        
        prompt = "Create course names under music.\n\nLate Night Music Production\nMusic Theory and Analysis\nMusic and Lyric Writing\nMusical Theater Writing\nMusic Composition for Film and Television\nMusic Performance Techniques\nJazz Improvisation and Performance\nPopular Music History and Styles\nIntroduction to Electronic Music Production\nWorld Music Studies\n\n"
        if examples >= 0 or noAI == True:
            prompt += "Create course names under python.\nIntroduction to Python Programming\nObject-Oriented Python Programming\nPython Data Structures and Algorithms\nAdvanced Python Web Development\nPython GUI Programming\nPython for Data Science and Machine Learning\nPython Scripting and Automation\nWeb Scraping with Python\nNatural Language Processing with Python\nApplied Statistics in Python\n\n"
        if examples >= 1:
            prompt += "Create course names under writing.\nCreative Writing\nTechnical Writing\nGrant Writing\nProfessional Copywriting\nBusiness Writing\nScientific Writing\nFiction Writing\nNon-Fiction Writing\nEssay and Opinion Writing\nJournalism and News Reporting\n\n"
        if noAI == False:
            prompt += "Create course names under " + category + ".\n\n"
            response = x.ai(prompt)
            response = response.split('\n')
            forPrint = "\n"
            for num, each in enumerate(response):
                forPrint += str(num) + ". " + each + "\n"
            print(forPrint)
            toOutput = input("What one (as a number) do you prefer? ")
            prompt += forPrint + "\nWhat one (as a number) do you prefer? " + toOutput
            toOutput = int(toOutput)
        self.courseList.append(prompt)
        if noAI == False:
            return response[toOutput]

    def data(self, x, noAI = False):
        y = x.tasks()
        if noAI == True:
            self.courses(x, "Whatever", noAI=True)
        y["courseList"] = "\n".join(self.courseList).split("\n")
        y["schedule"] = self.calendar.split("\n")
        return x.toml(reading=y)



def main():
    """AI and nonAI use seperated, 2 is without AI, 1 is with"""
    approach = 0
    try:
        approach = int(sys.argv[1])
    except IndexError:
        pass
    assert (approach != 0)
    x = importing.System(False)
    if approach == 2:
        
        Accuracy(x)
        Organizer(x, noAI=True)
    if approach == 1:
        Accuracy(x)
        Organizer(x)    


if __name__ == "__main__":
    main()
