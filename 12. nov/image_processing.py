import numpy as np
import cv2 as cv
 
class ImageProcessor:
    
    def __init__(self, image_path):
        self.image_path = image_path # File name
        self.image = None
        self.polylines = []
        self.stripped_polylines = []
        self.mm = None
        self.width, self.height = 0,0
        self.A4X = 297.0
        self.A4Y = 210.0
        self.A4_CENTER_MM = np.array([self.A4X/2.0, self.A4Y/2.0])
        self.liste =[]
        self.mm_polylines = []
    
    def image_processing(self):
        
        # Retrieving image from file name
        self.image_path = cv.samples.findFile(self.image_path)
        
        # Grayscaling and blurring the image:
        self.image = cv.imread(self.image_path, cv.IMREAD_GRAYSCALE)
        self.image = cv.GaussianBlur(self.image, (3,3), 0)
        
        # Detecting edges in image by thresholding:
        lower_threshold = 100
        higher_threshold = 150
        edges = cv.Canny(self.image, lower_threshold, higher_threshold) 
        
        # Smoothing the edges by filling smaller gaps, merging lines that are close by:
        kernel = np.ones((4, 4), np.uint8)
        edges = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel, iterations=1)
        edges = cv.dilate(edges, kernel, iterations=1)
        edges = cv.erode(edges, kernel, iterations=1)
    
        # Finding contours, approximating the polygons, and ignoring small lines:
        contours, _ = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE) 
        for i in contours:
            minimum_length = 12
            maximum_length = 80
            if len(i) < minimum_length:
                continue
            accuracy = 4.0
            approximation = cv.approxPolyDP(i, accuracy, False)
            points = approximation[:,0,:].astype(np.float32)  # Nx2
            if len(points) > maximum_length:
                samples = 50
                spaced_points = np.linspace(0, len(points)-1, samples).astype(int)
                points = points[spaced_points]
            self.polylines.append(points)
            #print(edges)
        
        # Removing [] from array:
        if len(self.polylines) > 0:
            self.stripped_polylines = np.concatenate(self.polylines, axis=0)  # (N, 2)
            print("Antall punkter:", len(self.stripped_polylines))
            print("Eksempel på første 5 punkter:\n", self.stripped_polylines[:5])
        else:
            self.stripped_polylines = np.empty((0, 2))
        return self.image, self.polylines, self.stripped_polylines
    
    def dimensions(self):
        self.width, self.height = self.image.shape[:2] 
        self.center = ([self.width/2, self.height/2]) 
        return self.width, self.height, self.center

    def scale_px_to_mm(self):       
        width, height = self.image.shape[:2] 
        self.width, self.height = width, height
        self.center = ([self.width/2, self.height/2])
        MARGIN = 8.0
        DRAW_W, DRAW_H = self.A4X-2*MARGIN, self.A4Y-2*MARGIN
        self.A4_CENTER_MM = np.array([self.A4X/2, self.A4Y/2], dtype=np.float32)
        
        sx = DRAW_W / self.width
        sy = DRAW_H / self.height
        s  = min(sx, sy)
        tx = MARGIN + (DRAW_W  - s*self.width)/2.0
        ty = MARGIN + (DRAW_H  - s*self.height)/2.0
        
        for poly in self.polylines:
            if poly is None or len(poly) == 0:
                continue
            if poly.ndim == 3 and poly.shape[1:] == (1,2):
                poly = poly[:,0,:]
            if poly.shape[1] != 2:
                continue
            self.mm = np.empty_like(poly, dtype=np.float32)
            self.mm[:,0] = s*poly[:,0] + tx
            self.mm[:,1] = s*(self.height - poly[:,1]) + ty
            self.mm_polylines.append(self.mm)
            self.liste.append(len(poly))
            
        return self.A4X, self.A4Y, self.A4_CENTER_MM, self.liste, self.mm, self.height, self.width, self.center
        #print(len(liste))
        #print(liste)
      
    def show_image(self):
        # Vis bildet som skal tegnes:
        cv.imshow(self.image_path, self.image) 
        
        # Vis polylines:
        blank = 255 * np.ones_like(self.image)
        for pts in self.polylines:
            cv.polylines(blank, [pts.astype(np.int32)], isClosed=False, color=0, thickness=1)
        cv.imshow("Finished painting", blank)
    
        cv.waitKey(0)
        cv.destroyAllWindows() #Image pop-up closes at key-press
    #    return all_pts
     
    #    print(all_pts.tolist())
     
    #coords = image_to_polylines()
    
painting = ImageProcessor('Lenna_test.png')
painting.image_processing()
painting.scale_px_to_mm()
painting.show_image()