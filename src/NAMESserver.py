from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time
import os
import cv2 as cv
import sys

SERVICES_NAMES = dict()

SERVICE_PORT_NAMES_REGISTRATION = 6000
SERVICE_PORT_NAMES_SEARCH = 7000


def check_if_service_exists(name : str) -> bool:
    names = list(SERVICES_NAMES.keys())
    if names == []:
        return False
    if name in names:
        return True
    else:
        return False

# Thread que vai escutar requisições da aplicação para registro
def service_names_registration():
    m_server_socket = socket(AF_INET, SOCK_STREAM)
    m_server_socket.bind(("localhost", SERVICE_PORT_NAMES_REGISTRATION)) #IP e porta
    print("[Servidor de registros] esperando [...]") 
    
    #Espera comunicação
    m_server_socket.listen()
    while True:
        client_socket, client_addr = m_server_socket.accept() 

        #Cria Thread para lidar com a requisição, multiplos clientes podem fazer requisições
        Thread(target = handle_request_register, args = (client_socket, client_addr)).start()

def handle_request_register(client_socket, client_addr):
    print(f"[Servidor de registros] estabeleceu conexao com o {client_addr}")
    
    request = client_socket.recv(1024)
    request = request.decode()

    exists = check_if_service_exists(request)
    if exists:
        response = "NAME-ALREADY-IN-USE"
        response.encode()
        client_socket.send(response)
    else:
        print(f"REGISTRATIN THE NAME {request}:{client_socket}")
        SERVICES_NAMES[request] = client_socket #Registra o IP e a PORTA
        response = f"SUCESSFUL-REGISTRATE-{request}-NAME"
        response = response.encode()
        client_socket.send(response)

    client_socket.close()


    

# Thread que vai escutar requisições dos usuários que irão pedir endereços
def service_names_requests():
    
    n_server_socket = socket(AF_INET, SOCK_STREAM)
    n_server_socket.bind(("localhost", SERVICE_PORT_NAMES_SEARCH)) #IP e porta
    print("[Servidor de nomes] esperando [...]") 
    
    #Espera comunicação
    n_server_socket.listen()
    while True:
        client_socket, client_addr = n_server_socket.accept() 

        #Cria Thread para lidar com a requisição, multiplos clientes podem fazer requisições
        Thread(target = handle_request_names, args = (client_socket, client_addr)).start()

# Thread que vai lidar com as requisições do usuário, se existir endereço registrado, retorne, senão NULL
def handle_request_names(client_socket, client_addr):
    print(f"[Servidor de nomes] estabeleceu conexao com o {client_addr}")
    
    request = client_socket.recv(1024)
    request = request.decode()
    print(f"[Servidor de nomes] recebeu a requisição {request}")

    exists = check_if_service_exists(request)
    
    if exists == True:
        IP_adress, port = SERVICES_NAMES[request]
        locate = str(IP_adress) + "-" +  str(port)
        locate = locate.encode()
        client_socket.send(locate)
    else:
        locate = "NULL"
        locate = locate.encode()
        client_socket.send(locate)
    
    client_socket.close()



#Inicializa socket servidor
if __name__ == "__main__":
    server_names_request = Thread(target = service_names_requests)
    server_names_registration = Thread(target = service_names_registration)

    server_names_registration.start()
    server_names_request.start()

   # server_names_request.join()
   # server_names_registration.join()