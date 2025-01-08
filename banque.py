import os
import hashlib
import random
import re
from datetime import datetime

class BanqueDigitale:
    def __init__(self):
        self.comptes = {}
        self.fichier = 'account.txt'
        self.journal_fichier = 'journal.txt'
        self.charger_comptes()

    def charger_comptes(self):
        """Charge les comptes existants depuis le fichier dans self.comptes."""
        if os.path.exists(self.fichier):
            try:
                with open(self.fichier, 'r') as f:
                    for line in f:
                        num_compte, nom, prenom, telephone, solde, mot_de_passe = line.strip().split(';')
                        self.comptes[num_compte] = {
                            'nom': nom,
                            'prenom': prenom,
                            'telephone': telephone,
                            'solde': float(solde),
                            'mot_de_passe': mot_de_passe
                        }
            except Exception as e:
                print(f"Erreur lors du chargement des comptes : {e}")

    def sauvegarder_comptes(self):
        """Sauvegarde tous les comptes dans le fichier."""
        try:
            with open(self.fichier, 'w') as f:
                for num_compte, infos in self.comptes.items():
                    f.write(f"{num_compte};{infos['nom']};{infos['prenom']};{infos['telephone']};{infos['solde']:.2f};{infos['mot_de_passe']}\n")
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
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        return re.match(pattern, mot_de_passe) is not None

    def create_compte(self, nom, prenom, telephone, mot_de_passe):
        if not self.valider_nom(nom):
            return "Le nom doit contenir au moins 5 caractères."
        if not self.valider_prenom(prenom):
            return "Le prénom doit contenir au moins 3 caractères."
        if not self.valider_telephone(telephone):
            return "Le numéro de téléphone doit commencer par +223 et contenir 8 chiffres."
        if not self.valider_mot_de_passe(mot_de_passe):
            return "Le mot de passe doit contenir au moins 8 caractères, une lettre, un chiffre et un caractère spécial."

        num_compte = self.generate_num_compte()
        mot_de_passe_hash = self.hasher_mot_de_passe(mot_de_passe)
        self.comptes[num_compte] = {
            'nom': nom,
            'prenom': prenom,
            'telephone': telephone,
            'solde': 0.0,
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

    def fermer_compte(self, num_compte):
        compte = self.lire_compte(num_compte)
        if compte:
            compte['solde'] = 0.0
            self.sauvegarder_comptes()
            return compte
        return None

    def supprimer_compte(self, num_compte):
        if num_compte in self.comptes:
            del self.comptes[num_compte]
            self.sauvegarder_comptes()
            return True
        return False

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
                try:
                    num_compte = input("Entrez votre numéro de compte : ")
                    if not num_compte.isdigit():
                        print("Le numéro de compte doit être un entier.")
                        continue
                    mot_de_passe = input("Entrez votre mot de passe : ")
                    if banque.verifier_mot_de_passe(num_compte, mot_de_passe):
                        print("Connexion réussie. Bienvenue !")
                        while True:
                            action = input("Que voulez-vous faire ? (1: Consulter solde, 2: Déposer, 3: Retirer, 4: Déconnexion) : ")
                            if action == "1":
                                if banque.verifier_mot_de_passe(num_compte, input("Confirmez votre mot de passe : ")):
                                    compte = banque.lire_compte(num_compte)
                                    print("Votre solde est de :", compte['solde'])
                                else:
                                    print("Mot de passe incorrect.")
                            elif action == "2":
                                montant = float(input("Entrez le montant à déposer : "))
                                if montant > 0:
                                    compte = banque.update_solde(num_compte, montant)
                                    print("Nouveau solde :", compte['solde'])
                                else:
                                    print("Le montant doit être positif.")
                            elif action == "3":
                                if banque.verifier_mot_de_passe(num_compte, input("Confirmez votre mot de passe : ")):
                                    montant = float(input("Entrez le montant à retirer : "))
                                    compte = banque.update_solde(num_compte, -montant)
                                    print("Nouveau solde :", compte['solde'])
                                else:
                                    print("Mot de passe incorrect.")
                            elif action == "4":
                                print("Déconnexion réussie.")
                                break
                            else:
                                print("Option invalide.")
                    else:
                        print("Numéro de compte ou mot de passe incorrect.")
                except ValueError:
                    print("Entrée invalide.")
            elif choix == "2":
                print("Inscription")
                nom, prenom, telephone, mot_de_passe = "", "", "", ""
                # Validation du nom
                while not banque.valider_nom(nom):
                    nom = input("Entrez votre nom : ")
                    if len(nom) < 5:
                        print("Le nom doit contenir au moins 5 caractères. Veuillez réessayer.")

                # Validation du prénom
                while not banque.valider_prenom(prenom):
                    prenom = input("Entrez votre prénom : ")
                    if len(prenom) < 3:
                        print("Le prénom doit contenir au moins 3 caractères. Veuillez réessayer.")

                # Validation du téléphone
                while not banque.valider_telephone(telephone):
                    telephone = input("Entrez votre numéro de téléphone : ")
                    if not banque.valider_telephone(telephone):
                        print("Le numéro de téléphone doit commencer par +223 et contenir 8 chiffres. Veuillez réessayer.")

                # Validation du mot de passe
                while not banque.valider_mot_de_passe(mot_de_passe):
                    mot_de_passe = input("Choisissez un mot de passe : ")
                    if not banque.valider_mot_de_passe(mot_de_passe):
                        print("Le mot de passe doit contenir au moins 8 caractères, une lettre, un chiffre et un caractère spécial. Veuillez réessayer.")

                # Création du compte
                resultat = banque.create_compte(nom, prenom, telephone, mot_de_passe)
                if isinstance(resultat, str):
                    print(resultat)
                else:
                    print(f"Compte créé avec succès. Votre numéro de compte est : {resultat}")
                    banque.enregistrer_journal(f"Création du compte {resultat} pour {nom} {prenom}")
                    if input("Souhaitez-vous effectuer un dépôt initial ? (oui/non) : ").lower() == "oui":
                        try:
                            montant = float(input("Entrez le montant à déposer : "))
                            if montant > 0:
                                compte = banque.update_solde(resultat, montant)
                                print("Dépôt effectué. Nouveau solde :", compte['solde'])
                            else:
                                print("Le montant doit être positif.")
                        except ValueError:
                            print("Montant invalide.")
            elif choix == "3":
                print("Merci d'avoir utilisé la Banque Digitale. À bientôt !")
                break
            else:
                print("Option invalide.")
        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
