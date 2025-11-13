import numpy as np
import cv2 as cv
import os
 

class ImageProcessor:
    
    
    # Intializing object variables:
    def __init__(self, image_path):
        self.image_path = image_path # File name
        self.image = None
        self.edges = None
        
        self.image_width, self.image_height = 0, 0
        self.image_center = []

        self.A4_width, self.A4_height = 210.0, 297.0
        self.A4_coordinates = None
      
        self.polylines = []
        self.scaled_polylines = []
        self.stripped_scaled_polylines = np.empty((0,2), np.float32)
        self.pts_per_polyline =[]
    
    
    
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
        if self.image.shape[1] > self.image.shape[0]:
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
        if self.edges is None:
            raise RuntimeError("Call detect_edges() before get_polylines().")
        else:
            contours, _ = cv.findContours(self.edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE) 
        
        self.polylines.clear()
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
        
        return self.polylines
    
    
    
    # Scaling drawing from pixel to mm:
    def scale_drawing(self, margin=20.0):       
        
        if self.image is None:
            raise RuntimeError("No image loaded before scale_drawing().")
        if not self.polylines:
            print("No polylines to scale.")
            return [], []
    
        # Image dimensions:
        self.image_height, self.image_width = self.image.shape[:2] # x = antall pixler i hver høyde(rad), y = antal pixler i hver bredde(kolonne)
        self.image_center = np.array([self.image_width / 2, self.image_height / 2], dtype=np.float32)
        
        # Defining workspace in A4 sheet:
        workspace_width, workspace_height = self.A4_width-2*margin, self.A4_height-2*margin
        #A4_center = np.array([A4_width / 2, A4_height / 2], dtype=np.float32)
        
        # Finding dimensions of pixels (mm per px) each direction:
        pixel_width = workspace_width / self.image_width
        pixel_height = workspace_height / self.image_height
        
        # Finding the smallest size factor for scaling:
        scale_factor = min(pixel_width, pixel_height)
        
        # Calculating leftover space after scaling, and centering it:
        offset_width = margin + (workspace_width - scale_factor * self.image_width) / 2
        offset_height = margin + (workspace_height - scale_factor * self.image_height) / 2
        
        # Scaling drawing to A4:
        self.scaled_polylines.clear()
        self.pts_per_polyline.clear()
        
        if not self.polylines:
            print("No polylines to scale.")
            self.stripped_scaled_polylines = np.empty((0, 2), np.float32)
            self.pts_per_polyline = []
            return [], self.stripped_scaled_polylines, self.pts_per_polyline
        
 #chatgpt herfra og ned til comments
       
        # 1) Finn bounding box for selve tegningen (alle polylines)
        all_points = np.vstack([
            pts.reshape(-1, 2) if pts.ndim == 3 else pts
            for pts in self.polylines
            if pts is not None and len(pts) > 0
        ])
        min_x = float(np.min(all_points[:, 0]))
        max_x = float(np.max(all_points[:, 0]))
        min_y = float(np.min(all_points[:, 1]))
        max_y = float(np.max(all_points[:, 1]))

        draw_width_px  = max_x - min_x
        draw_height_px = max_y - min_y
        
        # 2) A4-arbeidsområde i mm
        workspace_width  = self.A4_width  - 2 * margin
        workspace_height = self.A4_height - 2 * margin

        # 3) Skaleringsfaktor basert på tegningens størrelse, ikke bildebufferen
        pixel_width  = workspace_width  / draw_width_px
        pixel_height = workspace_height / draw_height_px
        scale_factor = min(pixel_width, pixel_height)

        # 4) Leftover space → offset for å sentrere tegningen
        scaled_width_mm  = scale_factor * draw_width_px
        scaled_height_mm = scale_factor * draw_height_px

        offset_width  = margin + (workspace_width  - scaled_width_mm)  / 2
        offset_height = margin + (workspace_height - scaled_height_mm) / 2

        # 5) Skaler alle polylines inn på A4
        self.scaled_polylines.clear()
        self.pts_per_polyline.clear()

        for poly in self.polylines:
            if poly is None or len(poly) == 0:
                continue
            if poly.ndim == 3 and poly.shape[1:] == (1, 2):
                poly = poly[:, 0, :]
                if poly.shape[1] != 2:
                    continue

        # Normaliser til bounding box (min_x, min_y) → (0, 0)
        norm = np.empty_like(poly, dtype=np.float32)
        norm[:, 0] = poly[:, 0] - min_x
        norm[:, 1] = poly[:, 1] - min_y

        A4_coords = np.empty_like(norm, dtype=np.float32)
        # X rett fram
        A4_coords[:, 0] = scale_factor * norm[:, 0] + offset_width
        # Y: flip innenfor tegningens høyde, så opp/ned blir riktig
        A4_coords[:, 1] = scale_factor * (draw_height_px - norm[:, 1]) + offset_height

        self.scaled_polylines.append(A4_coords)
        self.pts_per_polyline.append(len(A4_coords))

        if self.scaled_polylines:
            self.stripped_scaled_polylines = np.concatenate(self.scaled_polylines, axis=0)
        else:
            self.stripped_scaled_polylines = np.empty((0, 2), np.float32)

        return self.scaled_polylines, self.stripped_scaled_polylines, self.pts_per_polyline
        
        
        
        
        
        # for poly in self.polylines:
        #     if poly is None or len(poly) == 0:
        #         continue
        #     if poly.ndim == 3 and poly.shape[1:] == (1,2):
        #         poly = poly[:,0,:]
        #     if poly.shape[1] != 2:
        #         continue
        #     self.A4_coordinates = np.empty_like(poly, dtype=np.float32)
        #     self.A4_coordinates[:,0] = scale_factor * poly[:,0] + offset_width
        #     self.A4_coordinates[:,1] = scale_factor * (self.image_height - poly[:,1]) + offset_height # Flips the Y-axis
        #     self.scaled_polylines.append(self.A4_coordinates)
            
        #     self.pts_per_polyline.append(len(poly))
            
        # print("Antall linjer:", len(self.pts_per_polyline))
        # print(self.pts_per_polyline)    
        # print("Antall polylines:", len(self.scaled_polylines))
        # #print(self.scaled_polylines)   
            
        # # Removing [] from array:
        # if len(self.scaled_polylines) > 0:
        #     self.stripped_scaled_polylines = np.concatenate(self.scaled_polylines, axis=0)  # (N, 2)
        #     print("Antall punkter:", len(self.stripped_scaled_polylines))
        #     #print("Eksempel på første 5 punkter:\n", self.stripped_polylines[:5])
        # else:
        #     self.stripped_scaled_polylines = np.empty((0, 2))
        
        # return self.scaled_polylines, self.stripped_scaled_polylines, self.pts_per_polyline
        
 
    
    def show_drawing(self):
        # Show image / object of the drawing
        #cv.imshow(self.image_path, self.image) 
        
        # Show unscaled drawing / strokes:
        blank = 255 * np.ones_like(self.image)
        for pts in self.polylines:
            cv.polylines(blank, [pts.astype(np.int32)], isClosed=False, color=0, thickness=1)
        cv.imshow("Unscaled drawing", blank)
        
        # Close pop-up images at key-press:
        cv.waitKey(0)
        cv.destroyAllWindows()
        
        
    
    def show_scaled_drawing(self, scaling=3.0):

        if not hasattr(self, "scaled_polylines") or len(self.scaled_polylines) == 0:
            raise RuntimeError("No scaled polylines available. Run scale_drawing() first.")

        # Størrelse på A4-lerret i piksler
        canvas_height = int(self.A4_height * scaling)
        canvas_width  = int(self.A4_width  * scaling)

        # Hvit bakgrunn
        hvit_A4 = 255 * np.ones((canvas_height, canvas_width), dtype=np.uint8)

        # Tegn alle polylines: mm -> visningspiksler
        for poly in self.scaled_polylines:
            # poly er (N, 2) i mm; gang opp til piksler
            pts_px = (poly * scaling).astype(np.int32)
            
            #korrigerer y-aksen i opencv
            pts_px[:, 1] = canvas_height - pts_px[:, 1]
            cv.polylines(hvit_A4, [pts_px], isClosed=False, color=0, thickness=1)

        cv.imshow("Scaled drawing on A4", hvit_A4)
        cv.waitKey(0)
        cv.destroyAllWindows()  
        
    

    
if __name__ == "__main__":
    draw = ImageProcessor("Lenna_test.png")
    draw.find_image()
    draw.detect_edges()
    draw.get_polylines()
    draw.scale_drawing()
    draw.show_drawing()
    draw.show_scaled_drawing()