# 🚗 ABOU GENI v2.0 - Gestionnaire de Documents de Véhicules

## 📋 Description

ABOU GENI est une application moderne de gestion de documents de véhicules développée pour l'association ABOU GENI. L'application permet de gérer efficacement les véhicules (camions, bus, mini-bus, camionnettes) et leurs documents associés avec un système d'alertes automatiques.

## ✨ Fonctionnalités

### 🎯 Fonctionnalités Principales
- ✅ **Gestion des véhicules** (camions, bus, mini bus, camionnette)
- ✅ **Suivi des documents** avec dates d'expiration
- ✅ **Alertes automatiques** (30, 15, 7 jours)
- ✅ **Recherche avancée** par véhicule/propriétaire
- ✅ **Export Excel** complet

### 🚀 Fonctionnalités Avancées
- ✅ **Gestion multi-utilisateurs** avec privilèges détaillés
- ✅ **Sauvegarde automatique** (toutes les 6h)
- ✅ **Application mobile** installable (PWA)
- ✅ **Autocomplétion intelligente** sur tous les formulaires
- ✅ **Vue Excel** avec filtres et statistiques

## 🛠️ Technologies

### Backend
- **FastAPI** - Framework Python moderne
- **MongoDB** - Base de données NoSQL
- **JWT** - Authentification sécurisée
- **Motor** - Driver MongoDB asynchrone

### Frontend
- **React 19** - Interface utilisateur moderne
- **Tailwind CSS** - Styling responsive
- **Axios** - Client HTTP
- **React Router** - Navigation

## 🚀 Déploiement

### Application en ligne
- **URL**: https://abou-geni.vercel.app
- **Compte par défaut**: admin / admin123 ⚠️ (à changer en production)

### Variables d'environnement requises
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=abou_geni_db
REACT_APP_BACKEND_URL=https://your-backend-url
```

## 📱 Installation

### Prérequis
- Node.js 18+
- Python 3.9+
- MongoDB

### Installation locale
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend
cd frontend
npm install
npm start
```

## 📞 Support

- **Email**: support@abougeni.org
- **Version**: 2.0.0
- **License**: MIT

---

## 🏗️ Architecture

```
/app/
├── backend/         # API FastAPI
│   ├── server.py    # Application principale
│   └── requirements.txt
├── frontend/        # Interface React
│   ├── src/
│   │   └── App.js   # Application principale
│   └── package.json
├── vercel.json      # Configuration déploiement
└── README.md
```

## 🔐 Sécurité

- Authentification JWT
- Mots de passe hashés avec bcrypt
- CORS configuré
- Routes API protégées

**Développé avec ❤️ par Aboubakar448**