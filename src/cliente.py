from socket import socket, AF_INET, SOCK_STREAM
import sys

SERVICE_PORT_NAMES_SEARCH = 7000


service_request = sys.argv[1]
m_client = socket(AF_INET, SOCK_STREAM)

def call_names_service(service_request):
    m_client.connect(("localhost", SERVICE_PORT_NAMES_SEARCH))
    print(f"Conectado ao servidor de nome\nEnviando a request {service_request}")
    m_client.send(service_request.encode())
    resposta = m_client.recv(1024)
    resposta = resposta.decode()
    print(f"Recebido: {resposta}")
    return resposta

def check_integrity(response : str):
    if response == "NULL00":
        raise ValueError(f"Server not started yet or do not exist {service_request}")
    else:
        if response.count("-") > 1:
            raise ValueError(f"Wrong format of response, got {response}")
        
        response = response.split("-")
        IP_dest = response[0]
        PORT_dest = int(response[1])
    return IP_dest, PORT_dest

def make_requests(IP_dest, PORT_dest, type_of_conection : str):
    if type_of_conection == "tcp":
        m_client.connect((IP_dest, PORT_dest))
        print(f"Conectado ao servidor de TCP")
        ### APLICAÇÃO, POR ENQUANTO VOU MANDAR SÓ UM OI
        m_client.send(("oi").encode())
        resposta = m_client.recv(1024)
        resposta = resposta.decode()
        print(f"Recebido: {resposta}")

        
    elif type_of_conection == "udp":
            pass


if __name__ == "__main__":
    type_of_conection = "udp" if service_request.find("udp") else "tcp"
    response = call_names_service(service_request)
    IP_dest, PORT_dest = check_integrity(response)
   # make_requests(IP_dest, PORT_dest, type_of_conection)


# Conection to the name service