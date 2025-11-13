#import sys
#sys.path.append("C:\\Users\\mathe\\OneDrive\\Skrivebord\\School\\Intro til robotikk\\Prosjekt")
import numpy as np
import sys

#import functions from other script
import read_from_robot
import send_to_robot
import retrieve_image
from image_processing import ImageProcessor



def main():
    artist = PierreRobot(image_path="Lenna_test.png")
    artist.greet_user()
    artist.take_photo()
    artist.setup_workspace()
    artist.setup_drawing()
    artist.calculate_poses()
    artist.move_robot()



class PierreRobot:
    
    def __init__(self, image_path="Lenna_test.png"):
        self.image_path = image_path
        self.paper_pose = None
        self.marker_pose = None
        self.img = None
        self.translated_array = None
        self.pts_per_polyline = None
        self.updated_pose = None
        self.move_array = None
    
    
    
    def greet_user(self):
        #Wait for initial inputs from user: ---------------------------------------------------------------
        print("Bonjour! Je m'appelle Pierre Robot, ze best painter in all of France.\n")
        print("You are beautiful, I want to - how you say - paint you. \n")
        print("But first, there are a few things you need to tell me:\n")
        #Telling user to start UR3 program so we can gather the different POSEs and download the image of the participant.
        while True:
            go_ahead = input("On the UR3 computer, run the program. Am I looking at your beautiful face? (y/n)")
            if go_ahead != "y":
                print("Excusez-moi, wait for the move command to finish s'il vous plaît.")
            else:
                print("Formidable!")
                break
    
    
    
    def take_photo(self):
        #retrieve image er kommentert ut her siden vi bruker fil. av-kommenter denne hvis vi faktisk skal ta bilde med roboten.
        while True:
            go_ahead = input("Should i take the photo now? (y/n)")
            if go_ahead != "y":
                print("Excusez-moi, reposistion the camera so I can see you better s'il vous plaît.")
            else:
                #retrieve_image.save_image(read_from_robot.HOST)
                send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
                print("Fantastique! I shall use your lovely image as a - how you say - reference.")
                break
            
            
            
    def setup_workspace(self):
        while True:
            go_ahead = input("Am I at the paper yet? (y/n)")
            if go_ahead != "y":
                print("Excusez-moi, wait for the move command to finish s'il vous plaît.")
            else:
                self.paper_pose = read_from_robot.get_pose()
                send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
                print("Fantastique! I now know where the paper is.")
                break
        while True:
            go_ahead = input("Am I at the marker yet? (y/n)")
            if go_ahead!= "y":
                print("That is ok! Wait for the move command to finish.")
            else:
                self.marker_pose = read_from_robot.get_pose()
                send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
                print("Wonderful! I now know where my tool is")
                break
        #print paper and marker pose so we can check if the later arrays make sense.
        print("paper POSE original: ", self.paper_pose)
        print("marker POSE original: ", self.marker_pose)
    
    
    
    def setup_drawing(self):
        # Image processing: --------------------------------------------------------------------------
        self.img = ImageProcessor(self.image_path)
        self.img.find_image()
        self.img.detect_edges()
        self.img.get_polylines()
        scaled_polylines, stripped_scaled_polylines, pts_per_polyline = self.img.scale_drawing()
        self.img.show_scaled_drawing()
        
        #show the final image with vectors to the user to check if the image processing has been successful
        while True:
            image_quality = input("Is the final image good enough to be drawn by the robot? (y/n)")
            if image_quality != "y":
                print('OK, take a look at the tuning parameters in the "image_processing" script and try again.')
                sys.exit()
            else:
                break
        
        #adding marker height to paper_pose so the move instructions compensate for the height of the marker:
        paper_pose = np.array(self.paper_pose, dtype=float)
        marker_pose = np.array(self.marker_pose, dtype=float)
        paper_pose[2] = marker_pose[2] - 1.8
        self.paper_pose = paper_pose

        #array of points used to draw image from image_processing:
        self.translated_array = stripped_scaled_polylines
        self.pts_per_polyline = pts_per_polyline
        print(f'translated array = {self.translated_array}')
        
        #return scaled_polylines, self.translated_array, self.pts_per_polyline
        
        
        
    #Convert vectors to Movel instructions: ------------------------------------------------    
    def calculate_poses(self, teta=3*np.pi/4, decimals=4):
        
        #initializing values for later POSE transformations
        rotasjon = np.array([[np.cos(teta), -np.sin(teta)],
                             [np.sin(teta), np.cos(teta)]], dtype=float).T # Transposed
        
        #rotating our mm values to compensate for coordinate system of robot vs paper.
        self.translated_array = (self.translated_array @ rotasjon)
            
            
        print(f'translated array rotated {self.translated_array}')
        
        #Initializing empty arrays for updated pose (our x,y in terms of the paper) and move array (the strings we send the robot) 
        self.updated_pose = np.zeros([len(self.translated_array), 6])
        self.move_array = [""]*(len(self.translated_array))
        
        #transposing paper POSE so we can do matrix operations on it later
        self.paper_pose = np.array(self.paper_pose, dtype=float).reshape(6, 1)
        
        print(f'paper pose: {self.paper_pose}')
        
        #corner of the a4 is a pure y translation using pythagoras of the height and length of a4:
        self.paper_pose[0] = self.paper_pose[0] + (np.sqrt((((297)/2)**2)+(((210)/2)**2)))
        
        print(f'paper pose corner: {self.paper_pose}')
        
 #sjekk
        print("Før konvertering til meter (paper_pose):", self.paper_pose.T)
        print("Før konvertering til meter (første 5 translated_array):", self.translated_array[:5])
        
        #multiplying paper pose x,y,z by 0.001 to get them in meters - necessary for Move instructions
        self.paper_pose[0] = self.paper_pose[0]*0.001
        self.paper_pose[1] = self.paper_pose[1]*0.001
        self.paper_pose[2] = self.paper_pose[2]*0.001
        self.paper_pose = np.round(self.paper_pose, decimals)
        
        #multiplying our x,y mm by 0.001 to get them in meters - necessary for Move instructions
        self.translated_array *= 0.001
        self.translated_array = np.round(self.translated_array, decimals)
        
  #test
        print("Etter konvertering til meter (paper_pose):", self.paper_pose.T)
        print("Etter konvertering til meter (første 5 translated_array):", self.translated_array[:5])
        print("Første 10 updated_pose:")
        for i in range(10):
            print(i, self.updated_pose[i])
        
        #adding our x,y mm to paper pose to get them in terms of the world coordinates. putting everything in updated_pose.
        self.updated_pose[:,0] = self.paper_pose[0]+self.translated_array[:,0]
        self.updated_pose[:,1] = self.paper_pose[1]+self.translated_array[:,1]
        self.updated_pose[:,2] = self.paper_pose[2]
        self.updated_pose[:,3] = self.paper_pose[3]
        self.updated_pose[:,4] = self.paper_pose[4]
        self.updated_pose[:,5] = self.paper_pose[5]
        
        self.updated_pose = np.round(self.updated_pose, decimals)
        
        print(f'pose values: {self.updated_pose}')
        
        #adding all our POSE values to the movel string we send to the robot:
        for i in range(len(self.move_array)) :
            self.move_array[i] = "movel(p["+str(self.updated_pose[i,0])+","+str(self.updated_pose[i,1])+","+str(self.updated_pose[i,2])+","+str(self.updated_pose[i,3])+","+str(self.updated_pose[i,4])+","+str(self.updated_pose[i,5])+"], 0.1, 0.1)"
        
        print(f'Position of paper: {self.paper_pose}')
        
        print("Første 10 Z-verdier i updated_pose:", self.updated_pose[:10, 2])
        
        #asking user if arrays look ok. 
        while True:
            go_ahead = input("Do the arrays look good? (y/n)")
            if go_ahead != "y":
                print('OK, try again.')
                sys.exit()
            else:
                break
            
        
        
    def move_robot(self, lift_pen=0.02):
        #Sending move instructions to robot. The loop will only continue if the loop in read_from_robot breaks which happens when the tool speed is less than 0.005.
        polylines = 0
        cumulative_lengths = np.cumsum(self.pts_per_polyline) - 1  # Last index in each polyline

        for i, inst in enumerate(self.move_array):
            send_to_robot.sendCommand(inst)
            read_from_robot.wait_for_move_end()
    
            if polylines < len(cumulative_lengths) and i == cumulative_lengths[polylines]:
                print("polyline ended")   
                
                last_pose = self.updated_pose[i].copy()
                lift_pose = last_pose.copy()
                lift_pose[2] += lift_pen
                #pose = read_from_robot.get_pose()
                #pose = np.array(pose, dtype=float)
                #pose[:3] = pose[:3] * 0.001
                #pose[2] = pose[2] + lift_pen

                cmd = ("movel(p["+str(lift_pose[0])+","+str(lift_pose[1])+","+str(lift_pose[2])+","+str(lift_pose[3])+","+str(lift_pose[4])+","+str(lift_pose[5])+"], 0.1, 0.1)")
                send_to_robot.sendCommand(cmd)
                read_from_robot.wait_for_move_end()
                
                polylines += 1
        print("Voila! I hope you like it.")


if __name__ == "__main__":
    main()

