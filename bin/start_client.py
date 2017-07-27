#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import os
import hashlib
import json
import sys

class Ftp_client():
    def connect(self):
        #与服务端建立连接
        while True:
            self.client=socket.socket()
            address = input('请输入ftp服务器地址:')
            port = input('请输入ftp服务器端口号:')
            if len(address)>20 or len(port)>20:
                print('输入不能大于20个字符')
                continue
            if address and port.isdigit():
                try:
                    self.client.connect((address,int(port)))
                except :
                    print('连接失败,请重新输入')
                    continue
                else:
                    print('连接成功')
            else:
                print('输入格式不对,请重新输入')
                continue
            break

    def login(self):
        #用户登录认证
        self.md5 = True
        while True:
            user = input('请输入用户名')
            password = input('请输入密码')
            if len(user)>20 or len(password)>20:
                print('输入不能大于20个字符')
                continue
            if not (user and password):
                print('输入不能为空')
                continue
            self.client.send(user.encode())
            self.client.send(password.encode())
            signal = self.client.recv(1024)
            if signal.decode() == 'suceess':
                print('登录成功')
                break
            if signal.decode() == 'faild':
                print('登录失败')

    def handle(self):
        #解析用户输入的命令并执行相应动作
        while True:
            command = input('请输入命令')
            if len(command)>100:
                print('输入不能大于100个字符')
                continue
            if not command:
                print('不能为空')
                continue
            if command == 'quit':
                self.client.close()
                print('连接关闭')
                break
            elif hasattr(self,command.split()[0]):
                if len(command.split()) < 2:
                    print('请输入文件或目录,on或off')
                    continue
                self.client.send(command.encode())
                getattr(self, command.split()[0])(command)
            else :
                if command in ('cd','remove','mkdir') and len(command.split()) < 2:
                    print('请输入文件或目录')
                    continue
                self.client.send(command.encode())
                data = self.client.recv(1024)
                print(data.decode('GBK'))

    def MD5(self,command):
        #开启或关闭md5校验
        data = self.client.recv(1024)
        if command.split()[1] == 'on':
            self.md5  = True
        if command.split()[1] == 'off':
            self.md5 = False
        print(data.decode('GBK'))

    def get(self,command):
        #执行下载操作
        signal = self.client.recv(1024)
        if signal.decode() == 'non-existent':
            print('文件不存在')
            return
        else:
            if os.path.isfile(command.split()[1].split('\\')[-1]):#判断本地是否已经存在同名文件
                resume = input('是否断点续传(yes/no)')
                if resume == 'yes':
                    size_resume = os.path.getsize(command.split()[1].split('\\')[-1])
                    self.client.send(str(size_resume).encode())
                elif resume == 'no':
                    os.remove(command.split()[1].split('\\')[-1])
                    self.client.send(b'0')
                    size_resume = 0
            else:
                self.client.send(b'0')
                size_resume = 0
            data_dict = json.loads(signal.decode())
            with open(command.split()[1].split('\\')[-1],'ab') as file:
                received_size = size_resume
                while received_size < data_dict['size']:
                    data = self.client.recv(4096)
                    file.write(data)
                    received_size += len(data)
                    num = int(received_size / data_dict['size'] * 100)
                    print('\r [%-100s]%d%%' % ('=' * num, num),end='')
                else:
                    print('\nget完成')
            if self.md5:
                with open(command.split()[1].split('\\')[-1], 'rb') as file:
                    file_md5 = hashlib.md5(file.read()).hexdigest()
                    if data_dict['md5'] == file_md5:
                        print('md5校验通过')
                    else:
                        print('md5校验不通过')

    def put(self,command):
        #执行上传操作
        if os.path.isfile(command.split()[1]):
            file_name = command.split()[1].split('\\').pop()
            size = os.path.getsize(command.split()[1])
            if self.md5:
                with open(command.split()[1], 'rb')as file:
                    data_md5 = hashlib.md5(file.read()).hexdigest()
            else:
                data_md5 = None
            base_data = {'size': size, 'md5': data_md5,'name':file_name}
            self.client.send(json.dumps(base_data).encode())
            signal = self.client.recv(1024).decode()
            if signal == 'over_size':
                print('超出允许的最大磁盘空间')
                return
            elif signal == 'no_over':
                with open(command.split()[1],'rb')as file:
                    send_size = 0
                    for line in file:
                        self.client.send(line)
                        total_size = size
                        send_size += len(line)
                        num = int(send_size / total_size * 100)
                        print('\r [%-100s]%d%%' % ('=' * num, num), end='')
                print('\nput完成')
                if self.md5:
                    print(self.client.recv(1024).decode())

        else:
            print('文件不存在')


if __name__ == '__main__':
    ftp = Ftp_client()
    ftp.connect()
    ftp.login()
    ftp.handle()