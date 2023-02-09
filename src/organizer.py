#!/usr/bin/env poetry run python3
"""This file will provide a class for measuring accuracy and a class for organizing."""
import datetime
import importing
import os
import openai

openai.api_key = "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"


class Accuracy:
    """Will provide accuracy remarks."""
    tasks = []

    def __init__(self, x):
        self.tasks = x.tasks()
        x.log(self.tasks)
        print(self.schedule())

    def schedule(self):
        prompt = "Prompt: Make a schedule with the events of Lord of the Flies reading, and Essay for Jon Miller, starting from 02/08/2023 at approximately 17: 30. Let each event have length 1: 15 hours and include breaks of length 0: 15 minutes between each event. Repeat events until you have 8 events.\n\nSchedule: "
        prompt += """\n02/08/2023 17:30-18:45: Read Lord of the Flies\n02/08/2023 18:45-19:00: 15 minute break\n02/08/2023 19:00-20:15: Write Essay for Jon Miller\n02/08/2023 20:15-20:30: 15 minute break\n02/08/2023 20:30-21:45: Read Lord of the Flies\n02/08/2023 21:45-22:00: 15 minute break\n02/09/2023 00:00-01:15: Write Essay for Jon Miller\n02/09/2023 01:15-01:30: 15 minute break"""
        prompt += "\n\nPrompt: Make a schedule with the events of "
        for num, task in enumerate(self.tasks):
            prompt += task["title"] + ", "
            num += 2
            if len(self.tasks) == num:
                prompt += "and "
        date = datetime.datetime.now()
        date = date.replace(minute=15 * round(date.minute/15))
        prompt += "starting from " + \
            date.strftime("%m/%d/%Y at approximately %H:%M") + ". "
        prompt += "Let each event have length 1:15 hours and include breaks of length 0:15 minutes between each event."
        prompt += " Repeat events until you have 8 events."
        prompt += "\n\nSchedule: "
        prompt += "\n" + date.strftime("%m/%d/%Y %H:%M-")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.0,
            max_tokens=175,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.0
        )
        return (prompt + response["choices"][0]["text"])


class Organizer:
    """Will attempt to use an AI schedule with taskwarrior to organize homework assignments to increases accuracy faster."""

    tasks = []

    def __init__(self, x):
        self.tasks = x.tasks()


def main():
    x = importing.System(False)
    Accuracy(x)
    Organizer(x)


if __name__ == "__main__":
    main()
