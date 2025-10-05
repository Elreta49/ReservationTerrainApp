# 📋 Application de Réservation - Arrondissement

Cette application permet de gérer les réservations des terrains et salles d'une arrondissement.  
Elle propose une interface moderne, sécurisée par une page de connexion, et de nombreuses fonctionnalités pratiques.

---

## 🚀 Fonctionnalités principales

- **Connexion sécurisée** (login requis)
- **Ajout, modification, suppression** de réservations
- **Recherche instantanée** par nom
- **Calcul automatique de la durée** et du montant
- **Gestion des états de paiement** (Payé / Non payé)
- **Aperçu et impression** de reçus PDF
- **Exportation automatique** des données dans un fichier CSV
- **Affichage du total encaissé** (Payé)
- **Interface moderne** (Tkinter, design responsive)

---

## 🖥️ Installation & Lancement

### 1. **Prérequis**

- Python 3.8 ou plus récent
- Modules Python nécessaires :  
  `tkinter`, `tkcalendar`, `fpdf`, `pywin32`

Installe-les avec :
```sh
pip install tkcalendar fpdf pywin32
```

### 2. **Lancer l’application**

Dans le dossier du projet, exécute :
```sh
python app.py
```

### 3. **Créer un exécutable (.exe) (optionnel)**

Avec [PyInstaller](https://pyinstaller.org/) :
```sh
pip install pyinstaller
pyinstaller --onefile --noconsole app.py
```
Le fichier `.exe` sera dans le dossier `dist`.

---

## 🔑 Connexion

- **Nom d’utilisateur** : `admin`
- **Mot de passe** : `admin123`

---

## 📁 Fichiers importants

- `app.py` : Code principal de l’application
- `reservations.csv` : Base de données des réservations (créée automatiquement)
- Les reçus PDF sont générés à la demande

---

## ✨ Auteurs & Remerciements

Développé pour une arrondissement  
Design & code : [Hamdi Imrane]

---

## 🛠️ Personnalisation

- Pour changer les identifiants de connexion, modifiez la fonction `show_login_inplace` dans `app.py`.
- Pour ajouter des terrains ou salles, modifiez la liste `terrains` dans `app.py`.

---

## 📞 Support

Pour toute question ou bug, contactez : *0103.ihamdi@gmail.com*

---
