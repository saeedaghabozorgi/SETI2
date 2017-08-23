import requests
import json
#!pip install ibmseti
import ibmseti
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os
from PIL import Image
from matplotlib import cm

r = requests.get('https://dal.objectstorage.open.softlayer.com/v1/AUTH_cdbef52bdf7a449c96936e1071f0a46b/simsignals_files/public_list_basic_v2_26may_2017.csv')
filelist_txt = r.text
nl = filelist_txt.readline()
print nl
