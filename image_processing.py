import numpy as np
import cv2 as cv
import os
 

class ImageProcessor:
    
    
    # Intializing object variables:
    def __init__(self, image_path):
        self.image_path = image_path # File name
        self.image = None
        self.edges = None
        self.polylines = []
        self.stripped_polylines = np.empty((0,2), np.float32)
        self.px_width, self.px_height = 0, 0
        self.px_center = []
        self.mm = None
        self.liste =[]
        self.mm_polylines = []
    
    
    
    # Retrieving image from file name
    def find_image(self):
        
        # Check if file path exist, if not: find file:
        if not os.path.exists(self.image_path):
            sample_path = cv.samples.findFile(self.image_path)
            if not sample_path:
                raise FileNotFoundError(f"Image not found: {self.image_path}")
            self.image_path = sample_path
        
        # Load image, rotate if horizontal
        self.image = cv.imread(self.image_path, cv.IMREAD_GRAYSCALE)
        if self.image is None:
            raise ValueError(f"cv.imread failed for: {self.image_path}")
        # Rotate image if width > height
        if self.image.shape[0] > self.image.shape[1]:
            self.image = cv.rotate(self.image, cv.ROTATE_90_CLOCKWISE)
            
        return self.image
        
    
    
    # Grayscaling and blurring the image to detect edges:
    def detect_edges(self, low_threshold=100, high_threshold=150, blur=(3,3)):
        
        if self.image is not None and self.image.shape[0] > 0:
            self.image = cv.GaussianBlur(self.image, blur, 0)
            
            # Detecting edges in image by thresholding:
            self.edges = cv.Canny(self.image, low_threshold, high_threshold)
            
            # Smoothing the edges by filling smaller gaps, merging lines that are close by:
            kernel = np.ones((4,4),np.uint8)
            self.edges = cv.morphologyEx(self.edges, cv.MORPH_CLOSE, kernel, iterations=1)
            self.edges = cv.dilate(self.edges, kernel, iterations=1)
            self.edges = cv.erode(self.edges, kernel, iterations=1)
            
        return self.edges



    # Converting edges to polygons:
    def get_polylines(self, min_length=12, max_length=80, epsilon=4.0, samples=50):
        
        # Finding contours in image:
        if self.edges.all():
            print("No edges found.")
        contours, _ = cv.findContours(self.edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE) 
        
        for i in contours:
            
            # Ignoring small lines:
            if len(i) < min_length:
                continue
            
            # Approximating the polygons:
            approximation = cv.approxPolyDP(i, epsilon, False)
            pts = approximation[:,0,:].astype(np.float32)  # Nx2
            
            # Simplifying lines by removing and spacing points:
            if len(pts) > max_length:
                spaced_pts = np.linspace(0, len(pts)-1, samples).astype(int)
                pts = pts[spaced_pts]
            self.polylines.append(pts)
            
        # Removing [] from array:
        if len(self.polylines) > 0:
            self.stripped_polylines = np.concatenate(self.polylines, axis=0)  # (N, 2)
            print("Antall punkter:", len(self.stripped_polylines))
            #print("Eksempel på første 5 punkter:\n", self.stripped_polylines[:5])
        else:
            self.stripped_polylines = np.empty((0, 2))
            
        return self.polylines, self.stripped_polylines
    
    
    
    # Scaling drawing from pixel to mm:
    def scale_drawing(self, A4_width=210.0, A4_height=297.0, margin=8.0):       
        
        # Image dimensions:
        self.px_width, self.px_height = self.image.shape[:2] # x = bredde, y = høyde
        self.px_center = np.array([self.px_width / 2, self.px_height / 2], dtype=np.float32)
        
        # Defining workspace in A4 sheet:
        workspace_width, workspace_heigth = A4_width-2*margin, A4_height-2*margin
        A4_center = np.array([A4_width / 2, A4_height / 2], dtype=np.float32)
        
        # Scaling pixels in mm:
        sx = A4_width / self.px_width
        sy = A4_height / self.px_height
        s  = min(sx, sy)
        tx = margin + (A4_width  - s * self.px_width) / 2.0
        ty = margin + (A4_height  - s * self.px_height) / 2.0
        
        # Scaling drawing to A4:
        for poly in self.polylines:
            if poly is None or len(poly) == 0:
                continue
            if poly.ndim == 3 and poly.shape[1:] == (1,2):
                poly = poly[:,0,:]
            if poly.shape[1] != 2:
                continue
            self.mm = np.empty_like(poly, dtype=np.float32)
            self.mm[:,0] = s*poly[:,0] + tx
            self.mm[:,1] = s*(self.px_height - poly[:,1]) + ty
            self.mm_polylines.append(self.mm)
            self.liste.append(len(poly))
            
        print("Antall linjer:", len(self.liste))
        print(self.liste)    
        
        return self.liste, self.mm
        
      
        
    def show_image(self):
        # Show image / object of the drawing
        #cv.imshow(self.image_path, self.image) 
        
        # Show drawing / strokes:
        blank = 255 * np.ones_like(self.image)
        for pts in self.polylines:
            cv.polylines(blank, [pts.astype(np.int32)], isClosed=False, color=0, thickness=1)
        cv.imshow("Drawing by Pierre Robot", blank)
        
        # Close pop-up images at key-press:
        cv.waitKey(0)
        cv.destroyAllWindows()

    
draw = ImageProcessor("Lenna_test.png")
draw.find_image()
draw.detect_edges()
draw.get_polylines()
draw.scale_drawing()
draw.show_image()