import os
import cv2 as cv
import sys
import numpy as np
# from PIL import Image
# import matplotlib.pyplot as plt


def equal_imageNumber(imgPath1, imgPath2):
    files = []
    for name in os.listdir(imgPath1):
        # print(name)
        files.append(name)

    for name in os.listdir(imgPath2):
        if name not in files:
            os.remove(imagePath2 + name)


def clear_badImage(imgPath):

    # plt.hist(img.ravel(), 1001, [0, 1001])
    # plt.show()
    img = cv.imread(imgPath)
    if img is None:
        sys.exit("Could not read the image.")
    print(np.mean(img))

    cv.imshow("Display window", img)
    k = cv.waitKey(0)
    # bad:
    # 98.075390625
    # 52.92796223958333
    # for name in os.listdir(imgPath):
    #     img = cv.imread(imgPath + name)
    #     if img is None:
    #         sys.exit("Could not read the image.")
    #     # print(np.mean(img))
    #     mean = np.mean(img)
    #
    #     if mean > 60:
    #         os.remove(imgPath + name)

if __name__ == '__main__':
    imagePath1 = "/home/justyna/All/magisterka/images_models/clear_images/train_data/images/"
    imagePath2 = "/home/justyna/All/magisterka/images_models/clear_images/train_data/labels/"
    imagePath = "/home/justyna/All/magisterka/images_models/clear_images/train_data/images/depth_bathroom_22_0_0_3_4.png"
    # os.remove(imagePath + "demofile.txt")

    equal_imageNumber(imagePath1, imagePath2)
    # clear_badImage(imagePath)
