#import sys
#sys.path.append("C:\\Users\\mathe\\OneDrive\\Skrivebord\\School\\Intro til robotikk\\Prosjekt")
import numpy as np
import time

#import functions from other script
import read_from_robot
import send_to_robot
import retrieve_image
import image_processing


#Wait for initial inputs from user: ---------------------------------------------------------------
print("Bonjour! I am Pierre Robot, ze best painter in all of France.\n")
print("You are beautiful, I want to - how you say - paint you. \n")
print("But first, there are a few things you need to tell me:\n")

#Telling user to start UR3 program so we can gather the different POSEs and download the image of the participant.
while True:
    go_ahead = input("On the UR3 computer, run the program. Am I looking at your beautiful face? (y/n)")
    if go_ahead != "y":
        print("That is ok! Wait for the move command to finish.")
    else:
        participant_pose = read_from_robot.get_pose()
        print("Wonderful! I now know where you are")
        break

#retrieve image er kommentert ut her siden vi bruker fil. av-kommenter denne hvis vi faktisk skal ta bilde med roboten.
while True:
    go_ahead = input("Should i take the photo now? (y/n)")
    if go_ahead != "y":
        print("That is ok! Reposistion the camera so I can see you better.")
    else:
        #retrieve_image.save_image(read_from_robot.HOST)
        send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
        print("Fantastique! I shall use your lovely image as a - how you say - reference.")
        break

while True:
    go_ahead = input("Am I at the paper yet? (y/n)")
    if go_ahead != "y":
        print("That is ok! Wait for the move command to finish.")
    else:
        paper_pose = read_from_robot.get_pose()
        send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
        print("Fantastique! I now know where the paper is.")
        break

while True:
    go_ahead = input("Am I at the marker yet? (y/n)")
    if go_ahead!= "y":
        print("That is ok! Wait for the move command to finish.")
    else:
        marker_pose = read_from_robot.get_pose()
        send_to_robot.sendCommand('sec secondaryProg():\nset_digital_out(0, False)\nend')
        print("Wonderful! I now know where my tool is")
        break

#print paper and marker pose so we can check if the later arrays make sense.
print("paper POSE original: ", paper_pose)
print("marker POSE original: ", marker_pose)

# Image processing: --------------------------------------------------------------------------
img = image_processing.ImageProcessor("Lenna_test.png")
img.image_processing()
img.show_image()

#show the final image with vectors to the user to check if the image processing has been successful
while True:
    image_quality = input("Is the final image good enough to be drawn by the robot? (y/n)")
    if image_quality != "y":
        print('OK, take a look at the tuning parameters in the "image_processing" script and try again.')
        quit()
    else:
        break

#adding marker height to paper_pose so the move instructions compensate for the height of the marker:
paper_pose[2] = marker_pose[2]-1.8

#array of points used to draw image from image_processing:
px_array = img.stripped_polylines
dimensions = img.dimensions()
print(f'pixel array = {px_array}')

total_pixels_x, total_pixels_y, middle_point_pixels = dimensions

#initializing an array of zeroes the same size as px_array so we can put the mm values in later.
translated_array = np.zeros([(len(px_array)), 2])
print(f'pixel array : {px_array}')
print(f'rows in pixel array: {len(px_array)}')

#sizing down the pixel array so the largest value becomes 210mm and all other values are scaled by the same factor.
#basically her gjør vi om px til mm.
px_array = np.array(px_array)
factor = 210/(np.max(px_array))
px_array = px_array * factor

print(px_array)

#legger inn mm verdiene i translated array. Gjør dette mest fordi all videre kode bruker translated array.
for i in range(2):
    for row, value in enumerate(translated_array):
            value[0] = px_array[row,0]
            value[1] = px_array[row,1]


print(f'mm array: {translated_array}')

#Convert vectors to Movel instructions: ------------------------------------------------

#initializing values for later POSE transformations
teta = 3*np.pi/4
rotasjon = np.array([[np.cos(teta), -np.sin(teta)], [np.sin(teta), np.cos(teta)]])
rotasjon = np.transpose(rotasjon) 
print(rotasjon)

#rotating our mm values to compensate for coordinate system of robot vs paper.
for i in range(len(translated_array)):
    translated_array[i] = np.transpose(np.matmul(rotasjon, np.transpose(translated_array[i])))
    

print(f'translated array rotated {translated_array}')

#Initializing empty arrays for updated pose (our x,y in terms of the paper) and move array (the strings we send the robot) 
updated_pose = np.zeros([len(translated_array), 6])
move_array = [""]*(len(translated_array))

paper_pose = np.array([paper_pose])

#transposing paper POSE so we can do matrix operations on it later
paper_pose = paper_pose.astype(float)
paper_pose = np.transpose(paper_pose)

print(f'paper pose: {paper_pose}')

#corner of the a4 is a pure y translation using pythagoras of the height and length of a4:
paper_pose[1] = paper_pose[1] + (np.sqrt((((297)/2)**2)+(((210)/2)**2)))

print(f'paper pose corner: {paper_pose}')

#multiplying paper pose x,y,z by 0.001 to get them in meters - necessary for Move instructions
paper_pose[0] = paper_pose[0]*0.001
paper_pose[1] = paper_pose[1]*0.001
paper_pose[2] = paper_pose[2]*0.001
paper_pose = np.round(paper_pose, decimals=4)

#multiplying our x,y mm by 0.001 to get them in meters - necessary for Move instructions
for i in range(len(translated_array)):
    translated_array[i,0] = ((translated_array[i,0])*0.001)
    translated_array[i,1] = ((translated_array[i,1])*0.001)

translated_array = np.round(translated_array, decimals=4)

#adding our x,y mm to paper pose to get them in terms of the world coordinates. putting everything in updated_pose.
updated_pose[:,0] = paper_pose[0]+translated_array[:,0]
updated_pose[:,1] = paper_pose[1]+translated_array[:,1]
updated_pose[:,2] = paper_pose[2]
updated_pose[:,3] = paper_pose[3]
updated_pose[:,4] = paper_pose[4]
updated_pose[:,5] = paper_pose[5]

updated_pose = np.round(updated_pose, decimals=4)

print(f'pose values: {updated_pose}')

#adding all our POSE values to the movel string we send to the robot:
for i in range(len(move_array)) :
    move_array[i] = "movel(p["+str(updated_pose[i,0])+","+str(updated_pose[i,1])+","+str(updated_pose[i,2])+","+str(updated_pose[i,3])+","+str(updated_pose[i,4])+","+str(updated_pose[i,5])+"], 0.1, 0.1)"

print(f'Position of paper: {paper_pose}')

#asking user if arrays look ok. 
while True:
    go_ahead = input("Do the arrays look good? (y/n)")
    if go_ahead != "y":
        print('OK, try again.')
        quit()
    else:
        break


#Sending move instructions to robot. The loop will only continue if the loop in read_from_robot breaks which happens when the tool speed is less than 0.005.
polylines = 0
liste = img.liste
img.scale_px_to_mm()
for i, inst in enumerate(move_array):
    send_to_robot.sendCommand(inst)
    read_from_robot.wait_for_move_end()
    if i == liste[polylines]:
        polylines = polylines+1
        pose = read_from_robot.get_pose()
        pose = np.array(pose, dtype=float)
        pose[:] = pose[:]*0.001
        pose[2] = pose[2]-0.02
        send_to_robot.sendCommand("movel(p["+str(pose[0])+","+str(pose[1])+","+str(pose[2])+","+str(pose[3])+","+str(pose[4])+","+str(pose[5])+"], 0.1, 0.1)")

print("Voila! I hope you like it.")





