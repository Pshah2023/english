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
import shelvef
import json
import filecmp
import math
import pyppeteer
import asyncio
from dateutil import parser


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
        print("[System] Initiated and passed testing")

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
        self.write(path="docs")
        self.toml(path="learning")
        self.clipboard()
        self.tasks()
        # self.watch()
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

    def openFiles(self, learning=False, logs=False, docs=False):
        if learning:
            self.commandline(["code", "-n", self.fil["learning"]])
        if logs:
            length = len(self.write(path="logs", listed=True))-1
            self.commandline(["code", "-n", "-g", f"{self.fil['logs']}:{length}"])
        if docs:
            self.commandline(["code", "-n", self.fil["docs"]])
        
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
            try:
                allFiles.remove(newFile)
            except:
                pass
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
        self.database("tasks", processedOutput)
        return processedOutput

    def toml(self, reading=None, path="learning"):
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
                        return [listerizer(item) for item in list(item.values())]
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
                return parsed_toml
            except IOError:
                self.log(f"[System] Failed to load {path} path, creating file anew.")
                self.write(reading='0 = "Created new file"\n', path=path)
                return self.toml(path=path)
            except toml.TomlDecodeError:
                self.log("[System] " + self.write(path=path))
                self.toml(reading="Failed with TomlDecodeError", path=path)
        if reading != None:
            def dicterizer(item):
                if isinstance(item, list):
                    toReturnDict = dict()
                    for num, each in enumerate(item):
                        each = dicterizer(each)
                        if each != None:
                            toReturnDict[f"{num}"] = each
                    if len(toReturnDict.items()) != 0:
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
                    if len(toReturnDict.items()) != 0:
                        return toReturnDict
                else: 
                    return item
            self.database("toml", reading)
            reading = dicterizer(reading)
            with open(self.fil[path], "w", encoding="utf-8") as f:
                toml.dump(reading, f)
            return self.toml(path=path)

    def ai(self, prompt, presets="creative"):
        """
        Features
        + Run AI
        + Presets - "creative", "precise"
        + Gives only output
        + Saves output to database`
        Future Issues to Solve:
        - Slow
        - Alternative AIs not used
        """
        openai.api_key = "my updated key won't be here."
        data = self.database("ai")
        data = {item[0]: item[2] for item in data}
        try:
            data = data[prompt]
            return data
        except KeyError or SyntaxError:
            pass
        sets = {"creative": [0.9, 0.8, 0.25, 0.95], "precise": [0, 1, 0, 0]}
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=sets[presets][0],
            max_tokens=150,
            top_p=sets[presets][1],
            frequency_penalty=sets[presets][2],
            presence_penalty=sets[presets][3])
        self.database("ai", [prompt, presets, response["choices"][0]["text"]])
        return response["choices"][0]["text"]
    
    def database(self, category, data=None):
        """
        Features
        + Persistent database
        + Works and is convenient
        Issues
        """
        if data != {} and data != [] and data != "":
            with shelve.open(self.generalPath + "/data.db", writeback=True) as db:
                try:
                    check = list(db[category])
                except:
                    db[category] = list()
                    check = list()
                    print(f"[System] [Database] Created category {category}")
                if isinstance(check, list):
                    if data not in check and data != None:
                        if len(data) != 0:
                            if isinstance(data, str) and data.strip() != "":
                                check.append(data)
                                db[category] = check
                            else:
                                check.append(data)
                                db[category] = check
                        else:
                            print(f"[System] [Database] {category} Data is empty")
                    else:
                        print(f"[System] [Database] {category} Data already saved")
        else:
            print(f"[System] [Database] {category} Data is empty")
        return check

    def commandline(self, data):
        """
        Features
        + Uses database
        + Works and is convenient
        + Presets
        Issues
        """
        presets = {"chrome": ["google-chrome"]}
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
        self.database("terminal", [data, output])
        return output

    def chrome(self, data):
        async def toRun():
            # launch chromium browser in the background
            browser = await pyppeteer.launch(headless=False, executablePath='/usr/bin/google-chrome')
            
            # open a new tab in the browser
            page = await browser.newPage()
            # add URL to a new page and then open it
            await page.goto("https://www.medfield.net/o/medfield-high-school")
            # create a screenshot of the page and save it
            await page.screenshot({"path": "python.png"})
            # close the browser
            await browser.close()
        asyncio.run(toRun())
    
    def watch(self, afkData=False, chromeData = False):
        """
        Features
        + Works and is convenient
        + Parses correctly
        Issues
        """
        raw = subprocess.check_output(
            ["wget", "-qO-", "http://localhost:5600/api/0/export"]).decode("utf-8")
        raw = json.loads(raw)
        # The structure of raw
        # {'buckets':
        #   {
        #     'aw-watcher-window_pranit': ,
        #     {
        #       'id': 'aw-watcher-window_pranit',
        #       'created': date of first data captured,
        #       'name': None,
        #       'type': 'currentwindow,
        #       'client': 'aw-watcher-window',
        #       'hostname': 'pranit',
        #       'events': 
        #       [ # First is latest
        #         'timestamp': '%Y-%m-%dT%H:%M:%S.%f%z',
        #         'duration': float, # in seconds
        #         'data':
        #         {
        #           'app': string, # app name as string, e.g. 'Code'
        #           'title': 'importing.py - english - Visual Studio Code'
        #         }
        #       ], # Last is oldest
        #     }
        #     'aw-watcher-afk_pranit': ,
        #     {
        #       'id': 'aw-watcher-afk_pranit',
        #       'created': date of first data captured,
        #       'name': None, 
        #       'type': "afkstatus",
        #       'client': 'aw-watcher-afk',
        #       'hostname': 'pranit',
        #       'events': 
        #       [ # First is latest
        #         'timestamp': '%Y-%m-%dT%H:%M:%S.%f%z',
        #         'duration': float, # in seconds
        #         'data':
        #         {
        #           'status': 'not-afk' # or 'afk'
        #         }
        #       ], # Last is oldest
        #     }
        #     'aw-watcher-web-chrome': 
        #     {
        #       'id': 'aw-watcher-web-chrome',
        #       'created': date of first data captured,
        #       'name': None,
        #       'type': ''web.tab.current',
        #       'client': 'aw-client-web',
        #       'hostname': 'pranit',
        #       'events': 
        #       [ # First is latest
        #         'timestamp': '%Y-%m-%dT%H:%M:%S.%f%z',
        #         'duration': float, # in seconds
        #         'data':
        #         {
        #           'url': 'https://docs.activitywatch.net/en/latest/buckets-and-events.html',
        #           'title': 'Data model',
        #           'audible': False,
        #           'incognito': False,
        #           'tabCount': 12
        #         }
        #       ], # Last is oldest
        #     }
        #   } 
        # }
        windowWatch = self.database("windowWatch")
        date = datetime.datetime.now() - datetime.timedelta(minutes=1)
        recollect = True
        try:
            if parser.parse(windowWatch[-1].decode().split("...")[0]) > date.replace(second=0, microsecond=0):
                recollect = False
        except IndexError:
            pass
        if recollect:
            print("[System] [Activity Watch] Recollecting activity data")
            for each in raw["buckets"]["aw-watcher-window_pranit"]["events"]:
                date = parser.parse(each["timestamp"]).astimezone(pytz.timezone("US/Eastern"))
                date = date.replace(microsecond=0, tzinfo=None)
                duration = datetime.timedelta(seconds=each['duration'])
                title = each['data']['title']
                data = [str(date), str(duration), title]
                data = "...".join(data).encode()
                if str(duration) != "00:00:00" and data not in windowWatch:
                    self.database("windowWatch", data)
            if afkData:
                afkData = self.database("afkWatch")
                for each in raw["buckets"]["aw-watcher-afk_pranit"]["events"]:
                    date = parser.parse(each["timestamp"]).astimezone(pytz.timezone("US/Eastern"))
                    date = date.replace(microsecond=0, tzinfo=None)
                    duration = datetime.timedelta(seconds=each['duration'])
                    status = each['data']['status']
                    if str(duration) != "00:00:00" and status != 'not-afk':
                        data = [str(date), str(duration)]
                        data = "...".join(data)
                        if data not in afkData:
                            self.database("afkWatch", data)
            if chromeData:
                chromeData = self.database("chromeWatch")
                for each in raw["buckets"]["aw-watcher-web-chrome"]["events"]:
                    date = parser.parse(each["timestamp"]).astimezone(pytz.timezone("US/Eastern"))
                    date = date.replace(microsecond=0, tzinfo=None)
                    duration = datetime.timedelta(seconds=each['duration'])
                    title = each['data']['title']
                    data = [str(date), str(duration), title]
                    data = "...".join(data).encode()
                    if str(duration) != "00:00:00" and data not in chromeData:
                        self.database("chromeWatch", data)
        else:
            print("[System] [Activity Watch] Not recollecting data")
        allData = [self.database("windowWatch"), self.database("afkWatch"), self.database("chromeWatch")]
        windowData = []
        for item in allData[0]:
            item = item.decode().split("...")
            item = [item[0], item[1], item[2]]
            windowData.append(data)
        afkData = []
        for item in allData[1]:
            item = item.decode().split("...")
            item = [item[0], item[1]]
            afkData.append(data)
        chromeData = []
        for item in allData[2]:
            item = item.decode().split("...")
            item = [item[0], item[1], item[2]]
            chromeData.append(data)
        allData = [windowData, afkData, chromeData]
        return allData
