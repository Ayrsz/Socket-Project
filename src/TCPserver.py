from socket import socket, AF_INET, SOCK_STREAM
import sys

SERVICE_PORT_NAMES_REGISTRATION = 6000
PORT_THIS_SERVICE = 6300


def make_request_register() -> bool:
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    print(f"Conectado ao servidor de registro")

    name = sys.argv[1] #Name need to be passed by the terminal
    m_client.send(name.encode())

    response = (m_client.recv(1024)).decode()
    if response == "NAME-ALREADY-IN-USE":
        return False
    else:
        print(f"Nome cadastrado com sucesso, recebido {response}")
        return True


if __name__ == "__main__":
    registrated = make_request_register()
    if registrated == False:
        raise NameError("Nome em uso, não iniciando o servidor")
    else:
        pass