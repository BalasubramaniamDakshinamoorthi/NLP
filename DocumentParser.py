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
 
'''
At start up, grab an arbitrary number of .tsv files from the command line,
and create a DataBase object from each one.  (See DataBase.py).  Then
create a Python dictionary with the bare filenames as keys and the
DataBase objects as values.
'''

#Extract text from DOCX
def getDocxContent(filename):

    doc = docx.Document(filename)

    fullText = ""
    paragraphList = [] 

    for para in doc.paragraphs:
        paragraphText = para.text
        paragraphText = paragraphText.encode('ascii', errors='ignore').decode()
        print("Paragraph text= " + paragraphText)
        fullText += para.text
        if para.text != '':
            paragraphList.append(paragraphText)
    print('ParagraphList = ' + str(paragraphList))
    return paragraphList
	
file_dict = {}

cmdargs = sys.argv

cmdargs.pop(0) # Get rid of the script name, leaving only the actual arguments.

print(str(cmdargs))

for arg in cmdargs:

    if arg.endswith('.docx'):

       bare_filename = arg[:-5]

       print(bare_filename)

       file_dict[bare_filename] = arg 

    print(arg)

print('file_dict = ' + str(file_dict))

#Importing NLTK for sentence tokenizing
nltk.download('punkt')
nltk.download('popular')
from nltk.tokenize import sent_tokenize

token_list = []

token = {}

sentencenumber = 0

#sentences = sent_tokenize(resume)

for filename in file_dict:

    print('filename = ' + file_dict[filename])

    # full_text = getDocxContent(file_dict[filename])
    paragraph_list  = getDocxContent(file_dict[filename])

    #print('full text = ' + full_text)

    for paragraph in paragraph_list:

        sentences = sent_tokenize(paragraph)

        for sentence in sentences:

            token = {}
            sentence = sentence.encode('ascii', errors='ignore').decode()

            token['filename'] = file_dict[filename]
            token['datatype'] = 'plain text'
            token['sentencenumber'] = sentencenumber
            sentencenumber += 1
            token['text'] = sentence
            token_list.append(token)
            print('Sentence #' + str(sentencenumber))
            print(sentence)

# print('token_list = ' + str(token_list))

u = 'http://localhost:7201/graphdb/insertdata'
h = {'Content-Type':'application/json'}

# r = requests.post(u, headers=h, json=token_list)
