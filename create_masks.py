import os
import cv2 as cv
import sys
import numpy as np
# from skimage.metrics import structural_similarity as compare_ssim


def create_mask(imgPath1, imgPath2):
    masksPath = '/home/justyna/studia/magisterka/images_models/clear_images/train_data/masks/'
    # img1 = cv.imread(imgPath1, 0)
    # img2 = cv.imread(imgPath2, 0)
    # gray_image1 = cv.cvtColor(img1, cv.COLOR_HSV2RGB)
    # gray_image2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    # print(img1)
    # print(img2.shape)
    # cv.imshow("Oryginal", img2 - img1)
    # k = cv.waitKey(0)
    # (score, diff) = compare_ssim(img2, img1, full=True)
    # diff = (diff * 255).astype("uint8")
    #
    # cv.imshow("Oryginal", img1)
    # cv.imshow("Em", img2)
    # cv.imshow("Mask", diff)
    # k = cv.waitKey(0)

    for name in os.listdir(imgPath1):
        img1 = cv.imread(imgPath1 + name)
        img2 = cv.imread(imgPath2 + name)
        if img1 is None:
            sys.exit("Could not read the image.")

        cv.imwrite(masksPath + name, img2 - img1)

def change_masks(imgPath):
    for name in os.listdir(imgPath):
        img = cv.imread(imgPath + name)
        ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

        cv.imwrite(imgPath + name, thresh)

def check_image(imgPath):
    img = cv.imread(imgPath)
    print(img)

    cv.imshow("Mask", img)
    k = cv.waitKey(0)

if __name__ == '__main__':
    imgPat1 = '/home/justyna/studia/magisterka/images_models/clear_images/train_data/labels/'
    imgPat2 = '/home/justyna/studia/magisterka/images_models/clear_images/train_data/images/'
    masksPath = '/home/justyna/studia/magisterka/images_models/clear_images/train_data/masks/'
    imgPath = '/home/justyna/studia/magisterka/images_models/clear_images/test_data/masks/depth_bathroom_30_0_0_0_0.png'

    # check_image(imgPath)
    # create_mask(imgPat1, imgPat2)
    change_masks(masksPath)
