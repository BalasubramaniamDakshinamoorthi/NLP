import pandas as pd
from pandas import DataFrame as df
import re
import warnings
import subprocess
import numpy as np
import owlready2 as ar

class DataBase:

   """
   A DataBase object is a Pandas DataFrame with a few additional
   bells and whistles.  For example, is has the minimum, maximum,
   and average for those columns for which that makes sense.
   """


   def __init__(self, filename):

      print('filename sent to constructor  = ' + filename)

      warnings.simplefilter("ignore")  # Ignore garbage in the .tsv file.

      if filename.endswith('.tsv'):

          self.db = pd.read_csv(filename, sep='\t', error_bad_lines=False)

      elif filename.endswith('.csv'):
        
          self.db = pd.read_csv(filename, error_bad_lines=False)

      elif filename.endswith('.xlsx'):

          self.db = pd.read_excel(filename)

      else:

          print('Invalid filetype.')
          return

      self.db.dropna(axis='columns', how='all', inplace=True)
      cols = self.db.columns

      print('cols = ' + str(cols))

      for col in cols:

          '''
          Where applicable, convert strings to datetimes.
          '''

          if self.db[col].dtype == object:

              self.db[col] = pd.to_datetime(self.db[col],
                      errors='ignore', infer_datetime_format =True)
       
      print(str(self.db.dtypes)) # Diagnostic code written to the terminal.

      if filename == 'bug.tsv': #HACK!!!
          #This should be fixed by referring to the ontology.

          print(str(self.db['Date Closed'] - self.db['Opened']))

          # Time between opening and closing of each bug.
          self.db['time'] = self.db['Date Closed'] - self.db['Opened']

      self.minima = dict() # Minima for each numerical column.
      self.maxima = dict() # Maxima for each numerical column.
      self.averages = dict() # Averages for each numerical column.
      self.numerical = dict() # Boolean true iff column is numerical.

      cols = self.db.columns

      for col in cols:

          print("Column = " + str(col))
          print(str(self.db[col].dtype))
          self.numerical[col] = False

          if self.db[col].dtype == np.int64 or self.db[col].dtype == np.float64:
              '''
              Int64 and Float64 columns have robust methods for computing
              their minima, maxima, and means.  Robust means ignores NaN's
              blanks, and other garbage.
              '''

              self.numerical[col] = True
              self.minima[col] = np.nanmin(self.db[col].values)
              self.maxima[col] = np.nanmax(self.db[col].values)
              self.averages[col] = np.nanmean(self.db[col].values)

          if self.db[col].dtype  == 'timedelta64[ns]':

              '''
              Time deltas do NOT have robust min, mean, and average methods.
              We must go through all the values of the columns, computing
              min, max, and averages while ignoring invalid values.
              '''

              self.numerical[col] = True

              min = pd.Timedelta.max
              max = pd.Timedelta.min
              total = 0.0
              count = 1.00

              for x in self.db[col]:

                  # This is a general check for valid timedelta values
                  if pd.isnull(x) == False:

                      if x < min:
                          min = x
              
                      if x > max:
                          max = x

                      total = total + x.total_seconds() 
                      count = count + 1.0

              average = total / count

              average_time = pd.to_timedelta(average, unit='seconds')

              self.minima[col] = min
              self.maxima[col] = max
              self.averages[col] = average_time

      warnings.simplefilter("always")
      
      if 'Number' in self.db:
          print('Have Number field')
          self.db.set_index('Number', inplace = True)
          print('Set Index')
          print('Values = ' + str(self.db.index.values))
          self.valid_indices = set(self.db.index.values)
          print('Set Valid Indices')
      
      self.length = self.db.shape[0]

      return # End of constructor.

   def lookup(self, query):

      '''
      Look for various types of queries:
      '''

      query_minimum = (re.search('minimum', query, re.IGNORECASE) != None)
      query_maximum = (re.search('maximum', query, re.IGNORECASE) != None)
      query_average = (re.search('average', query, re.IGNORECASE) != None)
      howMany = query.lower().startswith('how many ')
      whatPercent = query.lower().startswith('what percent ')
      execute_script = query.startswith('sh ')

      cols = self.db.columns

      for col in cols:

          if self.numerical[col]:

              if re.search(str(col), query, re.IGNORECASE) != None:

                  if query_minimum:

                      return(str(self.minima[col]))

                  if query_maximum:

                      return(str(self.maxima[col]))

                  if query_average:

                      return(str(self.averages[col]))

                  return("Value not found.")

      if howMany or whatPercent:

         val = ""
         val2 = ""
         vals = ""
         fieldname = ""
         fieldname2 = ""
          
         cmd = query[9:]

         for fieldname in self.db.columns:

            if re.search(fieldname, cmd, re.IGNORECASE) != None:

               fieldname2 = fieldname

               print("fieldname2 = " + fieldname2, flush=True)

               vals = self.db[fieldname].unique()

               for val in vals:

                  print("val = " + str(val), flush=True)

                  if re.search(str(val), cmd, re.IGNORECASE) != None:

                     val2 = val

                     print("val2 = " + str(val2), flush=True)

         if fieldname2 == "":

             return("Query must contain a valid field name.")

         if val2 == "":

             return("Query must contain a valid value for \"" + fieldname2 + "\".")

         print("fieldname2 = " + fieldname2, flush=True)
         print("val2 = " + str(val2), flush=True)

         db2 = self.db[self.db[fieldname2] == val2]

         number = len(db2)

         print("number = " + str(number), flush=True)

         percent = round(100 * number / self.length, 2)

         print("percent = " + str(percent) + "%", flush=True)

         if whatPercent:

             return(str(percent) + '%')

         # It's a "how many request"

         return(str(number))

      if execute_script:

         cmd = query[3:] # Strip off the "sh "
         sp = subprocess.run(cmd, stdout=subprocess.PIPE)
         out = sp.stdout.decode('utf-8')
         return(out)

      have_num = False

      #Check if the query contains a numerical ID
      id = re.search('\d{7,7}', query)
      
      if id == None:

         id = re.search(r'srv\S+', query)

      else:

          have_num = True

      if id == None:
          
          return("Query must include valid ID")

      if have_num:

          index= int(id.group())

          print(str(index), flush=True)

      else:

         index = id.group()

         print(index, flush=True)

      if index not in self.valid_indices:

         return("Invalid ID")

      for fieldname in self.db.columns:

         if re.search(fieldname, query, re.IGNORECASE) != None:
            return(str(self.db.loc[index, fieldname]))


      return("Query must include a valid keyword.")
