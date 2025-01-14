import os
import hashlib
import random
import re
from datetime import datetime

class BanqueDigitale:
    def __init__(self):
        self.comptes = {}
        self.fichier = 'client.txt'
        self.journal_fichier = 'journal.txt'
        self.charger_comptes()

    def charger_comptes(self):
        """Charge les comptes existants depuis le fichier dans self.comptes."""
        if os.path.exists(self.fichier):
            try:
                with open(self.fichier, 'r') as f:
                    for line in f:
                        num_compte, nom, prenom, telephone, solde, mot_de_passe, type_compte = line.strip().split(';')
                        self.comptes[num_compte] = {
                            'nom': nom,
                            'prenom': prenom,
                            'telephone': telephone,
                            'solde': float(solde),
                            'mot_de_passe': mot_de_passe,
                            'type_compte': type_compte
                        }
            except Exception as e:
                print(f"Erreur lors du chargement des comptes : {e}")

    def sauvegarder_comptes(self):
        """Sauvegarde tous les comptes dans le fichier."""
        try:
            with open(self.fichier, 'w') as f:
                for num_compte, infos in self.comptes.items():
                    f.write(f"{num_compte};{infos['nom']};{infos['prenom']};{infos['telephone']};"
                            f"{infos['solde']:.2f};{infos['mot_de_passe']};{infos['type_compte']}\n")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des comptes : {e}")

    def generate_num_compte(self):
        """Génère un numéro de compte unique de 6 chiffres."""
        while True:
            num_compte = str(random.randint(100000, 999999))
            if num_compte not in self.comptes:
                return num_compte

    def hasher_mot_de_passe(self, mot_de_passe):
        """Hash un mot de passe avec SHA-256."""
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()

    def valider_nom(self, valeur):
        return len(valeur) >= 5

    def valider_prenom(self, valeur):
        return len(valeur) >= 3

    def valider_telephone(self, telephone):
        pattern = r"^\+223[0-9]{8}$"
        return re.match(pattern, telephone) is not None

    def valider_mot_de_passe(self, mot_de_passe):
        pattern = r"^\d{4}$"
        return re.match(pattern, mot_de_passe) is not None

    def create_compte(self, nom, prenom, telephone, mot_de_passe, type_compte, depot_initial=0):
        if not self.valider_nom(nom):
            return "Le nom doit contenir au moins 5 caractères."
        if not self.valider_prenom(prenom):
            return "Le prénom doit contenir au moins 3 caractères."
        if not self.valider_telephone(telephone):
            return "Le numéro de téléphone doit commencer par +223 et contenir 8 chiffres."
        if not self.valider_mot_de_passe(mot_de_passe):
            return "Le mot de passe doit contenir au moins 8 caractères, une lettre, un chiffre et un caractère spécial."

        if type_compte == "epargne" and depot_initial < 5000:
            return "Un dépôt initial minimum de 5000 est requis pour un compte épargne."

        num_compte = self.generate_num_compte()
        mot_de_passe_hash = self.hasher_mot_de_passe(mot_de_passe)
        self.comptes[num_compte] = {
            'nom': nom,
            'prenom': prenom,
            'telephone': telephone,
            'solde': depot_initial,
            'type_compte': type_compte,
            'mot_de_passe': mot_de_passe_hash
        }
        self.sauvegarder_comptes()
        return num_compte

    def verifier_mot_de_passe(self, num_compte, mot_de_passe):
        compte = self.lire_compte(num_compte)
        if compte:
            return compte['mot_de_passe'] == self.hasher_mot_de_passe(mot_de_passe)
        return False

    def lire_compte(self, num_compte):
        return self.comptes.get(num_compte, None)

    def update_solde(self, num_compte, montant):
        compte = self.lire_compte(num_compte)
        if compte:
            compte['solde'] += montant
            self.sauvegarder_comptes()
            return compte
        return None

    def enregistrer_journal(self, message):
        """Enregistre un message dans le fichier journal."""
        try:
            with open(self.journal_fichier, 'a') as f:
                f.write(f"{datetime.now()} - {message}\n")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans le journal : {e}")

def main():
    banque = BanqueDigitale()

    print("Bienvenue dans la Banque Digitale")
    while True:
        try:
            choix = input("Que voulez-vous faire ? (1: Se connecter, 2: S'inscrire, 3: Quitter) : ")
            if choix == "1":
                num_compte = input("Entrez votre numéro de compte : ")
                mot_de_passe = input("Entrez votre mot de passe : ")
                if banque.verifier_mot_de_passe(num_compte, mot_de_passe):
                    print("Connexion réussie.")
                else:
                    print("Numéro de compte ou mot de passe incorrect.")
            elif choix == "2":
                nom = input("Entrez votre nom : ")
                prenom = input("Entrez votre prénom : ")
                telephone = input("Entrez votre numéro de téléphone (+223xxxxxxxx) : ")
                mot_de_passe = input("Choisissez un mot de passe : ")
                type_compte = input("Type de compte (courant/epargne) : ").lower()
                depot_initial = 0
                if type_compte == "epargne":
                    depot_initial = float(input("Entrez le dépôt initial (minimum 5000) : "))

                resultat = banque.create_compte(nom, prenom, telephone, mot_de_passe, type_compte, depot_initial)
                print(resultat if isinstance(resultat, str) else f"Compte créé avec succès : {resultat}")
            elif choix == "3":
                print("Merci d'avoir utilisé la Banque Digitale.")
                break
            else:
                print("Option invalide.")
        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()

