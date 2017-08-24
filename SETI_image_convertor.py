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

base_url = 'https://dal.objectstorage.open.softlayer.com/v1/AUTH_cdbef52bdf7a449c96936e1071f0a46b'
container = 'simsignals_basic_v2'

r = requests.get('https://dal.objectstorage.open.softlayer.com/v1/AUTH_cdbef52bdf7a449c96936e1071f0a46b/simsignals_files/public_list_basic_v2_26may_2017.csv')
filelist_txt = r.text


def get_spectrogram(fname,h,w,lengthRatio=1.0):
    
    r = requests.get('{}/{}/{}'.format(base_url, container, fname), timeout=4.0)
    if r.status_code != 200:
        print 'Failed retrieving {}'.format(fname)
        print r
        return None
    else:
        aca = ibmseti.compamp.SimCompamp(r.content)
        com_data = aca.complex_data()
        ratio = int(np.sqrt(len(com_data) *lengthRatio / (h*w)))
        if ratio == 0: 
            raise ValueError, "The selected lenght of signal is less than (Height x Width), select bigger ratio"
        elif ratio == 1:
            sig_data = com_data[:h*w].reshape(h,w)
            spec = np.abs( np.fft.fftshift( np.fft.fft(sig_data), 1) )**2
            spec = np.log(spec)
            spec = spec/np.max(spec) # Convert to float (0-1)
            image = Image.fromarray(cm.jet(spec, bytes=True)) #convert to RGB
        elif ratio > 1: # resize using IPL image
            sig_data = com_data[:h*ratio*w*ratio].reshape(h*ratio,w*ratio)
            spec = np.abs( np.fft.fftshift( np.fft.fft(sig_data), 1) )**2
            spec = np.log(spec) # Convert to float (0-255)
            spec = spec/np.max(spec) # Convert to float (0-1)
            image = Image.fromarray(cm.jet(spec, bytes=True)) #convert to RGB  
            image = image.resize((int(w), int(h)), Image.ANTIALIAS)

        
        return image

h = 32 # The hight of output image (bins)
w = 32 # The witdh of output image
lengthRatio = 1.0  # the length-ration of signal to be read. The higher reatio, the better resolution. E.g. 0.5 means half of time sereis.
#rdd_rgb_spec = rdd_fname_lb.map(lambda row: (row[1], dictClass[row[0]], get_spectrogram(row[1],h,w,lengthRatio)))


def filetext_gen(filelist_txt):
    results = filelist_txt.splitlines()[1:]
#     if not results:
#         break
    for result in results:
        yield result


from array import array
def toBinary(class_name,img):
    classnum = int(class_name)
    data = array('B')
    data.append(classnum)
    pix = img.load()
    for color in range(0,3):
        for x in range(0,32):
            for y in range(0,32):
                data.append(pix[x,y][color])
    return data

dictClass = dict({u'narrowband': 2, u'narrowbanddrd': 1, u'noise': 3, u'squiggle': 0})







if not os.path.exists('SETI-batches-bin'):
    os.makedirs('SETI-batches-bin')
import pickle
#mybytes = [120, 3, 255, 0, 100]
#with open("SETI-batches-bin/data_batch_1.bin", "wb") as mypicklefile:
i = 1
counter = 1
batch_size = 100
data = array('B')
for item in filetext_gen(filelist_txt): 
    uuid, sigclass =  item.split(',')
    file_name = uuid +'.dat'
    img_spec = get_spectrogram(file_name, h, w, lengthRatio)
    img_bytes = toBinary(dictClass[sigclass],img_spec)
    data += img_bytes
    if counter%batch_size == 0:
        with open('SETI-batches-bin/data_batch_%d.bin' % i, "wb") as myfile:   
            data.tofile(myfile)
        data = array('B')
        print i
        i += 1
    counter += 1


os.system('tar -zcvf SETI-binary.tar.gz SETI-batches-bin/')