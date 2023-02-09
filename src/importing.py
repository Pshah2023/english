#!/usr/bin/env poetry run python3
# from scamp import *
import os
import glob
import datetime
import logging
import subprocess
import pathlib
import yaml
import json
import clipboard
from inform import fatal, os_error
from yaml import CLoader as Loader, CDumper as Dumper
import pytz


class System:
    generalPath = ""
    ge = dict()
    fil = dict()
    fileType = {"logs": ".log", "learning": ".md",
                "highlights": ".yaml", "data": ".json", "photos": ".png",
                "reviews": ".yaml", "docs": ".md", "tasks": ".json"}
    removeExcessPaths = ["src", "tests"]

    def __init__(self, toCreate, project_folder=False):
        self.generalPath = pathlib.Path(
            __file__).parent.parent.resolve().as_posix()
        if project_folder:
            self.generalPath = project_folder
        self.get()
        self.file(toCreate)
        self.docs()
        self.createFiles()
        self.log()
        self.yaml()
        self.cleaning()

    def get(self, remove=False):
        if remove == False:
            remove = self.removeExcessPaths
        for name in os.listdir(self.generalPath):
            if "." not in name:
                self.ge[name] = str(os.path.join(
                    str(self.generalPath), str(name)))
        try:
            for each in remove:
                del self.ge[each]
        except KeyError:
            pass
        return self.ge

    def file(self, names=False):
        # Begins with the general paths
        for name in self.ge.keys():
            self.fil[name] = self.ge[name]
        # Finds the file or creates it
        for name in self.fil.keys():
            try:
                fileOptions = glob.glob(
                    self.ge[name] + "/*" + self.fileType[name])
                path = max(fileOptions, key=os.path.getctime)
                self.fil[name] = path
            except ValueError:
                x = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                path = self.ge[name] + "/" + x + self.fileType[name]
                self.fil[name] = path
        # Creates the files
        if names != False:
            for name in names:
                x = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                self.fil[name] = self.ge[name] + "/" + x + self.fileType[name]
        return self.fil

    def createFiles(self):
        for path in self.fil.values():
            if os.path.exists(path) == False:
                subprocess.call(["touch", path])
        self.write()
        self.json()
        self.yaml()
        self.clipboard()
        self.tasks()
        self.log(
            "[System] Passed testing of data, highlights, tasks, and learning files")
        return self.fil

    def log(self, log=""):
        """Use .log files"""
        log_path = self.fil["logs"]
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d-%H-%M',
                            filename=log_path,
                            filemode='a')
        if "Configuring Logs" not in self.write(path="logs"):
            logging.info(f"Configuring Logs\nLog File: {log_path}\n")
        if log != "":
            logging.info(log)
        return self.write(path="logs")

    def yaml(self, reading=True, path="highlights"):
        if reading == True:
            try:
                with open(self.fil[path], 'r', encoding="utf-8") as file:
                    highlights = yaml.load(file, Loader=Loader)
                return highlights
            except IOError:
                text = self.write(path=path)
                self.log(f"[System] Failed to load {path}")
                self.log(f"[System] Previous {path}: {text}")
                with open(self.fil[path], 'w', encoding="utf-8") as file:
                    yaml.dump(["Failed"], file)
        elif reading != True:
            with open(self.fil[path], 'w', encoding="utf-8") as file:
                yaml.dump(reading, file)
            return self.yaml()

    def write(self, reading=True, path="learning", listed=False):
        if reading == True:
            try:
                if listed == False:
                    with open(self.fil[path], 'r', encoding="utf-8") as file:
                        text = file.read()
                elif listed == True:
                    with open(self.fil[path], 'r', encoding="utf-8") as file:
                        text = file.readlines()
                return text
            except IOError:
                with open(self.fil[path], 'a', encoding="utf-8") as file:
                    file.write("")
                return ""
        elif reading != True:
            with open(self.fil[path], 'w', encoding="utf-8") as file:
                file.write(reading)
            return self.write()

    def chineseFixer(self, path, fixer=True):
        if fixer == True:
            with open(self.fil[path], 'r') as f:
                text = f.read()
            text = text.encode("utf8").decode("unicode-escape")
            print(text)
            with open(self.fil[path], "w") as f:
                f.write(text)
        elif fixer == False:
            with open(self.fil[path], 'r') as f:
                text = f.read()
            text = text.encode("utf8").decode("utf8")
            print(text)
            with open(self.fil[path], "w") as f:
                f.write(text)

    def docs(self, path="", listed=False):
        if path == "":
            try:
                fileOptions = glob.glob(
                    self.ge["docs"] + "/*" + self.fileType["docs"])
                path = max(fileOptions, key=os.path.getctime)
                self.fil["docs"] = path
            except ValueError:
                self.log("Error: No docs found")
        with open(self.fil["docs"], 'r', encoding="utf-8") as file:
            text = file.read()
        return text

    def openFiles(self, highlights=False, learning=False):
        if learning:
            subprocess.call(
                ["code", "-n", self.fil["learning"]])
        if highlights:
            subprocess.call(
                ["code", "-n", self.fil["highlights"]])

    def json(self, reading=True, path="data"):
        if reading == True:
            try:
                with open(self.fil[path], 'r', encoding="utf-8") as file:
                    data = json.load(file)

                return data
            except IOError and json.decoder.JSONDecodeError:
                self.log(log=f"[System] IOError with json with path '{path}'")
                text = self.write(path=path)
                if text != "":
                    self.log(f"[System] Previous data: {text}")
                    with open(self.fil[path], 'w', encoding="utf-8") as file:
                        json.dump(["Failed To Process (Previous data in next index)", text], indent=4,
                                  separators=(' , ', ' : '), fp=file)
                elif text == "":
                    with open(self.fil[path], 'w', encoding="utf-8") as file:
                        json.dump([""], indent=4,
                                  separators=(' , ', ' : '), fp=file)
                return self.json(path="tasks")
        elif reading != True:
            with open(self.fil[path], 'w') as file:
                json.dump(reading, indent=4,
                          separators=(' , ', ' : '), fp=file)
            return self.json(path="tasks")

    def clipboard(self, reading=True):
        if reading == True:
            text = clipboard.paste()
            return text
        elif reading != True:
            clipboard.copy(reading)

    def cleaning(self):
        """Cleaning up the files"""
        allFiles = []
        for name in self.ge.keys():
            try:
                fileOptions = glob.glob(
                    self.ge[name] + "/*" + self.fileType[name])
                allFiles.append(fileOptions)
            except ValueError:
                pass
        allFiles = [item for sublist in allFiles for item in sublist]
        for each in allFiles:
            if os.path.getsize(each) == 0 or os.path.getsize(each) == 1:
                os.remove(each)

    def tasks(self):
        tasks = subprocess.check_output(
            ["task", "export"]).decode("utf-8")
        tasks = json.loads(tasks)
        self.log(f"[System] There is {len(tasks)} tasks")
        processedTasks = []
        for task in tasks:
            processedTask = dict()
            if task["status"] == "pending":
                processedTask["title"] = task["description"]
                date = task["modified"]
                date = datetime.datetime.strptime(
                    date + " UTC+0000", '%Y%m%dT%H%M%SZ %Z%z').astimezone(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d-%H-%M")
                processedTask["date"] = date
                try:
                    allDetails = []
                    for detail in task["annotations"]:
                        allDetails.append(detail["description"])
                    processedTask["details"] = allDetails
                except KeyError:
                    pass
                processedTasks.append(processedTask)
        processedTasks.reverse()
        output = self.json(reading=processedTasks, path="tasks")
        processedOutput = []
        for task in output:
            task["date"] = datetime.datetime.strptime(
                task["date"], '%Y-%m-%d-%H-%M')
            processedOutput.append(task)
        return processedOutput
