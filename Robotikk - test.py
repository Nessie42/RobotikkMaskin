import numpy as np
import cv2 as cv

#getting image from file path

path = cv.samples.findFile("C:\\Users\\mathe\\Downloads\\face.jpg")


#Grayscaling the image

image = cv.imread(path, cv.IMREAD_GRAYSCALE)


#Blurring the image to reduce noise

image = cv.blur(image, (3,3))


#Splitting the image by threshold: [image, threshold value, max value, method]
#Any value over threshold value will be changed to white, all others to max value.

_, thresh = cv.threshold(image, 200, 255, cv.THRESH_BINARY_INV)


#Creating borders to find lines in the image removed by threshold. [image, lower boundary, upper boundary]
#the boundaries are values for intensity gradients, where values under lower are discarded and values over upper are kept as edges.

edges = cv.Canny(image, 55, 70)


#adding the borders to the thresh image for a more detailed image:

added_image = cv.add(thresh, edges)


#Finding contours:
contours_thresh, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contours_edge, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

print("Contours found = ", len(contours_edge)+len(contours_thresh))
#print(contours)
image_contours = cv.drawContours(image, contours_thresh, -1, (0,255,0), 1)
image_contours = cv.drawContours(image_contours, contours_edge, -1, (0,255,0), 1)


#approximating contours for simpler POSE commands:
for i in contours_thresh:
    epsilon = 50*cv.arcLength(i, True)
    approx = cv.approxPolyDP(i, epsilon, True)

    image_approx = cv.drawContours(image, approx, -1, (0, 255, 0), 1)


#showing the image in pop-up for tuning.
print(contours_edge)

#cv.imshow("test", image_approx)


#Image pop-up closes at key-press
cv.waitKey(0)
cv.destroyAllWindows()