# coding=utf-8
import json
import requests
import datetime
import base64
import threading
import os
import shutil
import time

class ServerHandle:
    def MkDir(data):
        backmsg="dir is have"
        recvdict=json.loads(data.decode("utf8"))    
        path=os.getcwd()+"/"+recvdict["dir"].replace(" ","")
        if os.path.exists(path) is False:
            os.makedirs(path)
            backmsg="completion of creation"
        return backmsg.encode("utf8")
        
    def DeDir(data):
        backmsg="not find dir"
        recvdict=json.loads(data.decode("utf8"))    
        path=os.getcwd()+"/"+recvdict["dir"]
        print(path)
        if os.path.exists(path):
            os.rmdir(path)
            backmsg="completion of del"
        return backmsg.encode("utf8")

    def DeFile(data):
        backmsg="not find File"
        recvdict=json.loads(data.decode("utf8")) 
        path=os.getcwd()+"/"+recvdict["file"]
        print(path)
        if os.path.exists(path):
            os.remove(path)
            backmsg="completion of del"
        return backmsg.encode("utf8")
                   


