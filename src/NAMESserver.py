import socket as sck
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time
import os
import cv2 as cv
import sys

#Detect ctrl+c
import signal 
SERVICES_NAMES = dict()

SERVICE_PORT_NAMES_REGISTRATION = 6025
SERVICE_PORT_NAMES_SEARCH = 7025
REGISTER_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
REQUEST_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)

def delete_service_name(ip, port):
    key = None
    for key, value in SERVICES_NAMES.items():
        if value == (ip, port):
            key_to_delete = key
    if key is not None:
        del SERVICES_NAMES[key_to_delete]


def check_if_service_exists(name : str) -> bool:
    names = list(SERVICES_NAMES.keys())
    if names == []:
        return False
    if name in names:
        return True
    else:
        return False

# Thread que vai escutar requisições da aplicação para registro
def service_names_registration_tcp():

    #Permitir que CTRL+C libere logo a porta
    REGISTER_SERVER_SOCKET.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)
    REGISTER_SERVER_SOCKET.bind(("localhost", SERVICE_PORT_NAMES_REGISTRATION)) #IP e porta
    print("[Servidor de registros] esperando [...]") 
    
    #Espera comunicação
    REGISTER_SERVER_SOCKET.listen()
    while True:
        client_socket, client_addr = REGISTER_SERVER_SOCKET.accept() 

        #Cria Thread para lidar com a requisição, multiplos clientes podem fazer requisições
        Thread(target = handle_request_register, args = (client_socket, client_addr)).start()

def handle_request_register(client_socket, client_addr):
    print(f"[Servidor de registros] estabeleceu conexao com o {client_addr}")
    
    request = client_socket.recv(1024)
    request : str = request.decode()
    if request.startswith("DEL"):
        type_req, del_name_request, PORT_TO_DELETE = request.split("$")
        IP_TO_DELETE = client_addr[0]
        print("[Servidor de registros] DELETANDO", IP_TO_DELETE, PORT_TO_DELETE)
        delete_service_name(IP_TO_DELETE, PORT_TO_DELETE)


    elif request.startswith("REG"):
        #Request is of the type "name_service$port_of_the_service"
        type_req, new_name_request, port_of_service = request.split("$")

        exists = check_if_service_exists(new_name_request)
        if exists:
            response = "NAME-ALREADY-IN-USE"
            client_socket.send(response.encode())
        else:
            print(f"[Servidor de registros] nome registrado {request}:{client_addr}")

            SERVICES_NAMES[new_name_request] = (client_addr[0], port_of_service) #Registra o IP e a PORTA
            response = f"SUCESSFUL-REGISTRATE-{new_name_request}-NAME"
            response = response.encode()
            client_socket.send(response)
            print(f"[Servidor de registros] novos nomes registrados {SERVICES_NAMES}")

    client_socket.close()


    

# Thread que vai escutar requisições dos usuários que irão pedir endereços
def service_names_requests():
    
    REQUEST_SERVER_SOCKET.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)

    REQUEST_SERVER_SOCKET.bind(("localhost", SERVICE_PORT_NAMES_SEARCH)) #IP e porta
    print("[Servidor de nomes] esperando [...]") 
    
    #Espera comunicação
    REQUEST_SERVER_SOCKET.listen()
    while True:
        
        client_socket, client_addr = REQUEST_SERVER_SOCKET.accept()
        
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
    server_names_registration = Thread(target = service_names_registration_tcp)


    server_names_registration.start()
    server_names_request.start()
