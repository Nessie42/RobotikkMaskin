#import sys
#sys.path.append("C:\\Users\\mathe\\OneDrive\\Skrivebord\\School\\Intro til robotikk\\Prosjekt")
import numpy as np

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
        retrieve_image.save_image(read_from_robot.HOST)
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


#image processing:
image = image_processing.gray_and_blur('robot_image.jpeg', [3,3])

contours_edge, contours_thresh, image_contours= image_processing.vectorize_image(image)

simple_vectors, simple_vector_image = image_processing.simplifying_vectors(image, contours_thresh, 0.1)

image_processing.image_for_tuning(simple_vector_image)

while True:
    image_quality = input("Is the final image good enough to be drawn by the robot? (y/n)")
    if image_quality != "y":
        print('OK, take a look at the tuning parameters in the "image_processing" script and try again.')
        quit()
    else:
        break

#adding marker height to paper_pose:
paper_pose[2] = marker_pose[2]


#array of points used to draw image from image_processing:
px_array = simple_vectors

total_pixels_x, total_pixels_y, middle_point_pixels = image_processing.dimensions(image)

A4X = 210.0
A4Y = 297.0
A4MIDDLE = ([210.0/2.0, 297.0/2.0])

'''
translated_array = np.zeros([(len(px_array)), 2])

for i in range(len(translated_array)):
    translated_array[i,0] = ((px_array[i,0])/total_pixels_x)*A4X
    translated_array[i,1] = ((px_array[i,1])/total_pixels_y)*A4Y
'''

translated_array = np.array([[100.0,55.0,0,0,0,0],
                             [200.0,55.0,0,0,0,0],
                             [200.0,155.0,0,0,0,0],
                             [100.0,155.0,0,0,0,0]])

#Convert vectors to Movel instructions:
updated_pose = np.zeros([len(translated_array), 6])
move_array = [""]*(len(translated_array))

paper_pose = np.array([paper_pose])

paper_pose = paper_pose.astype(float)
paper_pose = np.transpose(paper_pose)
print(paper_pose)

paper_pose[0] = paper_pose[0]*0.001
paper_pose[1] = paper_pose[1]*0.001
paper_pose[2] = paper_pose[2]*0.001
paper_pose = np.round(paper_pose, decimals=4)

for i in range(len(translated_array)):
    translated_array[i,0] = ((translated_array[i,0]-A4MIDDLE[0])*0.001)
    translated_array[i,1] = ((translated_array[i,1]-A4MIDDLE[1])*0.001)

translated_array = np.round(translated_array, decimals=4)

updated_pose[:,0] = paper_pose[0]+translated_array[:,0]
updated_pose[:,1] = paper_pose[1]+translated_array[:,1]
updated_pose[:,2] = paper_pose[2]
updated_pose[:,3] = paper_pose[3]
updated_pose[:,4] = paper_pose[4]
updated_pose[:,5] = paper_pose[5]

'''
for i in range(len(translated_array)):
    updated_pose[i,0] = paper_pose[0]+translated_array[i,0]
    updated_pose[i,1] = paper_pose[1]+translated_array[i,1]
    updated_pose[i,2] = paper_pose[2]
    updated_pose[i,3] = paper_pose[3]
    updated_pose[i,4] = paper_pose[4]
    updated_pose[i,5] = paper_pose[5]

    updated_pose[i,0] = round(updated_pose[i,0], 4)
    updated_pose[i,1] = round(updated_pose[i,1], 4)
'''
    
for i in range(len(move_array)) :
    move_array[i] = "movel(p["+str(updated_pose[i,0])+","+str(updated_pose[i,1])+","+str(updated_pose[i,2])+","+str(updated_pose[i,3])+","+str(updated_pose[i,4])+","+str(updated_pose[i,5])+"], 0.1, 0.1)"

print(paper_pose)
print(move_array)
while True:
    go_ahead = input("Do the arrays look good? (y/n)")
    if image_quality != "y":
        print('OK, try again.')
        quit()
    else:
        break


#Run program sending move instructions to robot and waiting for feedback until next instruction
for i in move_array:
    print(i)
    send_to_robot.sendCommand(i)
    read_from_robot.wait_for_move_end()
 
print("Voila! I hope you like it.")





