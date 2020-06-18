import cv2
import numpy as np
import os
import radialProfile
from InterceptFace import crop_face
import pickle
from scipy.interpolate import griddata

data = {}
epsilon = 1e-8
N = 500
y = []
error = []

number_iter = 500

psd1D_total = np.zeros([number_iter, N])
label_total = np.zeros([number_iter])
psd1D_org_mean = np.zeros(N)
psd1D_org_std = np.zeros(N)

cont = 0

# fake data
rootdir = 'prepro_deepFake/fake/'

for subdir, dirs, files in os.walk(rootdir):
    for file in files:

        filename = os.path.join(subdir, file)

        img = cv2.imread(filename, 0)
        #         img = crop_face(filename)
        #         print(filename)
        # we crop the center
        h = int(img.shape[0] / 3)
        w = int(img.shape[1] / 3)
        img = img[h:-h, w:-w]

        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)

        magnitude_spectrum = 20 * np.log(np.abs(fshift))
        psd1D = radialProfile.azimuthalAverage(magnitude_spectrum)
        #         print(psd1D)
        #         print(type(psd1D))
        #         print(psd1D.size)
        # Calculate the azimuthally averaged 1D power spectrum
        points = np.linspace(0, N, num=psd1D.size)  # coordinates of a
        xi = np.linspace(0, N, num=N)  # coordinates for interpolation
        #         print(points)
        #         print(xi)
        interpolated = griddata(points, psd1D, xi, method='cubic')
        interpolated /= interpolated[0]

        psd1D_total[cont, :] = interpolated
        label_total[cont] = 0
        cont += 1

        if cont == number_iter:
            break
    if cont == number_iter:
        break

for x in range(N):
    psd1D_org_mean[x] = np.mean(psd1D_total[:, x])
    psd1D_org_std[x] = np.std(psd1D_total[:, x])

## real data
psd1D_total2 = np.zeros([number_iter, N])
label_total2 = np.zeros([number_iter])
psd1D_org_mean2 = np.zeros(N)
psd1D_org_std2 = np.zeros(N)

cont = 0
rootdir2 = 'prepro_deepFake/real/'

for subdir, dirs, files in os.walk(rootdir2):
    for file in files:

        filename = os.path.join(subdir, file)
        parts = filename.split("/")

        img = cv2.imread(filename, 0)

        #         img = crop_face(filename)
        #         print(filename)
        # we crop the center
        h = int(img.shape[0] / 3)
        w = int(img.shape[1] / 3)
        img = img[h:-h, w:-w]

        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        fshift += epsilon

        magnitude_spectrum = 20 * np.log(np.abs(fshift))

        # Calculate the azimuthally averaged 1D power spectrum
        psd1D = radialProfile.azimuthalAverage(magnitude_spectrum)

        points = np.linspace(0, N, num=psd1D.size)  # coordinates of a
        xi = np.linspace(0, N, num=N)  # coordinates for interpolation

        interpolated = griddata(points, psd1D, xi, method='cubic')
        interpolated /= interpolated[0]

        psd1D_total2[cont, :] = interpolated
        label_total2[cont] = 1
        cont += 1

        if cont == number_iter:
            break
    if cont == number_iter:
        break

for x in range(N):
    psd1D_org_mean2[x] = np.mean(psd1D_total2[:, x])
    psd1D_org_std2[x] = np.std(psd1D_total2[:, x])

y.append(psd1D_org_mean)
y.append(psd1D_org_mean2)

error.append(psd1D_org_std)
error.append(psd1D_org_std2)

psd1D_total_final = np.concatenate((psd1D_total, psd1D_total2), axis=0)
label_total_final = np.concatenate((label_total, label_total2), axis=0)

data["data"] = psd1D_total_final
data["label"] = label_total_final

output = open('train_1000.pkl', 'wb')
pickle.dump(data, output)
output.close()

print("DATA Saved")