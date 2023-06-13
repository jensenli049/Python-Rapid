import socket

IP = "127.0.0.1" #"192.168.125.1"
PORT = 5024
ADDRESS = (IP, PORT)

print(ADDRESS)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDRESS)


while True:
    data = input("Input your name: ")

    if data == "":
        print("No data")
        continue
    elif data == "stop":
        print("Python code stopped.")
        break
    else:
        s.send(bytes(str(data),"utf-8"))

