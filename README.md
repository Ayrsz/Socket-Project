# Projeto de Servidor de Nomes Centralizado (Name Server)

Este é um projeto em **Python** que implementa uma arquitetura de microsserviços básica e **centralizada** em um **Servidor de Nomes (Name Server)**. O Servidor de Nomes atua como o ponto central para a descoberta de serviços.

A **regra fundamental** do sistema é: **Se o nome do servidor não estiver registrado no Name Server, o cliente deve ser rejeitado.**

## Requisitos

* **Python 3.8+** (Verifique o `pyproject.toml` para a versão exata)
* **Poetry** (Gerenciador de Dependências Python)

## Instalação e Configuração

Certifique-se de ter o **Poetry** instalado.

1.  **Instalar dependências (via Poetry):**
    ```bash
    poetry install
    ```

2.  **Exibir o source ambiente virtual:**
    ```bash
    poetry env activate
    ```
3.  **Realizar o source:**
    ```bash
    source <caminho indicado pelo poetry no comando anterior>
    ```

---

## Estrutura Sugerida do Repositório

| Arquivo/Diretório | Descrição |
| :--- | :--- |
| `pyproject.toml` | Definição de dependências e metadados do projeto. |
| `src/NAMESserver.py` | **Servidor de Nomes (Name Server).** Ponto de controle central. **Deve ser iniciado primeiro.** |
| `src/TCPserver.py` | **Servidores de Funcionalidade.** Implementam serviços TCP. Se registram no Name Server ao iniciar. |
| `src/UDPserver.py` | **Servidores de Funcionalidade.** Implementam serviços UDP. Se registram no Name Server ao iniciar. |
| `src/client.py` | **Cliente.** Consulta o Name Server para resolver nomes de serviços antes de tentar a conexão. |

---

##  Como Executar (Fluxo Esperado)

O fluxo de execução **obrigatório** é: **Name Server** $\rightarrow$ **Servidores Funcionais** $\rightarrow$ **Clientes**.

### 1. Iniciar o Servidor de Nomes

Execute o Name Server. Ele deve estar ativo antes de qualquer outro componente.

```bash
python3 src/NAMESserver.py
```
### 2. Iniciar um Servidor de Funcionalidade

O servidor se registra no Name Server usando o nome passado como parâmetro.
Convenção de Nomes: Use o sufixo _tcp ou _udp para indicar o protocolo.

## Exemplo de Servidor TCP (usando o arquivo src/TCPserver.py)
```bash
python3 src/TCPserver.py service1_tcp
```
## Exemplo de Servidor UDP (usando o arquivo src/UDPserver.py)
```bash
python3 src/UDPserver.py service2_udp
```

### 3. Executar o Cliente

O cliente passa o nome do serviço desejado. O cliente consulta o Name Server e só então tenta a conexão direta, usando o protocolo correto.

## Cliente acessando o serviço 'service1_tcp'

```bash
python3 src/client.py service1_tcp < timing >
```
Timing é um valor [0, 1], sendo 0 sem a geração de gráficos e 1 com a geração de gráficos. Caso seja setado para 1, a aplicação tem um limite de tempo para executar (1000 ciclos do while True)
ATENÇÃO: Se o nome do serviço não estiver registrado em src/NAMESserver.py, a solicitação do cliente deve ser rejeitada (com uma mensagem de erro apropriada).