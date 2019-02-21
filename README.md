# Cluster Star Counter - First Approximation of the Number of Stars in Different Types of Open Clusters
A small algorithm I written for a paper on image processing using Python. 
## Cleaning the image
Before start the counting, the image must be cleaned to avoid misreadings.
### Background noise
In order to deal with background noise, which in the case of enchanted images it could be a relevant issue, we would usually apply filters through Fourier Transformation but due to the fact that what we want to count the pixels that differentiate themselves from the main color of the region around them and they are dispersed through all the image, we can not use this kind of solutions. In this type of cases, one common filter to use is the median filter. It is useful when we want to smooth the background noise. However, we do not want to erase any small star, so we would only take into consideration small arrays of 3x3 or 5x5 pixels.

Additionally, as the values of the pixels are normalize between 0 and 1, one way to clean the background would be apply a gamma contrast so the background pixels would decrease in value much faster than the bigger ones  I = I^{gamma}  , setting a bigger difference between background noise and stars.


![Filters](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/figure_filters_bkg-eps-converted-to.pdf)


### Nebula Dust
Another problem we find with the background in open cluster is the nebula dust, as in the case of the Pleiades. Luckily, applying the gamma contrast most of the dust is cleaned. While when using gamma = 3, we remove the majority of the dust, the results obtained with gamma = 2  are good enough to make the count easier. 

![Nebula Dust](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/figure_nebulosa_dust-eps-converted-to.pdf)


## Counting Stars
The main idea behind this method of counting the number of stars is that every star is considered to have a pixel which value its a local maximum, so by analyzing each pixel and its neighborhood, we detected them and proceed to count them. Although this is a basic idea, when we try to implement it we found several issues which add complexity to the program. 

Once we have cleaned the image, we can visually detect the stars. Nonetheless, the background noise is still big enough to trick the program so we need to define a threshold indicating which value we consider the brighter pixel of a star must have. As we have not remove completely the dust, we take into account the value of the pixels on the surrounding area to define it.  In order to get this value, we need first to make various attempts in different regions and different clusters. Once we have pass this threshold and consider our self at a star, we set a region of 7x7 pixels from the image already cleaned.

One of the first problem we find with this method is encountering more than one local maximum with an equal value on the same star. The correction we implement to avoid this is altering the value of the pixel and its neighbor when we found a local maximum by setting its value to 2 (twice as big as the maximum possible value of a pixel).  Once we have done that, we only need to indicate to the program that in order to considerate the pixel a star, the value must be bigger or equal than the maximum value of the contour but it must take into consideration that the value can not be bigger than 1, so we avoid counting all the pixel in the surroundings 3x3 pixels of a local maximum we have already changed.

### Edges
When considering the edges of the image, one easy method to avoid problems with the size of the region and the shape of $ M_O $ would have been avoiding them. However, the amount of stars found on the edges is relevant enough to make an modification to the code necessary in order to include them. This alteration consist in changing the shape of the regions to analyses depending on the distance to the edge and the location of the pixel we want to evaluate.  

### Star size
Using methods based on convolution of images is probably the most common way to count similar objects in images as cells and letters. The main reason why we can not use these methods is the diversity in sizes and shapes of the stars inside an open cluster. Furthermore, using transformation methods as Hough transformation would not work due to the amount of stars in each image.Additionally, this differences in sizes creates difficulties when there are stars large enough to include all the region we are analyzing inside them, making it difficult to detect only one local maximum in each star. In order to solve it, we increase the size of $ M_O $ to a region of 11x11 pixels. Luckily, all the large star are usually found at the center of the cluster so we do not face compilation errors.
  
Moreover, larger stars often show fluctuations in the maximums values of the pixels inside them, making it common to find multiples maximums separated enough from each other. The solution to this problem that we have found is expanding the modification we do around the counted stars setting to 2 a bigger square of 11x11 pixels.

![Nebula Dust](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/fig_big_stars-eps-converted-to.pdf)


### Star distribution density
The main reason to include the M15 cluster is because it sets a great example for the agglomeration of stars that usually happen at the center of the cluster due to its gravity. For these cases, a 7x7 region can include more than one stars, which can make the maximum of a star avoid the counting of the stars around it. To solve this, we must make the opposite of when we have a big star, which is reduce the size of the region we analyze to a 3x3 square. Moreover, now we must know when to differentiate between a being in a big star or in a very dense region of stars. We solve this by applying a threshold to the difference between the maximum and the minimum of each region, appealing to the fact that in one case there is background holes while in the larger stars it is a most uniform distribution. 

![Star density](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/fig_big_stars-eps-converted-to.pdf)



### Diffraction spikes
Another common problem this method faces is the one presented by the diffraction spikes. This spikes are caused by the telescope and are known to be a relevant inconvenient to study the object around big stars. Furthermore, this spikes have their own local maximums, so we must adjust the code to recognize them and not consider them stars. In order to do so, we evaluate the difference between both direction from the pixel. If the mean of both axis are different enough we consider to be studying a pixel in a spike. Nonetheless, there are cases where a small star has bigger width than height and can be wrongly defined as a spike. For that same reason, once we have consider a maximum to be part of a spike, we make a check with the ends values of the arrays and compare them with the pixel value.  

## Algorithm
1. Identify if we are evaluating a pixel near an edge. If it is the case, modify the shape of the arrays.
2. Check the neighbor pixels an see if we are into a big star or in a heavy populated area. Modify the shape of the arrays if it is the case. 
3. Find if we are in a local maximum.
4. Compare the both axis to see if we are in a big star's spike. In case we are, check for small stars with uneven shapes. 
5. Decide the size of the alteration of the pixels' values to avoid multiple counts. 

## Results

M15 - 4596
M44 - 2573
M45 - 4299

![Some Reuslts](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/fig_results_m15-eps-converted-to.pdf)
![Center of cluster](https://github.com/AlbertAlonso/ClusterStarCounter/blob/master/Readme_Images/fig_centre_m15-eps-converted-to.pdf)


