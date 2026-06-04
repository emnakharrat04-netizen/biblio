# 📚 Bibliothèque Intelligente

Application de gestion de bibliothèque développée avec **FastAPI**, **MySQL** et **Tkinter**, intégrant un **catalogue interactif**, un **tableau de bord statistique** et un **assistant IA basé sur Google Gemini**.

---

# 🚀 Fonctionnalités

## 🔐 Authentification

* Inscription sécurisée avec validation des champs
* Connexion avec vérification des identifiants
* Gestion de session utilisateur
* Déconnexion sécurisée

---

## 📖 Catalogue interactif

### Consultation des ouvrages

* Affichage sous forme de cartes visuelles
* Couvertures des livres
* Informations détaillées :

  * Titre
  * Auteur
  * Catégorie
  * Description
  * Disponibilité

### Recherche et filtrage

* Recherche instantanée par titre ou auteur
* Filtrage par catégorie
* Mise à jour dynamique des résultats

### Gestion des emprunts

* Réservation d’un ouvrage
* Emprunt d’un ouvrage
* Mise à jour automatique du stock disponible

---

## 📚 Gestion des livres (Administration)

* Ajout de livres
* Modification des informations
* Suppression de livres
* Gestion des quantités disponibles
* Association d’images de couverture

---

## 📊 Tableau de bord

### KPIs

* Nombre total de livres
* Livres disponibles
* Livres empruntés
* Livres réservés

### Visualisations

* Donut Chart : répartition des statuts
* Histogramme : livres par catégorie
* Histogramme : auteurs les plus représentés

Les graphiques sont générés dynamiquement avec Matplotlib à partir des données de la base MySQL.

---

## 🤖 Assistant IA

Assistant conversationnel intégré utilisant Google Gemini.

Fonctionnalités :

* Questions en langage naturel
* Réponses contextualisées
* Aide à la recherche d’ouvrages
* Suggestions automatiques
* Interface conversationnelle moderne

---

# 🏗️ Architecture du projet

Frontend :

* Tkinter
* PIL (gestion des images)
* Matplotlib
* Requests

Backend :

* FastAPI
* Pydantic
* Uvicorn

Base de données :

* MySQL

IA :

* Google Gemini API

---

# 🔌 API REST

| Méthode | Endpoint               | Description                     |
| ------- | ---------------------- | ------------------------------- |
| GET     | /health                | Vérification de l’état de l’API |
| POST    | /auth/register         | Création d’un compte            |
| POST    | /auth/login            | Connexion                       |
| GET     | /livres                | Liste des livres                |
| GET     | /livres/{id}           | Détails d’un livre              |
| POST    | /livres                | Ajouter un livre                |
| PUT     | /livres/{id}           | Modifier un livre               |
| DELETE  | /livres/{id}           | Supprimer un livre              |
| POST    | /livres/{id}/reserver  | Réserver un livre               |
| POST    | /livres/{id}/emprunter | Emprunter un livre              |
| GET     | /stats                 | Statistiques globales           |
| POST    | /chat                  | Assistant IA                    |

Documentation Swagger :

http://localhost:8000/docs

---

# ▶️ Lancement du projet

## Backend

```bash
cd backend
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
python app.py
```

---

# 🛠️ Technologies utilisées

* Python 3
* FastAPI
* MySQL
* Tkinter
* Pillow
* Matplotlib
* Requests
* Google Gemini API

---

# 📈 Évolutions futures

* Historique des emprunts
* Gestion des utilisateurs et rôles
* Notifications automatiques
* Recommandations intelligentes de lecture
* Export PDF des statistiques
* Déploiement web complet

---

# 👩‍💻 Réalisé par

Emna Kharrat

Projet universitaire de gestion de bibliothèque intelligente.
