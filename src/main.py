#!/usr/bin/env python2-
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:29:49 2017

@author: Albert Alonso
"""

from __future__ import division, print_function
import matplotlib.pyplot as plt
from skimage import data
from scipy import signal
import time as t
import numpy as np


plt.interactive(True)

TIC = t.time()

# === FUNCTIONS ===============================================================


def region_square(base, inix, finx, iniy, finy):
    # Define which square of the original image
    # we are going to analyse if we need to study
    # a specific region
    im_region = base[inix:finx, iniy:finy]
    seg_size_x = finx-inix
    seg_size_y = finy-iniy
    return im_region, seg_size_x, seg_size_y


def median_filter(base, dx, dy):
    # Function to appply the median filter with subregions of (dx x dy)
    img_medfilt = signal.medfilt2d(base, (dx, dy))
    return img_medfilt


def gamma_contrast(im, num):
    # Function to apply a gamma contrast with power num and return normalized
    im_gamm = im**num
    im_gamm = (im_gamm-im_gamm.min())/(im_gamm.max()-im_gamm.min())
    return im_gamm


def repaint_square(im, xx, yy, star, contorn):
    # In order to avoid repetition of stars we repaint the image depending
    # where we find ourselves
    if contorn.mean() > 0.8*star and star > 0.5:
        im[xx-5:xx+6, yy-5:yy+6] = 2
    elif contorn.mean() > 0.6*star and star > 0.3:
        im[xx-3:xx+4, yy-3:yy+4] = 2
    else:
        im[xx-1:xx+2, yy-1:yy+2] = 2
    return im


def check(im, xx, yy, val):
    # Once we have found a star, we use this function to mark its position
    im[xx-1:xx+2, yy] = val
    im[xx, yy-1:yy+2] = val
    return im


# === MAIN PROGRAM ============================================================

FULL = False      # Use False to analyse specific regions while True count all

# --- Read the image to analyse------------------------------------------------

image_path = input('Image Path')
im = data.imread(image_path, as_grey=True)

Nx, Ny = im.shape

# --- Clean the image with filters and gamma-----------------------------------
im_clean_media3 = median_filter(im, 3, 3)
im_clean_media5 = median_filter(im, 5, 5)
im_clean_gamma2 = gamma_contrast(im, 2)
im_clean_gamma3 = gamma_contrast(im, 3)

# Select the appropiate one to use in the count
im_clean = np.copy(im_clean_gamma2)
print("Image has been cleaned...")

# --- Work with section or full image  ----------------------------------------

if FULL is False:
    ix, iy = 650, 900
    fx, fy = ix+200, iy+200
else:
    ix, iy = 0, 0
    fx, fy = Nx, Ny

im_work, size_x, size_y = region_square(im_clean, ix, fx, iy, fy)
im_sec = im[ix:fx, iy:fy]

# --- Creation of new arrays to use -------------------------------------------

im_res = np.zeros_like(im_work)  # Image results where the marks will go
im_copy = np.copy(im_work)       # Copy of the image to work before alteration

# M_O matrix to compare the value with its surroundings. Different sizes used
MO_small = np.ones((3, 3))
MO_small[1, 1] = 0

MO_m = np.ones((7, 7))
MO_m[3, 3] = 0

MO_large = np.ones((11, 11))
MO_large[5, 5] = 0

# --- Evaluation of each pixel-------------------------------------------------
print('Start detection and count...')
count = 0
for x in range(size_x):
    for y in range(size_y):
        MO = MO_m
        star = im_work[x, y]
        startx, endx = x - 3, x + 4
        starty, endy = y - 3, y + 4

        # We check if we are in an edge  and modify MO accordingly
        if x < 3:
            startx = 0
            MO = MO[3-x:, :]
        elif x >= size_x - 3:
            endx = size_x
            MO = MO[:3+size_x-x, :]
        if y < 3:
            starty = 0
            MO = MO[:, 3-y:]
        elif y >= size_y - 3:
            endy = size_y
            MO = MO[:, :3+size_y-y]

        # We select the region to study
        quad = im_work[startx:endx, starty:endy]

        if star - quad.mean() >= 0.07 or star > 0.8:
            # We define a threshold taking into consideration the mean of the
            # quadrant and in the case we are in a big star, just the mean.
            if (quad.mean() > 0.9*star and min(x, y) > 5 and
               x < size_x-5 and y < size_y-5):
                # We are in a big star. 1rst we check if there is a count
                # around. To do so lets first make bigger the region to
                # 11x11. We apply this at 5p from the edges to avoid errors
                quad_large = im_work[x-5:x+6, y-5:y+6]
                contorn = quad_large * MO_large

            elif (quad.mean() > 0.1 and quad.max()-quad.min() > 0.8 and
                  quad.shape == (7, 7)):
                # We find ourself in a very populated area so we must evalutate
                # carefully all the variations, to do so we work with an
                # (5x5) array and adapt the neighbour accordingly
                quad_small = im_work[x-1:x+2, y-1:y+2]
                contorn = quad_small * MO_small
            else:
                # In this case we find in a normal star so we do not alter the
                # arrays.
                contorn = quad * MO

            # Now we have a section for each case and  its contorn
            # If the pixel we find counting is the maximun in the contorn and
            # it is not one of our alterations, we add a count, otherwise we
            # pass to the next.
            if star >= contorn.max() and star != 2:
                # We add 1 to the count and mark it in the results image
                count += 1
                im_res = check(im_res, x, y, 1)

                # We need to check if the pixel is from a diffraction spike.
                # We evaluate both axis in order to check it, taking into
                # consideration if we are in an edge.
                axis_x = im_copy[x, starty:endy]
                axis_y = im_copy[startx:endx, y]
                if abs(axis_x.mean()-axis_y.mean()) > 0.05:
                    # In this case we are in a branch so we should not count it
                    count -= 1
                    im_res = check(im_res, x, y, 0)
                    # We confirmed by making sure it is not an amorphed star.
                    ex1, ex2 = axis_x[0], axis_x[len(axis_x)-1]
                    ey1, ey2 = axis_y[0], axis_y[len(axis_y)-1]
                    if max(ex1, ex2, ey1, ey2) < 0.7*star:
                        # If it is we restore the count and the star.
                        count += 1
                        im_res = check(im_res, x, y, 1)
                        im_work = repaint_square(im_work, x, y, star, contorn)
                else:
                    # If we are in a star we need to repaint the zone to avoid
                    # multiple counts on a single star.
                    im_work = repaint_square(im_work, x, y, star, contorn)


im_work = (im_work-im_work.min())/(im_work.max()-im_work.min())
resu = im_copy - im_copy*im_res
resu = (resu-resu.min())/(resu.max()-resu.min())
print("Nº stars = ", count)

# --- FIGURES------------------------------------------------------------------

plt.figure("Background Noise")
plt.subplot(231)
plt.title('(a)')
plt.axis('off')
plt.imshow(im[ix:fx, iy:fy], cmap='gray_r')
plt.subplot(232)
plt.title("(b)")
plt.axis('off')
plt.imshow(im_clean_media3[ix:fx, iy:fy], cmap='gray_r')
plt.subplot(233)
plt.title("(c)")
plt.axis('off')
plt.imshow(im_clean_media5[ix:fx, iy:fy], cmap='gray_r')
plt.subplot(234)
plt.title('(d)')
plt.axis('off')
plt.imshow(im[ix:fx, iy:fy], cmap='gray_r')
plt.subplot(235)
plt.title("(e)")
plt.axis('off')
plt.imshow(im_clean_gamma2[ix:fx, iy:fy], cmap='gray_r')
plt.subplot(236)
plt.title("(f)")
plt.axis('off')
plt.imshow(im_clean_gamma3[ix:fx, iy:fy], cmap='gray_r')

plt.figure("Results")
plt.subplot(221)
plt.title("(a)")
plt.axis('off')
plt.imshow(im_copy, cmap='gray_r')
plt.subplot(222)
plt.axis('off')
plt.title("(b)")
plt.imshow(im_work, cmap='gray_r')
plt.subplot(223)
plt.axis('off')
plt.title("(c)")
plt.imshow(im_res, cmap='gray_r')
plt.subplot(224)
plt.axis('off')
plt.title("(d)")
plt.imshow(resu, cmap='gray_r')


# =============================================================================
TAC = t.time()
print("time: ", TAC-TIC, " sec")
