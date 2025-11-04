import webbrowser
import requests

robot_ip = "192.168.12.55"

url = "http://"+robot_ip+":4242/current.jpg?annotations=\<on\|off\>"

webbrowser.open(url)



