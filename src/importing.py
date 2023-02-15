#!/usr/bin/env poetry run python3
# from scamp import *
import os
import glob
import datetime
import logging
import subprocess
import pathlib
import clipboard
from inform import fatal, os_error
import toml
import pytz
import itertools
import openai
import re
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import shelve
import json
import filecmp
import math

class System:
    generalPath = ""
    ge = dict()
    fil = dict()
    folders = {"logs": ".log", "learning": ".toml",
                "highlights": ".toml", "data": ".toml", "photos": ".png",
                "reviews": ".yaml", "docs": ".md", "tasks": ".toml", "readable": ".toml"}
    removeExcessPaths = ["src", "tests"]

    def __init__(self, toCreate, project_folder=False):
        self.generalPath = pathlib.Path(
            __file__).parent.parent.resolve().as_posix()
        if project_folder:
            self.generalPath = project_folder
        self.get()
        self.file(toCreate)
        self.cleaning()
        self.createFiles()

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
                    self.ge[name] + "/*" + self.folders[name])
                path = max(fileOptions, key=os.path.getctime)
                self.fil[name] = path
            except ValueError:
                x = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                path = self.ge[name] + "/" + x + self.folders[name]
                self.fil[name] = path
        # Creates the files
        if names != False:
            for name in names:
                x = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                self.fil[name] = self.ge[name] + "/" + x + self.folders[name]
        return self.fil

    def createFiles(self):
        for path in self.fil.values():
            if os.path.exists(path) == False:
                subprocess.call(["touch", path])
        self.write(reading="New File")
        self.toml(path="highlights")
        self.clipboard()
        self.tasks()
        self.log("Passed Testing")
        return self.fil

    def log(self, log=""):
        """
        Featues
        + Use .log files
        + Logs while preventing needless duplicates
        Issues
        - """
        log_path = self.fil["logs"]
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d-%H-%M',
                            filename=log_path,
                            filemode='a')
        logData = self.write(path="logs")
        if "Configuring Logs" not in logData:
            logging.info(f"Configuring Logs\nLog File: {log_path}\n")
        if (log not in logData or len(log) > 150) and log != "":
            logging.info(log)
        return self.write(path="logs")


    def write(self, reading=True, path="learning", listed=False):
        """
        Features: 
        + Creates file if it doesn't exist
        + Get file as a list of lines or as one string
        Issues: 
        - The file system component is complicated.
        """
        if "/" not in path:
            path = self.fil[path]
        if reading == True:
            try:
                if listed == False:
                    with open(path, 'r', encoding="utf-8") as file:
                        text = file.read()
                elif listed == True:
                    with open(path, 'r', encoding="utf-8") as file:
                        text = file.readlines()
                return text
            except FileNotFoundError:
                with open(path, 'a', encoding="utf-8") as file:
                    file.write("0 = 'New File'")
                return self.write(path=path)
        elif reading != True:
            with open(path, 'w', encoding="utf-8") as file:
                file.write(reading)
            return self.write()

    def openFiles(self, highlights=False, learning=False, logs=False, tasks=False):
        data = False
        if learning:
            data = ["code", "-n", self.fil["learning"]]
        if highlights:
            data = ["code", "-n", self.fil["highlights"]]
        if logs:
            length = len(self.write(path="logs", listed=True))-1
            data=["code", "-n", "-g", f"{self.fil['logs']}:{length}"]
        if tasks:
            length = len(self.write(path="tasks", listed=True))-1
            data = ["code", "-n", "-g", f"{self.fil['tasks']}:{length}"]
        if data:
            self.commandline(data)

    def clipboard(self, reading=True):
        if reading == True:
            text = clipboard.paste()
            return text
        elif reading != True:
            clipboard.copy(reading)

    def cleaning(self, thorough = False):
        """Cleaning up the files
        Features:
        + Removes empty files
        Issues:
        - Does not delete duplicates.
        - Should be improved so that all files are created and tested and that this removes files not meant to be initialized.
        - Shouldn't delete the newest file
        """
        allFiles = []
        for name in self.ge.keys():
            try:
                fileOptions = glob.glob(
                    self.ge[name] + "/*" + self.folders[name])
                allFiles.append(fileOptions)
            except ValueError:
                pass
        allFiles = [item for sublist in allFiles for item in sublist]
        for newFile in self.fil.values():
            allFiles.remove(newFile)
        for fileA, fileB in itertools.combinations(allFiles, 2):
            try:
                content1 = self.write(path=fileA)
                content2 = self.write(path=fileB)
                path1 = pathlib.Path(fileA)
                size1 = path1.stat().st_size
                path2 = pathlib.Path(fileB)
                size2 = path2.stat().st_size
                if thorough:
                    if content1 == content2 or math.isclose(size1, size2, rel_tol=10):
                        last_modified1 = path1.stat().st_mtime
                        last_modified2 = path2.stat().st_mtime
                        if last_modified1 <= last_modified2:
                            os.remove(path1)
                            print("Removed " + str(path1))
                        else:
                            os.remove(path2)
                            print("Removed " + str(path1))
                else:
                    if content1 == content2:
                        last_modified1 = path1.stat().st_mtime
                        last_modified2 = path2.stat().st_mtime
                        if last_modified1 <= last_modified2:
                            os.remove(path1)
                            print("Removed " + str(path1))
                        else:
                            os.remove(path2)
                            print("Removed " + str(path1))
            except FileNotFoundError as e:
                print(e)
        for each in allFiles:
            try:
                if os.path.getsize(each) == 0:
                    os.remove(each)
                    print("Removed " + str(each))
            except FileNotFoundError as e:
                print(e)

    def tasks(self):
        """
        Features
        + Works and is convenient
        + Parses correctly
        Issues
        """
        tasks = subprocess.check_output(
            ["task", "export"]).decode("utf-8")
        tasks = json.loads(tasks)
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
        processedOutput = dict()
        for task in processedTasks:
            processedOutput[task["title"]] = task["date"]
        self.database(["tasks", processedOutput])
        return processedOutput

    def toml(self, reading=None, path="tasks"):
        """
        Features
        + Automatically parses nontomlizable data into tomlizable data and back
        + Failsafes created for testing file path
        + Works with chinese and other languages nicely!
        + Efficient!
        + Works well with past data too. So no significant code changes required.
        + Makes long text readable with line splits, wow!
        Issues:
        - Works best with only strings, dicts, and lists, basically everything else might not work
        """
        if reading == None:
            def listerizer(item):
                if isinstance(item, dict):
                    returnAsList = True
                    for key, value in item.items():
                        try:
                            int(key)
                        except ValueError:
                            returnAsList = False
                    if returnAsList == True:
                        return list(item.values())
                    else:
                        returnDict = dict()
                        for key, value in item.items():
                            returnDict[key] = listerizer(value)
                        return returnDict
                else: 
                    return item
            try:
                with open(self.fil[path], "r", encoding="utf-8") as f:
                    data = toml.load(f)
                parsed_toml = listerizer(data)
                self.database(["tomlUnparsed", parsed_toml])
                return parsed_toml
            except IOError:
                self.log(f"[System] Failed to load {path} path, creating file anew.")
                self.write(reading='0 = "Created new file"\n', path=path)
                return self.toml(path=path)
            except toml.TomlDecodeError:
                self.log("[System] " + self.write(path=path))
                self.toml(reading="Nothing", path=path)
        if reading != None:
            def dicterizer(item):
                if isinstance(item, list):
                    toReturnDict = dict()
                    for num, each in enumerate(item):
                        each = dicterizer(each)
                        if each != None:
                            toReturnDict[f"{num}"] = each
                    return toReturnDict
                elif isinstance(item, str):
                    stringList = re.split("\n", item)
                    if len(stringList) == 1:
                        stringList = stringList[0]
                        if stringList != "":
                            return stringList
                        else:
                            return None
                    elif len(stringList) != 0:
                        return dicterizer(stringList)
                elif isinstance(item, dict):
                    toReturnDict = dict()
                    for key, value in item.items():
                        toReturnDict[key] = dicterizer(value)
                    return toReturnDict
                else: 
                    return item
            reading = dicterizer(reading)
            self.database(["tomlParsed", reading])
            with open(self.fil[path], "w", encoding="utf-8") as f:
                toml.dump(reading, f)
            return self.toml(path=path)

    def ai(self, prompt, presets="creative"):
        """
        Features
        + Run AI
        + Presets - "creative", "precise"
        + Gives only output
        + Saves output to database
        Future Issues to Solve:
        - Slow
        - Alternative AIs not used
        """
        sets = {"creative": [0.9, 0.8, 0.25, 0.95], "precise": [0, 1, 0, 0]}
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=sets[presets][0],
            max_tokens=150,
            top_p=sets[presets][1],
            frequency_penalty=sets[presets][2],
            presence_penalty=sets[presets][3])
        self.database(["ai", prompt, sets[presets], response, response["choices"][0]["text"]])
        return response["choices"][0]["text"]
    
    def scheduler(self, function, date, preset):
        """
        Features
        + Allows for running at a specific time
        Issues
        - Untested
        """
        scheduler = BackgroundScheduler()
        scheduler.s.start()
        scheduler.remove_all_jobs()
        trigger = CronTrigger(
            year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute, second=date.second
        )
        scheduler.add_job(
            foo,
            trigger=trigger,
            args=preset,
            name="Python Automation",
        )
        while True:
            sleep(5)


    def database(self, data=None):
        """
        Features
        + Persistent database
        + Works and is convenient
        Issues
        """
        if data==None:  
            busdata=shelve.open(self.generalPath + "/data.db")
            toReturn = dict(busdata)
            busdata.close()
            return toReturn
        if data!=None:
            with shelve.open(self.generalPath + "/data.db") as db:
                db[datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")] = data
                db.close()
            return self.database()

    def commandline(self, data):
        """
        Features
        + Uses database
        + Works and is convenient
        + Presets
        Issues
        """
        presets = {"chrome", ["google-chrome"]}
        assert (isinstance(data, list))
        try:
            sets = data[0]
            toInsert = presets[sets]
            data.pop(0)
            data = toInsert + data
        except KeyError:
            pass
        output = subprocess.check_output(data)
        output = output.decode()
        self.database(["command", data, output])
        return output