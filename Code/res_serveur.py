import socket
import threading
import logging
from Salle_Reservation import SalleReservation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Instance unique de la classe SalleReservation
reservation = SalleReservation()


class ServerRes:
    def handle_client(client_socket):
        """Gère l'interaction avec un client."""
        try:
            client_socket.send(
                "Bienvenue Professeur sur le service de réservation de l'ITMA\n".encode()
            )
            utilisateur_authentifie = None

            while True:
                if not utilisateur_authentifie:
                    client_socket.send(
                        "Que voulez-vous faire ? \n"
                        "1: Se connecter \n"
                        "2: S'inscrire \n"
                        "3: Quitter : \n"
                        "Entrez le numéro de votre action : ".encode()
                    )
                    choix = client_socket.recv(4096).decode().strip()

                    if choix == "1":
                        client_socket.send("Entrez votre nom d'utilisateur : ".encode())
                        nom = client_socket.recv(4096).decode().strip()

                        client_socket.send("Entrez votre mot de passe : ".encode())
                        motdepasse = client_socket.recv(4096).decode().strip()

                        result = reservation.authentification(nom, motdepasse)
                        if result["status"] == "success":
                            utilisateur_authentifie = nom
                            client_socket.send(
                                f"Connexion réussie. Bienvenue {nom} !\n".encode()
                            )
                        else:
                            client_socket.send(
                                "Nom d'utilisateur ou mot de passe incorrect.\n".encode()
                            )

                    elif choix == "2":
                        client_socket.send("Entrez votre nom d'utilisateur : ".encode())
                        nom = client_socket.recv(4096).decode().strip()

                        client_socket.send("Entrez votre numéro de téléphone : ".encode())
                        telephone = client_socket.recv(4096).decode().strip()

                        client_socket.send("Choisissez un mot de passe : ".encode())
                        motdepasse = client_socket.recv(4096).decode().strip()

                        result = reservation.inscription(nom, telephone, motdepasse)
                        client_socket.send(f"{result['message']}\n".encode())

                    elif choix == "3":
                        client_socket.send(
                            "Merci d'avoir utilisé le système de réservation. Au revoir !\n".encode()
                        )
                        break
                    else:
                        client_socket.send("Option invalide.\n".encode())
                else:
                    client_socket.send(
                        "Que voulez-vous faire ?\n"
                        "1. Réserver une salle\n"
                        "2. Consulter mes réservations\n"
                        "3. Voir les salles libres\n"
                        "4. Annuler une réservation\n"
                        "5. Changer mot de passe\n"
                        "6. Se déconnecter\n"
                        "Choisissez une option : ".encode()
                    )
                    action = client_socket.recv(4096).decode().strip()

                    if action == "1":
                        try:
                            client_socket.send(
                                "Quel salle voulez-vous réserver :\n"
                                "1. Salle informatique du premier étage\n"
                                "2. Salle Billgate\n"
                                "3. Bibliothèque Ginette Bellegarde\n"
                                "4. Salle Informatique Etage 2\n"
                                "Entrez l'index de la salle à réserver : ".encode()
                            )
                            salle_index = int(client_socket.recv(4096).decode().strip()) - 1

                            if salle_index < 0 or salle_index >= len(reservation.salles):
                                client_socket.send("Index de salle invalide.\n".encode())
                                continue

                            client_socket.send(
                                "Entrez la date de début (YYYY-MM-DD HH:MM) : ".encode()
                            )
                            debut = client_socket.recv(4096).decode().strip()

                            client_socket.send(
                                "Entrez la date de fin (YYYY-MM-DD HH:MM) : ".encode()
                            )
                            fin = client_socket.recv(4096).decode().strip()

                            reservation.reserver(utilisateur_authentifie, salle_index, debut, fin)
                        except ValueError:
                            client_socket.send(
                                "Entrée invalide. Assurez-vous de fournir des données correctes.\n".encode()
                            )

                    elif action == "2":
                        reservations = reservation.consulter(utilisateur_authentifie)
                        client_socket.send(f"Vos réservations : {reservations}\n".encode())

                    elif action == "3":
                        salles_libres = reservation.voir_liberte()
                        client_socket.send(
                            f"Salles disponibles : {salles_libres}\n".encode()
                        )

                    elif action == "4":
                        try:
                            reservations = reservation.consulter(
                                utilisateur_authentifie
                            ).split("\n")
                            if not reservations or reservations == [
                                "Aucune réservation trouvée."
                            ]:
                                client_socket.send(
                                    "Aucune réservation à annuler.\n".encode()
                                )
                                continue

                            client_socket.send(
                                f"Vos réservations :\n{reservations}\n"
                                "Entrez l'index de la réservation à annuler : ".encode()
                            )
                            index = int(client_socket.recv(4096).decode().strip()) - 1

                            result = reservation.annuler_reservation(utilisateur_authentifie, index)
                            client_socket.send(f"{result['message']}\n".encode())
                            
                            client_socket.send(f"{result['message']}\n".encode())
                        except ValueError:
                            client_socket.send(
                                "Index invalide. Veuillez réessayer.\n".encode()
                            )
                    
                    elif action == "5":
                        client_socket.send("Entrez votre mot de passe actuel : ".encode())
                        ancien_mdp = client_socket.recv(4096).decode().strip()

                        client_socket.send("Entrez le nouveau mot de passe : ".encode())
                        nouveau_mdp = client_socket.recv(4096).decode().strip()

                        result = reservation.modifier_mot_de_passe(utilisateur_authentifie, ancien_mdp, nouveau_mdp)
                        client_socket.send(f"{result['message']}\n".encode())

                    elif action == "6":
                        client_socket.send(
                            "Déconnexion réussie. Au revoir !\n".encode()
                        )
                        utilisateur_authentifie = None
                        

                    else:
                        client_socket.send("Option invalide.\n".encode())
        except Exception as e:
            logging.error(f"Erreur dans la gestion du client : {e}")
            client_socket.send(f"Erreur : {e}\n".encode())
        finally:
            client_socket.close()

    def run_server():
        """Démarre le serveur de réservation."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("127.0.0.1", 1235))
        server_socket.listen(5)
        logging.info("Serveur en attente de connexions...")

        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connexion acceptée de {addr}")
            client_thread = threading.Thread(
                target=ServerRes.handle_client, args=(client_socket,)
            )
            client_thread.start()


if __name__ == "__main__":
    ServerRes.run_server()