#import sys
#sys.path.append("C:\\Users\\mathe\\OneDrive\\Skrivebord\\School\\Intro til robotikk\\Prosjekt")
import numpy as np
import time

#import functions from other script
import read_from_robot
import send_to_robot
import retrieve_image
import image_processing


#Wait for input asking for user to snap a pic
print("Bonjour! I am Pierre Robot, ze best painter in all of France.\n")
print("You are beautiful, I want to - how you say - paint you. \n")
print("But first, there are a few things you need to tell me:\n")

while True:
    go_ahead = input("On the UR3 computer, run the program. Am I looking at your beautiful face? (y/n)")
    if go_ahead != "y":
        print("That is ok! Wait for the move command to finish.")
    else:
        participant_pose = read_from_robot.get_pose()
        print("Wonderful! I now know where you are")
        break

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

#print section to check against:
print("paper POSE original: ", paper_pose)
print("marker POSE original: ", marker_pose)

# Image processing:
img = image_processing.ImageProcessor("Lenna_test.png")
img.image_processing()
img.show_image()

while True:
    image_quality = input("Is the final image good enough to be drawn by the robot? (y/n)")
    if image_quality != "y":
        print('OK, take a look at the tuning parameters in the "image_processing" script and try again.')
        quit()
    else:
        break

#adding marker height to paper_pose:
paper_pose[2] = marker_pose[2]-2.5

#array of points used to draw image from image_processing:
px_array = img.stripped_polylines
dimensions = img.dimensions()
print(f'pixel array = {px_array}')

total_pixels_x, total_pixels_y, middle_point_pixels = dimensions


translated_array = np.zeros([(len(px_array)), 2])
print(f'pixel array : {px_array}')
print(f'rows in pixel array: {len(px_array)}')

for i in range(2):
    for row, value in enumerate(translated_array):
            value[0] = (px_array[row,0]/total_pixels_x)*img.A4X
            value[1] = (px_array[row,1]/total_pixels_y)*img.A4Y

print(f'mm array: {translated_array}')

#Convert vectors to Movel instructions:
teta = -3*np.pi/4
rotasjon = np.array([[np.cos(teta), -np.sin(teta)], [np.sin(teta), np.cos(teta)]]) 

for i in translated_array:
    i = rotasjon*np.transpose(i)
    i = np.transpose(i)
    
updated_pose = np.zeros([len(translated_array), 6])
move_array = [""]*(len(translated_array))

paper_pose = np.array([paper_pose])

paper_pose = paper_pose.astype(float)
paper_pose = np.transpose(paper_pose)
print(paper_pose)

a4 = np.array([[img.A4X/2, img.A4Y/2]])
rotert_a4 = rotasjon*np.transpose(a4)
rotert_a4 = np.transpose(rotert_a4)
print(rotert_a4)
print(np.transpose(a4))

paper_pose[0] = paper_pose[0] - (rotert_a4[0,0]-rotert_a4[1,0])
paper_pose[1] = paper_pose[1] - (rotert_a4[0,1]+rotert_a4[1,1])
paper_pose[2:] = paper_pose[2:]

paper_pose[0] = paper_pose[0]*0.001
paper_pose[1] = paper_pose[1]*0.001
paper_pose[2] = paper_pose[2]*0.001
paper_pose = np.round(paper_pose, decimals=4)

for i in range(len(translated_array)):
    translated_array[i,0] = ((translated_array[i,0])*0.001)
    translated_array[i,1] = ((translated_array[i,1])*0.001)

translated_array = np.round(translated_array, decimals=4)

updated_pose[:,0] = paper_pose[0]-translated_array[:,0]
updated_pose[:,1] = paper_pose[1]-translated_array[:,1]
updated_pose[:,2] = paper_pose[2]
updated_pose[:,3] = paper_pose[3]
updated_pose[:,4] = paper_pose[4]
updated_pose[:,5] = paper_pose[5]

updated_pose = np.round(updated_pose, decimals=4)

for i in range(len(move_array)) :
    move_array[i] = "movel(p["+str(updated_pose[i,0])+","+str(updated_pose[i,1])+","+str(updated_pose[i,2])+","+str(updated_pose[i,3])+","+str(updated_pose[i,4])+","+str(updated_pose[i,5])+"], 0.1, 0.1)"

print(f'Position of paper: {paper_pose}')
print(f' Move array: {move_array}')
while True:
    go_ahead = input("Do the arrays look good? (y/n)")
    if go_ahead != "y":
        print('OK, try again.')
        quit()
    else:
        break

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





