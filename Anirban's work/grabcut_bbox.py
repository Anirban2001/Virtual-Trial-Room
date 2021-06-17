# import the necessary packages
import numpy as np
import argparse
import time
import cv2
import os
from utils import show, apply_new_background, find_largest_contour  # Addition 1


def ExtractFace(img_name):
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    # img_name = input("Enter the image path : ")
    ap.add_argument("-i", "--image", type=str,
                    default=os.path.sep.join([path1 + img_name]),
                    help="path to input image that we'll apply GrabCut to")
    ap.add_argument("-c", "--iter", type=int, default=10,
                    help="# of GrabCut iterations (larger value => slower runtime)")
    args = vars(ap.parse_args())
    # load the input image from disk and then allocate memory for the
    # output mask generated by GrabCut -- this mask should hae the same
    # spatial dimensions as the input image
    image = cv2.imread(args["image"])
    mask = np.zeros(image.shape[:2], dtype="uint8")
    # define the bounding box coordinates that approximately define my
    # face and neck region (i.e., all visible skin)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # we need to keep in mind aspect ratio so the image does
    # not look skewed or distorted -- therefore, we calculate
    # the ratio of the new image to the old image
    r = 400.0 / image.shape[1]
    dim = (400, int(image.shape[0] * r))
    # perform the actual resizing of the image and show it
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # print(faces)
    x = faces[0][0]
    y = faces[0][1]
    w = faces[0][2]
    h = faces[0][3]
    x1 = x+w
    y1 = y+h
    # print(x, y, x1, y1)
    h_upper = int((h*50)/100)
    h_lower = int((h*25)/100)
    w = int((w*10)/100)
    x -= w
    x = max(0, x)
    y = y-h_upper
    y = max(0, y)
    x1 = x1+w
    y1 = y1+h_lower
    rect = (x, y, x1-x, y1-y)
    # allocate memory for two arrays that the GrabCut algorithm internally
    # uses when segmenting the foreground from the background
    fgModel = np.zeros((1, 65), dtype="float")
    bgModel = np.zeros((1, 65), dtype="float")
    # apply GrabCut using the the bounding box segmentation method
    start = time.time()
    (mask, bgModel, fgModel) = cv2.grabCut(image, mask, rect, bgModel,
                                           fgModel, iterCount=args["iter"], mode=cv2.GC_INIT_WITH_RECT)
    end = time.time()
    print("[INFO] applying GrabCut took {:.2f} seconds".format(end - start))
    # the output mask has for possible output values, marking each pixel
    # in the mask as (1) definite background, (2) definite foreground,
    # (3) probable background, and (4) probable foreground
    values = (
        ("Definite Background", cv2.GC_BGD),
        ("Probable Background", cv2.GC_PR_BGD),
        ("Definite Foreground", cv2.GC_FGD),
        ("Probable Foreground", cv2.GC_PR_FGD),
    )
    # loop over the possible GrabCut mask values
    for (name, value) in values:
        # construct a mask that for the current value
        # print("[INFO] showing mask for '{}'".format(name))
        valueMask = (mask == value).astype("uint8") * 255
        # display the mask so we can visualize it
        #cv2.imshow(name, valueMask)
        # cv2.waitKey(0)
        # we'll set all definite background and probable background pixels
        # to 0 while definite foreground and probable foreground pixels are
        # set to 1
        outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD),
                              0, 1)
        # scale the mask from the range [0, 1] to [0, 255]
        outputMask = (outputMask * 255).astype("uint8")
        # apply a bitwise AND to the image using our mask generated by
        # GrabCut to generate our final output image
        output = cv2.bitwise_and(image, image, mask=outputMask)
        # show the input image followed by the mask and output generated by
        # GrabCut and bitwise masking
        #cv2.imshow("Input", image)
        #cv2.imshow("GrabCut Mask", outputMask)

    # Add from here to your code
        ##############################################################
        # create `new_mask3d` from `mask2` but with 3 dimensions instead of 2
        new_mask3d = np.repeat(outputMask[:, :, np.newaxis], 3, axis=2)
        mask3d = new_mask3d
        mask3d[new_mask3d > 0] = 255.0
        mask3d[mask3d > 255] = 255.0
        # apply Gaussian blurring to smoothen out the edges a bit
        # `mask3d` is the final foreground mask (not extracted foreground image)
        mask3d = cv2.GaussianBlur(mask3d, (5, 5), 0)
        # show('Foreground mask', mask3d)

        # create the foreground image by zeroing out the pixels where `mask2`...
        # ... has black pixels
        foreground = np.copy(image).astype(float)
        foreground[outputMask == 0] = 0
        # show('Foreground', foreground.astype(np.uint8))

        # save the images to disk
        #save_name = image.split('/')[-1].split('.')[0]

    # Till here
        ######################################################################
        # cv2.imshow("GrabCut Output", output)

        # if args['new_background']:

    img_name = img_name[::-1]
    pos = img_name.find('.')
    img_name = img_name[pos+1:]
    img_name = img_name[::-1]
    apply_new_background(mask3d, foreground, (x, x1, y, y1),
                         path2+img_name)  # Also add this line
    cv2.waitKey(0)
    cv2.destroyAllWindows()


path1 = input("Path of folder of images :")
path2 = input("Path of folder of saved faces:")
listing = os.listdir(path1)
for file in listing:
	ExtractFace(file)
