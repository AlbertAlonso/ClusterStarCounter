from cluster import Cluster

import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from skimage import data

path = 'samples/M15.png'

im = Cluster(path, (100,200,100,200))
print(im.path)
print(im.size)
plt.imshow(im.image)
plt.show()
