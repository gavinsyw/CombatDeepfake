# from https://www.astrobetter.com/blog/2010/03/03/fourier-transforms-of-images-in-python/
import numpy as np


def azimuthalAverage(image, center=None):
    """
    Calculate the azimuthally averaged radial profile.

    image - The 2D image
    center - The [x,y] pixel coordinates used as the center. The default is 
             None, which then uses the center of the image (including 
             fracitonal pixels).

    """
    # Calculate the indices from the image
    # print(image[0, 0])
    y, x = np.indices(image.shape)
    #     print(x)
    #     print(y)

    if not center:
        center = np.array([(x.max() - x.min()) / 2.0, (y.max() - y.min()) / 2.0])

    r = np.hypot(x - center[0], y - center[1])

    # Get sorted radii
    ind = np.argsort(r.flat)
    r_sorted = r.flat[ind]
    i_sorted = image.flat[ind]

    # Get the integer part of the radii (bin size = 1)
    r_int = r_sorted.astype(int)

    # Find all pixels that fall within each radial bin.
    deltar = r_int[1:] - r_int[:-1]  # Assumes all radii represented
    rind = np.where(deltar)[0]  # location of changed radius
    nr = rind[1:] - rind[:-1]  # number of radius bin

    # Cumulative sum to figure out sums for each radius bin
    csim = np.cumsum(i_sorted, dtype=float)
    tbin = csim[rind[1:]] - csim[rind[:-1]]

    radial_prof = tbin / nr

    return radial_prof


def verticalAverage(image):
    x, y = image.shape
    # print(x, y)
    L = []
    for i in range(y):
        tmp = 0
        for j in range(x):
            tmp += image[j, i]
        tmp = tmp / x
        L.append(tmp)
    L = np.array(L)
    return L


def horizontalAverage(image):
    x, y = image.shape
    # print(x, y)
    L = []
    for i in range(x):
        tmp = 0
        for j in range(y):
            tmp += image[i, j]
        tmp = tmp / y
        L.append(tmp)
    L = np.array(L)
    return L