#test
import numpy as np

A4X = 210.0
A4Y = 297.0
A4MIDDLE = ([210.0/2.0, 297.0/2.0])

paper_pose = ([['X_actual = 203.9755\n', 'Y_actual = -273.2781\n', 'Z_actual = -283.9514\n', 'Rx_actual = -2.8687\n', 'Y_actual = -273.2781\n', 'Z_actual = -283.9514\n']])

for i in range(6):
    for pose in paper_pose:
        original_string = pose[i]
        new_string = ""
        for char in original_string:
            if char.isdigit() or char == ".":
                new_string += char
        pose[i] = float(new_string)

print(paper_pose)

translated_array = np.array([[100.0,55.0,0,0,0,0],
                             [200.0,55.0,0,0,0,0],
                             [200.0,155.0,0,0,0,0],
                             [100.0,155.0,0,0,0,0]])

paper_pose = np.transpose(paper_pose)

#Convert vectors to Movel instructions:
updated_pose = np.zeros([len(translated_array), 6])
move_array = [""]*(len(translated_array))

for i in range(len(translated_array)):
    print(i)
    translated_array[i,0] = ((translated_array[i,0]-A4MIDDLE[0])*0.001)
    translated_array[i,1] = ((translated_array[i,0]-A4MIDDLE[1])*0.001)

print(translated_array)
print(updated_pose[1])

updated_pose[:,0] = paper_pose[0]+translated_array[:,0]
updated_pose[:,1] = paper_pose[1]+translated_array[:,1]

print(updated_pose)

'''
for row in range(len(updated_pose)):
    print(row)
    print(range(len(updated_pose)))
    for item in row:
        item = paper_pose[0]+translated_array[row,0]
        item = paper_pose[1]+translated_array[row,1]

'''