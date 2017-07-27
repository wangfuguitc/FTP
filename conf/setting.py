#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_PATH = os.path.join(BASE_PATH,'home')
USER_PATH = os.path.join(BASE_PATH,'conf','user_data')
sys.path.append(BASE_PATH)
ADDRESS = '0.0.0.0'
PORT = 9999