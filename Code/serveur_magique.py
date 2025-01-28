from res_serveur import ServerRes
from banque import BanqueDigitale
from server_banque1 import BanqueServer
import socket
import threading

banque=BanqueDigitale()

def acceuil(utilisateur_socket):
    """Gère l'interaction initiale avec l'utilisateur."""
    try:
        utilisateur_socket.send(
            "Bonjour utilisateur, que voulez-vous faire aujourd'hui ?\n"
            "1. Utiliser la banque\n"
            "2. Réserver une salle\n"
            "0. Quitter\n"
            "Entrez le numéro correspondant à votre choix : ".encode()
        )
        choix = int(utilisateur_socket.recv(1024).decode().strip())  

        if choix == 0:
            utilisateur_socket.send("Merci de nous avoir utilisé. À bientôt !".encode())
            print("L'utilisateur a quitté.")
        elif choix == 1:
            utilisateur_socket.send("Bienvenue dans la banque.\n".encode())
            BanqueServer.occuper_client(utilisateur_socket, banque)
        elif choix == 2:
            utilisateur_socket.send("Bienvenue dans le service de réservation.\n".encode())
            ServerRes.handle_client(utilisateur_socket)
        else:
            utilisateur_socket.send("Choix invalide. Veuillez entrer 0, 1 ou 2.\n".encode())
    except ValueError:
        utilisateur_socket.send("Erreur : Veuillez entrer un nombre valide.\n".encode())
    except Exception as e:
        print(f"Erreur dans le traitement de la requête : {e}")
    finally:
        utilisateur_socket.close()  

def serveur():
    """Démarre le serveur principal."""
    HOST = "127.0.0.1"
    PORT = 1246
    
    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur_socket.bind((HOST, PORT))  
    serveur_socket.listen(5)
    print("Serveur en attente de connexions...")
    

    try:
        while True:
            utilisateur_socket, addr = serveur_socket.accept()
            print(f"Connexion établie avec {addr}")
            thread = threading.Thread(target=acceuil, args=(utilisateur_socket,))
            thread.start()
    except KeyboardInterrupt:
        print("Arrêt du serveur...")
    except Exception as e:
        print(f"Erreur dans le serveur : {e}")
    finally:
        serveur_socket.close()

if __name__ == "__main__":
    serveur()