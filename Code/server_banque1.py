import socket
import threading
from banque import BanqueDigitale  # Importation du module banque.py

class BanqueServer:
    @staticmethod
    def occuper_client(client_socket, banque):
        try:
            client_socket.send("Bienvenue dans la Banque Digitale\n".encode())
            while True:
                client_socket.send("Que voulez-vous faire ? (1: Se connecter, 2: S'inscrire, 3: Quitter) : ".encode())
                choix = client_socket.recv(1024).decode().strip()

                if choix == "1":  # Connexion
                    client_socket.send("Entrez votre numéro de compte : ".encode())
                    num_compte = client_socket.recv(1024).decode().strip()

                    client_socket.send("Entrez votre mot de passe : ".encode())
                    mot_de_passe = client_socket.recv(1024).decode().strip()

                    if banque.verifier_mot_de_passe(num_compte, mot_de_passe):
                        client_socket.send("Connexion réussie. Bienvenue !\n".encode())

                        # Menu des transactions après connexion
                        while True:
                            client_socket.send(
                                "Que voulez-vous faire ? (1: Retrait, 2: Dépôt, 3: Consultation solde, "
                                "4: Changer code PIN, 5: Quitter) : ".encode()
                            )
                            option = client_socket.recv(1024).decode().strip()

                            if option == "1":  # Retrait
                                client_socket.send("Entrez le montant à retirer : ".encode())
                                montant = float(client_socket.recv(1024).decode().strip())
                                compte = banque.lire_compte(num_compte)
                                if compte and compte['solde'] >= montant:
                                    banque.update_solde(num_compte, -montant)
                                    client_socket.send("Retrait effectué avec succès.\n".encode())
                                    banque.enregistrer_journal(f"Retrait de {montant:.2f} FCFA du compte {num_compte}")
                                else:
                                    client_socket.send("Solde insuffisant ou compte introuvable.\n".encode())

                            elif option == "2":  # Dépôt
                                client_socket.send("Entrez le montant à déposer : ".encode())
                                montant = float(client_socket.recv(1024).decode().strip())
                                banque.update_solde(num_compte, montant)
                                client_socket.send("Dépôt effectué avec succès.\n".encode())
                                banque.enregistrer_journal(f"Dépôt de {montant:.2f} FCFA sur le compte {num_compte}")

                            elif option == "3":  # Consultation solde
                                compte = banque.lire_compte(num_compte)
                                if compte:
                                    solde = compte['solde']
                                    client_socket.send(f"Votre solde est : {solde:.2f} F CFA\n".encode())
                                else:
                                    client_socket.send("Compte introuvable.\n".encode())

                            elif option == "4":  # Changer code PIN
                                client_socket.send("Entrez votre ancien mot de passe : ".encode())
                                ancien_mot_de_passe = client_socket.recv(1024).decode().strip()

                                if banque.verifier_mot_de_passe(num_compte, ancien_mot_de_passe):
                                    client_socket.send("Entrez votre nouveau mot de passe : ".encode())
                                    nouveau_mot_de_passe = client_socket.recv(1024).decode().strip()

                                    banque.changer_mot_de_passe(num_compte, nouveau_mot_de_passe)
                                    client_socket.send("Votre mot de passe a été changé avec succès.\n".encode())
                                    banque.enregistrer_journal(f"Changement de mot de passe pour le compte {num_compte}")
                                else:
                                    client_socket.send("L'ancien mot de passe est incorrect.\n".encode())

                            elif option == "5":  # Quitter
                                client_socket.send("Merci d'avoir utilisé la Banque Digitale. À bientôt !\n".encode())
                                break

                            else:
                                client_socket.send("Option invalide.\n".encode())

                    else:
                        client_socket.send("Numéro de compte ou mot de passe incorrect.\n".encode())

                elif choix == "2":  # Inscription
                    client_socket.send("Inscription\n".encode())
                    client_socket.send("Entrez votre nom : ".encode())
                    nom = client_socket.recv(1024).decode().strip()

                    client_socket.send("Entrez votre prénom : ".encode())
                    prenom = client_socket.recv(1024).decode().strip()

                    client_socket.send("Entrez votre numéro de téléphone (+223xxxxxxxx) : ".encode())
                    telephone = client_socket.recv(1024).decode().strip()

                    client_socket.send("Choisissez un mot de passe : ".encode())
                    mot_de_passe = client_socket.recv(1024).decode().strip()

                    client_socket.send("Type de compte (courant/epargne) : ".encode())
                    type_compte = client_socket.recv(1024).decode().strip().lower()

                    depot_initial = 0
                    if type_compte == "epargne":
                        client_socket.send("Entrez le dépôt initial (minimum 5000) : ".encode())
                        depot_initial = float(client_socket.recv(1024).decode().strip())

                    resultat = banque.create_compte(nom, prenom, telephone, mot_de_passe, type_compte, depot_initial)
                    if isinstance(resultat, str) and resultat.startswith("Erreur"):
                        client_socket.send(f"Erreur : {resultat}\n".encode())
                    else:
                        client_socket.send(
                            f"Compte créé avec succès. Votre numéro de compte est : {resultat}\n".encode()
                        )

                elif choix == "3":  # Quitter
                    client_socket.send("Merci d'avoir utilisé la Banque Digitale. À bientôt !\n".encode())
                    break

                else:
                    client_socket.send("Option invalide.\n".encode())

        except Exception as e:
            client_socket.send(f"Erreur : {e}\n".encode())
        finally:
            client_socket.close()

    @staticmethod
    def run_server():
        banque = BanqueDigitale()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("127.0.0.1", 12345))
        server_socket.listen(5)
        print("Serveur en attente de connexions...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connexion acceptée de {addr}")
            client_thread = threading.Thread(target=BanqueServer.occuper_client, args=(client_socket, banque))
            client_thread.start()

if __name__ == "__main__":
    BanqueServer.run_server()
