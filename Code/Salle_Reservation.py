import threading
from datetime import datetime
from datetime import timedelta
import os

class SalleReservation:
    def __init__(self):
        self.salles = [
            {"nom": "Salle informatique du premier étage", "reservations": [], "lock": threading.Lock()},
            {"nom": "Salle Billgate", "reservations": [], "lock": threading.Lock()},
            {"nom": "Bibliothèque Ginette Bellegarde", "reservations": [], "lock": threading.Lock()},
            {"nom": "Salle Informatique Etage 2", "reservations": [], "lock": threading.Lock()},
        ]
        self.utilisateurs = {}
        self.fichier = "sauvegarde.txt" 

    def authentification(self, nom, motdepasse):
        self.charger_sauvegarde()
        if nom in self.utilisateurs and self.utilisateurs[nom][0] == motdepasse:
            return {"status": "success", "message": f"Bienvenue {nom}"}
        else:
            return {"status": "echec", "message": "Nom ou mot de passe incorrect"}

    def inscription(self, nom, telephone, motdepasse):
        if len(telephone) < 8 or not telephone.isdigit():
            return {"status": "failure", "message": "Le numéro de téléphone doit contenir 8 chiffres"}
        self.utilisateurs[nom] = [motdepasse, telephone]
        self.sauvegarde()
        return {"status": "success", "message": f"Votre inscription a bien été faite !"}

    def reserver(self, utilisateur, salle_index, debut, fin):
        try:
            horaire1 = datetime.strptime(debut, "%Y-%m-%d %H:%M")
            horaire2 = datetime.strptime(fin, "%Y-%m-%d %H:%M")
            date_actuelle=datetime.now()
            
            if horaire1<date_actuelle and horaire2<date_actuelle:
                return {"status": "failure", "message": "La date de début est déjà dépassée."}
            
            elif horaire2<horaire1:
                return {"status": "failure", "message": "La date de fin doit être après la date de début."}
            elif(horaire2-horaire1) > timedelta(24) :
                return {"status": "failure", "message": "La réservation ne peut pas dépasser 24 heures."}

            with self.salles[salle_index]["lock"]:
                if self.disponibilite(self.salles[salle_index], horaire1, horaire2):
                    self.salles[salle_index]["reservations"].append({"utilisateur": utilisateur, "debut": horaire1, "fin": horaire2})
                    self.sauvegarde()
                    return {"status": "success", "message": f"Réservation confirmée pour {utilisateur} dans {self.salles[salle_index]['nom']}"}
                else:
                    return {"status": "failure", "message": f"La salle {self.salles[salle_index]['nom']} est déjà réservée pour cette plage horaire."}
        except ValueError:
            return {"status": "error", "message": "Format de date/heure invalide."}

    def annuler_reservation(self, utilisateur, index):
        for salle in self.salles:
            for idx, res in enumerate(salle["reservations"]):
                if res["utilisateur"] == utilisateur and idx == index:
                    salle["reservations"].pop(idx)
                    self.sauvegarde()
                    return {"status": "success", "message": "Réservation annulée avec succès."}
        return {"status": "failure", "message": "Réservation non trouvée ou index invalide."}

    
    def modifier_mot_de_passe(self, utilisateur, ancien_mdp, nouveau_mdp):
        if utilisateur in self.utilisateurs and self.utilisateurs[utilisateur][0] == ancien_mdp:
            self.utilisateurs[utilisateur][0] = nouveau_mdp
            self.sauvegarde()
            return {"status": "success", "message": "Votre mot de passe a été modifié avec succès."}
        else:
            return {"status": "failure", "message": "Ancien mot de passe incorrect ou utilisateur introuvable."}


    
    def consulter(self, utilisateur):
        reservations = []
        for salle in self.salles:
            for res in salle["reservations"]:
                if res["utilisateur"] == utilisateur:
                    reservations.append(f"Salle: {salle['nom']} - De {res['debut']} à {res['fin']}")
        return "\n".join(reservations) if reservations else "Aucune réservation trouvée."

    def voir_liberte(self):
        disponibilites = []
        for salle in self.salles:
            if not salle["reservations"]:
                disponibilites.append(f"{salle['nom']} - Aucune réservation, salle libre.")
            else:
                plages = [
                    f"De {res['debut']} à {res['fin']} par {res['utilisateur']}"
                    for res in salle["reservations"]
                ]
                disponibilites.append(f"{salle['nom']} - Réservations : {', '.join(plages)}")
        return "\n".join(disponibilites)


    def disponibilite(self, salle, horaire1, horaire2):
        for reservation in salle["reservations"]:
            if horaire1 < reservation["fin"] and horaire2 > reservation["debut"]:
                return False
        return True

    def sauvegarde(self):
        try:
            with open(self.fichier, 'w') as f:
                # Sauvegarde des utilisateurs
                f.write("Utilisateurs:\n")
                for nom, (motdepasse, telephone) in self.utilisateurs.items():
                    f.write(f"{nom};{motdepasse};{telephone}\n")
            
                # Sauvegarde des réservations
                f.write("\nRéservations:\n")
                for salle in self.salles:
                    f.write(f"{salle['nom']}:\n")
                    for res in salle["reservations"]:
                        utilisateur = res["utilisateur"]
                        debut = res["debut"].strftime("%Y-%m-%d %H:%M")
                        fin = res["fin"].strftime("%Y-%m-%d %H:%M")
                        f.write(f"    {utilisateur}, De {debut} à {fin}\n")
            print("Sauvegarde effectuée avec succès.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")


    def charger_sauvegarde(self):
        if not os.path.exists(self.fichier):
            print("Aucun fichier de sauvegarde trouvé.")
            return

        try:
            with open(self.fichier, 'r') as f:
                section = None
                salle = None
                for line in f:
                    line = line.strip()

                    if line == "Utilisateurs:":
                        section = "utilisateurs"
                    elif line == "Réservations:":
                        section = "reservations"
                    elif section == "utilisateurs" and ";" in line:
                        # Chargement des utilisateurs
                        nom, motdepasse, telephone = line.split(";")
                        self.utilisateurs[nom] = [motdepasse, telephone]
                    elif section == "reservations" and ":" in line:
                        # Identifier la salle pour les réservations
                        salle_nom = line[:-1]
                        salle = next((s for s in self.salles if s["nom"] == salle_nom), None)
                    elif section == "reservations" and ";" in line:
                        # Charger les réservations pour une salle
                        utilisateur, debut, fin = line.split(";")
                        debut = datetime.strptime(debut, "%Y-%m-%d %H:%M")
                        fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")
                        if salle:
                            salle["reservations"].append({"utilisateur": utilisateur, "debut": debut, "fin": fin})

            print("Chargement effectué avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

            try:
                with open(self.fichier, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if ';' in line:
                            id, nom, telephone, motdepasse = line.strip().split(';')
                            self.utilisateurs[id] = [nom, motdepasse, telephone]
            except Exception as e:
                print(f"Erreur lors du chargement : {e}")
reservation = SalleReservation()

# Simulation des threads
Prof1 = threading.Thread(target=lambda: print(reservation.reserver("Adijetou", 1, "2025-01-14 14:30", "2025-01-14 15:30")))
Prof2 = threading.Thread(target=lambda: print(reservation.reserver("Abdoul", 1, "2025-01-14 14:30", "2025-01-14 16:30")))

Prof1.start()
Prof2.start()

Prof1.join()
Prof2.join()

print("\nDisponibilités des salles :")
print(reservation.voir_liberte())