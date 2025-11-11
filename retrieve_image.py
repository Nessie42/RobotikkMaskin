import webbrowser
import requests

def save_image(ip):
   '''
   explenation

   args:

   returns:
   
   '''
   robot_ip = ip
   url = "http://"+robot_ip+":4242/current.jpg?annotations=\<on\|off\>"
   
   r = requests.get(url, stream=False)
   
   with open('robot_image.jpeg', 'wb') as fd:
         for chunk in r.iter_content(chunk_size=128):
             fd.write(chunk)

save_image('192.168.12.55')


    

