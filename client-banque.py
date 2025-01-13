import socket

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 12345))

    try:
        while True:
            response = client_socket.recv(1024).decode()
            print(response, end="")
            
            if "À bientôt" in response:  # Détecter la fin de la session
                break
            
            message = input()
            client_socket.send(message.encode())
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    run_client()
