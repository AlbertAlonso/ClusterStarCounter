import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from skimage import data

class Cluster:

    def load_image(self, path):
        return data.imread(path,as_gray=True)

    def __init__(self, path, region = None):
        '''
        Constructor that loads an image and selects the correct region to
        analyze.
        :path str the location of the image relative to the script
        :region tupple  (initial_x, final_x, initial_y, final_y)
        '''
        self.path = path
        image = self.load_image(path)
        if region is None:
            self.image = image
        else:
            self.image = image[region[0]:region[1], region[2]:region[3]]

    def region_square(inix, finx, iniy, finy):
        '''
        Defines the square of the base image to focus on.
        '''
        return self.image[inix:finx, iniy:finy]

    def size(self):
        return np.shape(self.image)

    def median(self, dx, dy):
        self.image = signal.medfilt2d(self.image,(dx,dy))
