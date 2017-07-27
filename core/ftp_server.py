#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socketserver
import os
import subprocess
import hashlib
import sys
import json

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from conf import setting

class Ftp_server(socketserver.BaseRequestHandler):
    def login(self):
        #登录认证
        self.md5 = True
        while True:
            self.user = self.request.recv(1024).decode()
            self.password = self.request.recv(1024).decode()
            with open(setting.USER_PATH,'r') as f:
                for line in f:
                    data = line.split()
                    if self.user == data[0] and self.password == data[1]:
                        self.size = data[2]
                        self.dir_path = os.path.join(setting.HOME_PATH, self.user)
                        self.request.send(b'suceess')
                        return
                self.request.send(b'faild')

    def command(self):
        #解析客户端输入的命令并执行相应操作
        while True:
            self.handle = self.request.recv(1024).decode()
            if hasattr(self,self.handle.split()[0]):
                getattr(self,self.handle.split()[0])()
            else:
                self.request.send('命令不存在'.encode(encoding='GBK'))

    def get(self):
        #执行下载操作
        if os.path.isfile(os.path.join(self.dir_path,self.handle.split()[1])):
            file_path = os.path.join(self.dir_path,self.handle.split()[1])
            size = os.path.getsize(file_path)
            if self.md5:
                with open(file_path, 'rb')as file:
                    data_md5 = hashlib.md5(file.read()).hexdigest()
            else:
                data_md5 = None
            base_data = {'size':size,'md5':data_md5}
            self.request.send(json.dumps(base_data).encode())
            resume_size = int(self.request.recv(1024).decode())
            with open(file_path,'rb')as file:
                file.seek(resume_size)
                for line in file:
                    self.request.send(line)
        else:
            self.request.send(b'non-existent')

    def remove(self):
        #执行删除操作
        file_path = os.path.join(self.dir_path, self.handle.split()[1])
        if os.path.isfile(os.path.join(self.dir_path, self.handle.split()[1])):
            os.remove(file_path)
            self.request.send('删除成功'.encode('GBK'))
        elif os.path.isdir(os.path.join(self.dir_path, self.handle.split()[1])):
            try:
                os.rmdir(file_path)
            except:
                self.request.send('目录不为空'.encode('GBK'))
            else:
                self.request.send('删除成功'.encode('GBK'))
        else:
            self.request.send('文件或文件夹不存在'.encode('GBK'))

    def mkdir(self):
        #执行新建目录操作
        file_path = os.path.join(self.dir_path, self.handle.split()[1])
        os.makedirs(file_path)
        self.request.send('创建成功'.encode('GBK'))

    def MD5(self):
        #开启或关闭md5校验
        if self.handle.split()[1] == 'off':
            self.md5 = False
            self.request.send('验证关闭'.encode('GBK'))
        elif self.handle.split()[1] == 'on':
            self.md5 = True
            self.request.send('验证开启'.encode('GBK'))
        else:
            self.request.send('请输入on或off'.encode('GBK'))

    def put(self):
        #执行上传操作
        size_total = 0
        for root, dirs, files in os.walk(os.path.join(setting.HOME_PATH,self.user), True):
            size_total += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        signal = self.request.recv(1024)
        data_dict = json.loads(signal.decode())
        if data_dict['size']+size_total > int(self.size):
            self.request.send(b'over_size')
            return
        else:
            self.request.send(b'no_over')
        file_name = data_dict['name']
        with open(os.path.join(self.dir_path,file_name), 'wb') as file:
            received_size = 0
            while received_size < data_dict['size']:
                data = self.request.recv(4096)
                file.write(data)
                received_size += len(data)
        if self.md5:
            data_md5 = data_dict['md5']
            with open(os.path.join(self.dir_path,file_name), 'rb') as file:
                file_md5 = hashlib.md5(file.read()).hexdigest()
                if data_md5 == file_md5:
                    self.request.send('md5校验通过'.encode())
                else:
                    self.request.send('md5校验不通过'.encode())

    def dir(self):
        #打印当前目录
        data = subprocess.Popen(self.handle,shell=True,stdout=subprocess.PIPE,cwd=self.dir_path)
        print(self.dir_path)
        data = data.stdout.read().decode('GBK').replace(setting.HOME_PATH,'').encode('GBK')
        self.request.send(data)

    def cd(self):
        #切换目录
        path = self.handle.split()[1]
        if path == '..' and self.dir_path == os.path.join(setting.HOME_PATH, self.user):
            self.request.send('已经是根目录'.encode('GBK'))
        elif path == '.':
            self.request.send(self.dir_path.replace(setting.HOME_PATH,'').encode('GBK'))
        elif path == '..':
            dir_list = self.dir_path.split('\\')
            dir_list.pop()
            self.dir_path = '\\'.join(dir_list)
            self.request.send(self.dir_path.replace(setting.HOME_PATH, '').encode('GBK'))
        elif os.path.isdir(os.path.join(self.dir_path,path)):
            self.dir_path = os.path.join(self.dir_path,path)
            self.request.send(self.dir_path.replace(setting.HOME_PATH,'').encode('GBK'))
        else:
            self.request.send('目录不存在'.encode('GBK'))

    def handle(self):
        self.login()
        self.command()

def main():
    server = socketserver.ThreadingTCPServer((setting.ADDRESS,setting.PORT),Ftp_server)
    server.serve_forever()
