import socket

def lancer_client():
    utilisateur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        utilisateur_socket.connect(('127.0.0.1', 1246))  

        while True:
            
            reponse = utilisateur_socket.recv(1024).decode()
            if not reponse:
                print("\nConnexion fermée par le serveur.")
                break  
            print(reponse, end='')

            
            message = input()
            utilisateur_socket.send(message.encode())

    except ConnectionRefusedError:
        print("Erreur : Impossible de se connecter au serveur. Assurez-vous qu'il est en cours d'exécution.")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        utilisateur_socket.close()  

if __name__ == "__main__":
    lancer_client()
