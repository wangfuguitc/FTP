#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from core import ftp_server

if __name__ == '__main__':
    ftp_server.main()