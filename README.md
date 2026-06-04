# 📚 Bibliothèque Intelligente

Application de gestion de bibliothèque avec interface graphique Tkinter, backend FastAPI, base de données MySQL et chatbot IA propulsé par Google Gemini.

---

## 🗂️ Structure du projet

```
bibliotheque/
│
├── schema.sql                   ← Base de données MySQL (tables + 10 livres de démo)
│
├── backend/
│   ├── main.py                  ← Point d'entrée FastAPI, routes CRUD + stats
│   ├── database.py              ← Pool de connexions MySQL, helpers fetchall/execute
│   ├── auth.py                  ← Router /auth/register  /auth/login  (bcrypt)
│   ├── chatbot.py               ← Router /chat  →  contexte DB + Gemini
│   ├── models.py                ← Schémas Pydantic (validation entrées/sorties)
│   ├── requirements.txt         ← Dépendances backend
│   └── uploads/                 ← Dossier pour les images de couverture uploadées
│
├── frontend/
│   ├── app.py                   ← Shell principal : barre de navigation + pages
│   ├── login.py                 ← Écran de connexion
│   ├── signup.py                ← Écran d'inscription
│   ├── dashboard.py             ← Tableau de bord (KPIs + 3 graphiques Matplotlib)
│   ├── books.py                 ← Gestion des livres (tableau + dialog ajout/édition)
│   ├── chatbot_ui.py            ← Fenêtre chatbot IA (bulles, typing, suggestions)
│   └── assets/                  ← Icônes et images locales (optionnel)
│
├── requirements.txt             ← Toutes les dépendances (backend + frontend)
├── start.sh                     ← Lanceur Linux / macOS
├── start.bat                    ← Lanceur Windows
└── README.md
```

---

## ⚡ Installation rapide

### Prérequis
- Python 3.10 ou supérieur
- MySQL 8.0+ (ou MariaDB 10.6+) avec phpMyAdmin ou accès CLI
- Une clé API Google Gemini (gratuite sur https://aistudio.google.com/)

### 1. Base de données

Importez le schéma dans phpMyAdmin, ou via le terminal :

```bash
mysql -u root -p < schema.sql
```

Cela crée la base `bibliotheque` avec les tables `utilisateurs` et `livres`, et insère 10 livres de démonstration.

### 2. Dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configuration

Éditez les variables au début de `start.sh` (Linux/macOS) ou `start.bat` (Windows) :

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=bibliotheque
GEMINI_API_KEY=AIza...          # https://aistudio.google.com/
```

Ou exportez-les directement :

```bash
export GEMINI_API_KEY="AIza..."
export DB_PASSWORD="motdepasse"
```

### 4. Lancer l'application

**Linux / macOS :**
```bash
chmod +x start.sh
./start.sh
```

**Windows :**
Double-cliquez sur `start.bat`  
ou dans un terminal PowerShell :
```powershell
.\start.bat
```

**Manuellement (deux terminaux) :**
```bash
# Terminal 1 – Backend
cd backend
python main.py

# Terminal 2 – Frontend
cd frontend
python app.py
```

---

## 🖥️ Fonctionnalités détaillées

### 🔐 Authentification
| Fonctionnalité | Description |
|---|---|
| Inscription | Formulaire nom / e-mail / mot de passe × 2, validation complète |
| Connexion | Vérification bcrypt, messages d'erreur précis |
| Session | Données utilisateur transmises à toute l'application |
| Déconnexion | Confirmation puis retour à l'écran de connexion |

### 📚 Gestion des livres
| Fonctionnalité | Description |
|---|---|
| Tableau | Colonnes triables, alternance de lignes, scroll infini |
| Recherche | Instantanée sur titre, auteur et ID |
| Filtres | Pills : Tous / Disponible / Emprunté / Réservé |
| Ajout | Dialog modal avec validation de tous les champs |
| Modification | Préremplissage du formulaire, mise à jour en base |
| Suppression | Confirmation obligatoire avant suppression |

### 📊 Tableau de bord
| Graphique | Type | Données |
|---|---|---|
| KPI cards | Chiffres colorés | Total, disponibles, empruntés, réservés |
| Statuts | Donut chart | Répartition en % des 3 statuts |
| Catégories | Barres horizontales | Nombre de livres par catégorie |
| Top auteurs | Barres horizontales | Top 8 auteurs par nombre de livres |

### 🤖 Chatbot IA
| Fonctionnalité | Description |
|---|---|
| Langage naturel | Questions libres en français |
| Contexte réel | Tous les livres de la DB injectés dans le prompt |
| Suggestions | Chips de raccourcis cliquables |
| Indicateur | Animation "● ● ●" pendant le chargement |
| Historique | Bulles horodatées, effaçables |

---

## 🔌 Référence API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | État de l'API et de la base |
| `POST` | `/auth/register` | Créer un compte |
| `POST` | `/auth/login` | Se connecter |
| `GET` | `/livres` | Lister (+ `?search=`) |
| `GET` | `/livres/{id}` | Détails d'un livre |
| `POST` | `/livres` | Ajouter |
| `PUT` | `/livres/{id}` | Modifier |
| `DELETE` | `/livres/{id}` | Supprimer |
| `GET` | `/stats` | Statistiques globales |
| `POST` | `/chat` | Chatbot Gemini |

Documentation interactive : **http://localhost:8000/docs**

---

## 🎨 Design

Thème **Dark Luxury** :
- Fond noir profond `#0D0F14` + surfaces élevées `#13161E`
- Accents dorés `#C9A84C` (titres, bordures actives, boutons CTA)
- Vert / orange / bleu pour les statuts de livres
- Violet `#8B5CF6` pour le chatbot
- Notifications toast animées (fade-in / fade-out)
- Indicateur de frappe du chatbot animé image par image

---

## 🛠️ Dépannage

| Problème | Solution |
|---|---|
| `Connection refused` au démarrage | Vérifiez que `python main.py` tourne sur le port 8000 |
| `Access denied` MySQL | Vérifiez `DB_USER` / `DB_PASSWORD` dans les variables d'env |
| `Erreur Gemini 503` | Vérifiez `GEMINI_API_KEY` — obtenez-en une sur aistudio.google.com |
| `ModuleNotFoundError` | Relancez `pip install -r requirements.txt` |
| Fenêtre Tkinter trop petite | Ajoutez `self.geometry("1400x900")` dans `app.py` si `zoomed` ne fonctionne pas |
