# coding=utf-8
from math import fabs
from socket import *
import threading
import os
import json
import requests
import datetime
import urllib
import base64
from handle import*

class JyTcpServer:
    def __init__(self,port,clientClass):      
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.address = ('', port)
        self.tcp_server_socket.bind(self.address)
        self.tcp_server_socket.listen(1024)     
        self.clientClass=clientClass

    def StartListen(self):
        threading.Thread(target=self.Listen).start()

    def Listen(self):
        print("Server is runing at "+os.getcwd())
        while True:
            client_socket, clientAddr = self.tcp_server_socket.accept()
            client = self.clientClass(client_socket,clientAddr)
            client.StartRun()

class JyTcpClient:
    def __init__(self,client_socket=None,clientAddr=None):
        if client_socket is None:
            self.client_socket=socket(AF_INET, SOCK_STREAM)           
        else:
            self.client_socket=client_socket
            self.clientAddr=clientAddr

    def StartRun(self):
        threading.Thread(target=self.Run).start()

    def Connect(self,serverAddr):
        self.client_socket.connect(serverAddr)

    def Run(self):
        while True:  
            try:          
                recv_data = self.client_socket.recv(1024) 
                if len(recv_data)<=0:
                    break                    
                self.HandleRecvData(recv_data)                                     
            except:
                break      

    def HandleRecvData(self,data):
        print('recv data:', data.decode('utf-8'))
        print(len(data))

    def Send(self,data):
        self.client_socket.send(data)

class JyHttpDefaultClient(JyTcpClient):
    

    def Run(self):
        self.isKeep=True
        while self.isKeep:    
            # recv_data = self.client_socket.recv(1024) 
            # if len(recv_data)<=0:
            #     break    
            # data = recv_data.split(b'\r\n\r\n') 
            # self.handerData = data[0]
            # if len(data)>1:
            #     self.bodyData = data[1]                                    
            # self.HandleRecvData(self.handerData)      
            
            try:          
                recv_data = self.client_socket.recv(1024) 
                if len(recv_data)<=0:
                    break    
                data = recv_data.split(b'\r\n\r\n') 
                self.handerData = data[0]
                if len(data)>1:
                    self.bodyData = data[1]                                    
                self.HandleRecvData(self.handerData)                                    
            except error:
                print(error)
                break     

    def HandleRecvData(self,data):
        msg=data.decode("utf-8")  
        print(msg)      
        self.GetHttpInfo(msg)
        sendData=self.Handel()
        handerData=self.GetHeader(len(sendData))
        self.client_socket.send(handerData)
        self.client_socket.sendall(sendData)
        #print("发送成功")
        self.client_socket.shutdown(SHUT_RDWR)
        #self.isKeep=False
        #self.client_socket.close()

    def GetHttpInfo(self, str):
        ret=str.splitlines()
        msgOneLineArry = ret[0].split(" ")
        self.isKeep=False
        self.recvlen=-1
        if len(msgOneLineArry)<=1:
            self.type=None
            self.recvlen=0
        elif len(msgOneLineArry)>=3:
            self.type=msgOneLineArry[0]
            self.path=msgOneLineArry[1]
            self.path=urllib.parse.unquote(self.path)
        for str in ret:
            strs = str.split(':')
            if strs[0]=="Content-Length":
                self.recvlen = int(strs[1])                 

    def Handel(self):
        fileData=("don`t type").encode("utf-8")
        if self.type==None:
            return fileData
        if self.type.find("GET")>=0:
            fileData=self.DoGet()
        if self.type.find("POST")>=0:
            fileData=self.DoPost()
        return fileData

    def GetHeader(self,dataLen, statusCode = "200 OK"):
        sBuffer = "HTTP/1.1 " + statusCode + "\r\n"
        #sBuffer += "Cache-Control: max-age=3600\r\n"
        sBuffer += "Access-Control-Allow-Origin: *\r\n"
        sBuffer += "Content-Length: " + str(dataLen) + "\r\n\r\n"
        bSendData = sBuffer.encode("utf-8")
        return bSendData
 ###########GET###############
    def DoGet(self):
        fname=os.getcwd()+self.path
        fname=fname.replace("\\","/")
        fileData=("no find file").encode("utf-8")
        if len(self.path)<=1:
            fname=os.getcwd()+"/index.html"
            fname=fname.replace("\\","/")
        if os.path.isfile(fname):
            file = open(fname,'rb')
            fileData = file.read()
            file.close()
        elif os.path.isdir(fname):
            files=",".join(os.listdir(fname)) 
            print(files)
            fileData=files.encode("utf8")
        return fileData



    def DoPost(self):
        if self.bodyData==None:
            self.bodyData=b""
        lenth = self.recvlen-len(self.bodyData)
        print("header___"+str(len(self.bodyData)))
        sendData=""
        if lenth >0:
            while True:               
                data = self.client_socket.recv(self.recvlen-len(self.bodyData))
                self.bodyData=self.bodyData + data
                print("recv__"+str(len(data)))
                if len(self.bodyData)>=self.recvlen:
                    break
                       
        sendData=self.PostHandle(self.bodyData)
        return sendData
    
    ###########POST###############
    def PostHandle(self,data):
        path=os.getcwd()+"/temp"
        path=path.replace("\\","/")
        body = data.split(b'\r\n\r\n')
        bodydata=body[len(body)-1]
        if len(body)>1:            
            headerdata=body[0]
            header = headerdata.decode("utf8")
            filenameFirstIndex=header.find("filename=\"")+len("filename=\"")
            filenameLastIndex=header.find("\"",filenameFirstIndex)
            if filenameFirstIndex>=0:
                path = os.getcwd()+"/"+ header[filenameFirstIndex:filenameLastIndex]
                path=path.replace("\\","/")
        if self.path=="/savefile":
            file = open(path,'wb')         
            file.write(bodydata)
            file.close()
        elif self.path=="/print":
            print(path)
        print(path)
        return (self.path+" ok").encode("utf-8")



class JyHttpHandle(JyHttpDefaultClient):

    def PostHandle(self,data):
        backData="no find".encode("utf8")
        last=self.path.find("/",1)
        if last<1:
            last=len(self.path)
        path=self.path[1:last]  
        try:     
            func=getattr(ServerHandle, path)
        except:
            func=None
        if func is not None:
            backData=func(data)
        elif path=="savefile":
            backData = self.savefile(data)
        elif path=="saveb64file":
            backData = self.saveb64file(data)
        print(backData)
        return backData

    def savefile(self,data):
        backmsg="erro"
        start=self.path.find("/",1)
        if start>1:
            last=len(self.path)               
            backmsg=self.path[start:last]
            file=open(os.getcwd()+backmsg,"wb")
            file.write(data)
            file.close()
        return backmsg.encode("utf-8")
    
    def saveb64file(self,data):
        backmsg="erro"
        start=self.path.find("/",1)
        if start>1:
            last=len(self.path)               
            backmsg=self.path[start:last]
            file=open(os.getcwd()+backmsg,"wb")
            saveData=self.WebUpDataToData(data)
            print(saveData)
            file.write(saveData)           
            file.close()
        return backmsg.encode("utf-8")

    def WebUpDataToData(self, data):
        backmsg="data erro!!"
        s = data.decode()
        sArry=s.split(";")
        datatype = sArry[0]
        dataStr=sArry[1]
        dataBase=dataStr.split(",")
        base=dataBase[0]
        dataBody=dataBase[1]
        decoded_data = base64.b64decode(dataBody)
        return decoded_data

if __name__=='__main__':
    #pass
    #JyTcpServer(80,JyHttpDefaultClient).StartListen()
    JyTcpServer(80,JyHttpHandle).StartListen()
    
