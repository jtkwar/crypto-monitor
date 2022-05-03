# -*- coding: utf-8 -*-
"""
Created on Sun May  1 21:58:30 2022

@author: stark

Packages required for running scripts.
"""
# Import Libraries
import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime
import email, smtplib, ssl
from typing import *

# MMS Messages
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

# Web scraping Libraries
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'

from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# GLOBAL VARIABLES
SMS         = "vtext.com"
MMS         = "vzpix.com"
MMS_SUPPORT = True
mime_maintype = "image"
mime_subtype = "png"

URL = "https://coinmarketcap.com/"
COINS = ['BTC', 'ETH', 'SHIB', 'DOGE']
urls_dict = {"BTC":"https://coinmarketcap.com/currencies/bitcoin/",
             "ETH":"https://coinmarketcap.com/currencies/ethereum/",
             "SHIB":"https://coinmarketcap.com/currencies/shiba-inu/",
             "DOGE":"https://coinmarketcap.com/currencies/dogecoin/"
             }

BASE_PATH = os.getcwd()