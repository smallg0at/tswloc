import os

file_list = os.listdir('.')
target_list = [f for f in file_list if f.endswith('_translated.csv')]
