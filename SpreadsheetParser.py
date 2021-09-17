import os
import datetime
import time
import re
from slackclient import SlackClient
from DataBase import DataBase
import sys
import platform
import docx
import nltk
import requests
import pandas as pd
from pandas import DataFrame as df
import re
import warnings
import subprocess
import numpy as np


'''
At start up, grab an arbitrary number of .tsv files from the command line,
and create a DataBase object from each one.  (See DataBase.py).  Then
create a Python dictionary with the bare filenames as keys and the
DataBase objects as values.
'''
u = 'http://localhost:7201/graphdb/insertdata'
h = {'Content-Type':'application/json'}

cmdargs = sys.argv

cmdargs.pop(0) # Get rid of the script name, leaving only the actual arguments.

filelist = cmdargs


print('filelist = ' + str(filelist))

for filename in filelist:

    print('filename = ' + filename)

    warnings.simplefilter("ignore")  # Ignore garbage in the .tsv file.

    if filename.endswith('.tsv'):

        db = pd.read_csv(filename, sep='\t', error_bad_lines=False)

    elif filename.endswith('.csv'):
        
        db = pd.read_csv(filename, error_bad_lines=False)

    elif filename.endswith('.xlsx'):

        db = pd.read_excel(filename)

    else:

        print('Invalid filetype.')
        exit()

    db.dropna(axis='columns', how='all', inplace=True)
    cols = db.columns
    r, c = db.shape
    print('r = ' + str(r))
    print('c = ' + str(c))
    print('db[0][0] = ' + str(db.iloc[0,0]))


    for i in range(3):

        token_list = []

        for col in cols:

            if db.notnull()[col].iloc[i]:

                token = {}

                print('col = ' + col)
                print('row = ' + str(i))
                print('cell = ' + str(db[col].iloc[i])) 

                token['filename'] = filename
                token['column name'] = col
                token['row number'] = str(i)
                token['content'] = str(db[col].iloc[i])
                
                token_list.append(token)

        print(str(token_list))
        r = requests.post(u, headers=h, json=token_list)


