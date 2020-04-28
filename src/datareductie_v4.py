import Waarneemproef_tools_D4 as WT
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import glob
import sp

path = "/data2/suters/"
shape_nonwindowed = (4200,2154) # x en y 'omgedraaid' in fits files
shape_windowed = (1007,956)

def master(masterfile, imagepath):
    '''combineren images tot master frame (master bias, flat...)'''
    list_of_files = glob.glob(imagepath)
    print(len(list_of_files)) # check of je alle files hebt
    for file_name in list_of_files:
        singlefile = fits.open(file_name)[1] # data in 1
        masterfile += singlefile.data * 1.
    masterfile_final = masterfile / len(list_of_files) # middelen
    return masterfile_final

def windowing(flat, window):
    '''handmatig windowen flat'''
    x1, x2, y1, y2 = window
    flat_windowed = flat[y1:y2, x1:x2]
    return flat_windowed

def calibration(light_filelist):
    '''zoals in formules voor kalibratie van PS wp1, nu zonder dark'''
    for light_file in light_filelist:
        
        light_raw = fits.open(light_file)[1] # data in 1
        light = light_raw.data
        
        flat1 = flat_master - bias_nonwindowed_master
        flat2 = flat1 / np.mean(flat1)
        
        # 'manually' windowing flat
        # X1, X2; Y1, Y2 [668:1623,1642:2648]
        window =(667, 1623, 1641, 2648)
        flat2_windowed = windowing(flat2, window)
        
        light1 = light - bias_windowed_master
        science = light1 / flat2_windowed
        science[science<-100] = 1 # 'artefacten' door procedure eruithalen
        
        # opslaan
        light_name = light_file[24:]
        WT.saveFITS(science,"science_calibrated/{0}".format(light_name))
        print("Created and saved 1 science image!")

# bias non-windowed (10 totaal)
bias_nonwindowed = np.zeros(shape_nonwindowed)
bias_nonwindowed_master = master(bias_nonwindowed, path+'bias_fullframe/r*.fit')

# bias windowed (20 totaal)
bias_windowed = np.zeros(shape_windowed)
bias_windowed_master = master(bias_windowed, path+'/bias_windows/r*.fit')

# flats in B-filter (wij werken alleen in B) (5 totaal)
flat = np.zeros(shape_nonwindowed)
flat_master = master(flat, path+'flats/B/r*.fit')

# light (58 totaal)
light_filelist = glob.glob(path+'science/B/r*.fit')
print(len(light_filelist)) # check of je alle files hebt

# science
calibration(light_filelist)
