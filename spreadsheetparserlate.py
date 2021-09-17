import os
import datetime
import time
import re
import sys
import platform
import nltk
import requests
import pandas as pd
from pandas import DataFrame as df
import re
import warnings
import subprocess
import numpy as np
import json
import uuid
import multiprocessing as mp
import sqlalchemy as sa

now = datetime.datetime.now().time() # time object

print("now =", now)


'''
At start up, grab an arbitrary number of .tsv files from the command line,
and create a DataBase object from each one.  (See DataBase.py).  Then
create a Python dictionary with the bare filenames as keys and the
DataBase objects as values.
'''
db = pd.DataFrame()

e = sa.create_engine('postgres://')
# e = sa.create_engine('postgres://postgres:postgres@52.173.130.34:5432/postgres')

cmdargs = sys.argv

cmdargs.pop(0) # Get rid of the script name, leaving only the actual arguments.

filelist = cmdargs

print('filelist = ' + str(filelist))

for filename in filelist:

    bare_filename = ''

    print('filename = ' + filename)

    warnings.simplefilter("ignore")  # Ignore garbage in the .tsv file.

    if filename.endswith('.tsv'):

        bare_filename = filename[:-4]
        db = pd.read_csv(filename, sep='\t', error_bad_lines=False, dtype=str)

    elif filename.endswith('.csv'):
        
        bare_filename = filename[:-4]
        db = pd.read_csv(filename, error_bad_lines=False)

    elif filename.endswith('.xlsx'):

        bare_filename = filename[:-5]
        db = pd.read_excel(filename)

    else:

        print('Invalid filetype.')
        exit()

    db.dropna(axis='columns', how='all', inplace=True)
    cols = db.columns
    number_of_rows, number_of_columns = db.shape
    print('number_of_rows = ' + str(number_of_rows))
    print('number_of_columns = ' + str(number_of_columns))
    # print('db[0][0] = ' + str(db.iloc[0,0]))

    db_list = db.to_numpy().tolist()

    print('db_list = ' + str(db_list))


    db.to_sql(bare_filename, con=e, if_exists='replace')
    db2 = pd.read_sql_table(bare_filename, 'postgres://')
    # db2 = pd.read_sql_table(bare_filename, 'postgres://postgres:postgres@52.173.130.34:5432/postgres')
    print(db2)
