import socket
import threading
from banque import BanqueDigitale  # Importation du module banque.py

def handle_client(client_socket, banque):
    try:
        client_socket.send("Bienvenue dans la Banque Digitale\n".encode())
        while True:
            client_socket.send("Que voulez-vous faire ? (1: Se connecter, 2: S'inscrire, 3: Quitter) : ".encode())
            choix = client_socket.recv(1024).decode().strip()

            if choix == "1":
                client_socket.send("Entrez votre numéro de compte : ".encode())
                num_compte = client_socket.recv(1024).decode().strip()

                client_socket.send("Entrez votre mot de passe : ".encode())
                mot_de_passe = client_socket.recv(1024).decode().strip()

                if banque.verifier_mot_de_passe(num_compte, mot_de_passe):
                    client_socket.send("Connexion réussie. Bienvenue !\n".encode())

                    # Options après connexion
                    while True:
                        client_socket.send("Que voulez-vous faire ? (1: Retrait, 2: Dépôt, 3: Consultation solde, 4: Quitter) : ".encode())
                        option = client_socket.recv(1024).decode().strip()

                        if option == "1":  # Retrait
                            client_socket.send("Entrez le montant à retirer : ".encode())
                            montant = float(client_socket.recv(1024).decode().strip())
                            resultat = banque.retirer(num_compte, montant)
                            client_socket.send(resultat.encode())

                        elif option == "2":  # Dépôt
                            client_socket.send("Entrez le montant à déposer : ".encode())
                            montant = float(client_socket.recv(1024).decode().strip())
                            resultat = banque.deposer(num_compte, montant)
                            client_socket.send(resultat.encode())

                        elif option == "3":  # Consultation solde
                            solde = banque.consulter_solde(num_compte)
                            client_socket.send(f"Votre solde est : {solde}\n".encode())

                        elif option == "4":  # Quitter
                            client_socket.send("Merci d'avoir utilisé la Banque Digitale. À bientôt !\n".encode())
                            break
                        else:
                            client_socket.send("Option invalide.\n".encode())

                else:
                    client_socket.send("Numéro de compte ou mot de passe incorrect.\n".encode())

            elif choix == "2":
                client_socket.send("Inscription\n".encode())
                client_socket.send("Entrez votre nom : ".encode())
                nom = client_socket.recv(1024).decode().strip()

                client_socket.send("Entrez votre prénom : ".encode())
                prenom = client_socket.recv(1024).decode().strip()

                client_socket.send("Entrez votre numéro de téléphone : ".encode())
                telephone = client_socket.recv(1024).decode().strip()

                client_socket.send("Choisissez un mot de passe : ".encode())
                mot_de_passe = client_socket.recv(1024).decode().strip()

                resultat = banque.create_compte(nom, prenom, telephone, mot_de_passe)
                if isinstance(resultat, str):
                    client_socket.send(f"Erreur : {resultat}\n".encode())
                else:
                    client_socket.send(f"Compte créé avec succès. Votre numéro de compte est : {resultat}\n".encode())

            elif choix == "3":
                client_socket.send("Merci d'avoir utilisé la Banque Digitale. À bientôt !\n".encode())
                break
            else:
                client_socket.send("Option invalide.\n".encode())

    except Exception as e:
        client_socket.send(f"Erreur : {e}\n".encode())
    finally:
        client_socket.close()

def run_server():
    banque = BanqueDigitale()  # Crée une instance de la classe BanqueDigitale
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 12345))
    server_socket.listen(5)
    print("Serveur en attente de connexions...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connexion acceptée de {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, banque))
        client_thread.start()

if __name__ == "__main__":
    run_server()
