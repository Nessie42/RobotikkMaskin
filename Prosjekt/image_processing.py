import numpy as np
import cv2 as cv



#grayscaling and blurring the image to reduce noise
def gray_and_blur(path, kernel_size):
    '''
    Uploads image from path, blurs it and grayscales it for further processing

    args:
        path: file path of chosen image
        kernel_size: (x,y) Size of kernel when blurring. Bigger = more blurry

    returns:
        image: blurred and grayscaled image as variable for further use
   '''
    
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)
    image = cv.blur(image, kernel_size)

    
    return image

#getting shape of image for later interpolation to x,y coordinates:
def dimensions(image):
    height, width = image.shape[:2] 
    center = ([width/2, height/2])

    return height, width, center



#threshhold for large shapes, edges for potential details
def vectorize_image(image):
    '''
    Vectorizes edges in the image by using threshold and canny to find contours on vector form.

    args:
        image: chosen image

    returns:
        contours_edge: Contrours found from Canny
        contours_thresh: Contours found from threshold
        image_contours: all contours superimposed on the original image.
   '''
    _, thresh = cv.threshold(image, 200, 255, cv.THRESH_BINARY_INV)
    edges = cv.Canny(image, 55, 70)

    contours_thresh, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours_edge, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    image_contours = cv.drawContours(image, contours_thresh, -1, (0,255,0), 1)
    image_contours = cv.drawContours(image_contours, contours_edge, -1, (0,255,0), 1)

    return contours_edge, contours_thresh, image_contours

#print("Contours found = ", len(contours_edge)+len(contours_thresh))


#approximating contours for simpler POSE commands:
def simplifying_vectors(image, contours, factor):
    '''
    Simplifies the vectors to fewer line segments

    args:
        image: chosen image
        contours: set of contours to be simplified
        factor: number. How detailed the simplification should be. High = less detailed

    returns:
        approx: set of new vectors
        image_approx: new vectors superimposed on image
   
   '''
    for i in contours:
        epsilon = factor*cv.arcLength(i, True)
        approx = cv.approxPolyDP(i, epsilon, True)

        image_approx = cv.drawContours(image, approx, -1, (0, 255, 0), 1)

    return approx, image_approx


#showing the image in pop-up for tuning.
def image_for_tuning(image):
    '''
    creates a pop up of image with vectors so user can check if its ok.

    args:
        image: chosen image
   
   '''
    cv.imshow("test", image)

    cv.waitKey(0)
    cv.destroyAllWindows()


