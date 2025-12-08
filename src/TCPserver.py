from socket import socket, AF_INET, SOCK_STREAM
import sys
from threading import Thread
import numpy as np
import ultralytics as ultra
import cv2 as cv
import torch
import signal


SERVICE_PORT_NAMES_REGISTRATION = 6025
PORT_THIS_SERVICE = 6300
YOLO_MODEL = ultra.YOLO("yolo11n.pt", task = "detect")

def delete_registration(sig, frame):
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    name = sys.argv[1]
    request = "DEL" + "$" + name + "$" + str(PORT_THIS_SERVICE)
    m_client.send(request.encode())
    m_client.close()
    sys.exit(0)

def make_request_register() -> bool:
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    print(f"Conectado ao servidor de registro")

    name = sys.argv[1] #Name need to be passed by the terminal
    request = "REG$" + name + "$" + str(PORT_THIS_SERVICE)
    m_client.send(request.encode())

    response = (m_client.recv(1024)).decode()
    if response == "NAME-ALREADY-IN-USE":
        return False
    else:
        print(f"Nome cadastrado com sucesso, recebido {response}")
        return True

def check_integrity_registration(registrated):
    if registrated == False:
        raise NameError("Nome em uso, não iniciando o servidor")
    else:
        print("Nome registrado, funcionando")

def check_integrity_size_image(size : str):
    assert size.find("x") != -1
    numbers = size.split("x")

    assert len(numbers) == 3
    h, w, c = int(numbers[0]), int(numbers[1]), int(numbers[2])
    
    return h, w, c 


def recv_all(client_socket, bytes_size):
    data = b""

    while len(data) < bytes_size:
        packet = client_socket.recv(bytes_size - len(data))
        if not packet:
            break
        data = data + packet #Concatena os  bytes
    
    return data





def server_face_detection():
    m_server_socket = socket(AF_INET, SOCK_STREAM)
    m_server_socket.bind(("localhost", PORT_THIS_SERVICE)) #IP e porta
    print("[Servidor de detecçao TCP] esperando [...]") 
    
    #Espera comunicação
    m_server_socket.listen()
    while True:
        client_socket, client_addr = m_server_socket.accept() 

        #Cria Thread para lidar com a requisição, multiplos clientes podem fazer requisições
        Thread(target = handle_request_face_detection, args = (client_socket, client_addr)).start()

def handle_request_face_detection(client_socket, client_addr):
    print(f"[Servidor de detecçao TCP] estabeleceu conexao com o {client_addr}")
    
    request = client_socket.recv(1024)
    request = request.decode()
    print(f"[Servidor de detecçao TCP] recebeu o tamanho da imagem {request}")
    h, w, c = check_integrity_size_image(request)

    #1 Byte per pixel
    bytes_size = w * h * c

    #Return to the client the sucessful message
    client_socket.send(("SUCESSFUL").encode())

    while True:
        bytes_image = recv_all(client_socket, bytes_size)
        if len(bytes_image) <= 4 and bytes_image.decode() == "END":
            client_socket.close()
            print(f"[Servidor de detecçao TCP] conexao com {client_addr} fechada")
            break
        #Construct the image
        image = np.frombuffer(bytes_image, dtype=np.uint8)
        image = image.reshape((h, w, c))
        detection = YOLO_MODEL(image, classes = [0])[0]


        #Return the detections positions
        cordinates = detection.boxes.xywh
        response = '[]'
        if len(cordinates) > 0:
            response = str([pc.tolist() for pc in cordinates])        

        client_socket.send(response.encode())



if __name__ == "__main__":
   registrated = make_request_register()
   check_integrity_registration(registrated)
   signal.signal(signal.SIGINT, delete_registration)
   
   server_face_detection_tcp = Thread(target = server_face_detection)

   server_face_detection_tcp.start()
