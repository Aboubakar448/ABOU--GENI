# 📦 Guide d'Installation ABOU GENI v2.0

## 🚀 Déploiement sur Vercel

### 1. Prérequis
- Compte GitHub avec votre projet ABOU GENI
- Compte Vercel connecté à GitHub
- Base de données MongoDB (Atlas recommandé)

### 2. Configuration MongoDB Atlas

1. Créez un cluster sur [MongoDB Atlas](https://cloud.mongodb.com)
2. Créez un utilisateur de base de données
3. Autorisez toutes les IPs (0.0.0.0/0) ou configurez selon vos besoins
4. Récupérez votre connection string

### 3. Variables d'environnement Vercel

Dans votre dashboard Vercel, ajoutez ces variables :

```
MONGO_URL = mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME = abou_geni_production
```

### 4. Structure des fichiers pour Vercel

Assurez-vous que votre projet GitHub contient :

```
/
├── vercel.json                 # Configuration Vercel
├── package.json               # Configuration npm principale
├── README.md                  # Documentation
├── frontend/
│   ├── package.json          # Dépendances React
│   ├── src/
│   │   └── App.js           # Application React
│   └── public/
└── backend/
    ├── server.py             # API FastAPI
    └── requirements.txt      # Dépendances Python
```

### 5. Commandes de build

Vercel exécutera automatiquement :

```bash
# Installation et build du frontend
cd frontend && npm install && npm run build
```

### 6. Configuration du domaine

1. Dans Vercel, allez dans Settings > Domains
2. Ajoutez votre domaine personnalisé si souhaité
3. Mettez à jour `REACT_APP_BACKEND_URL` avec la nouvelle URL

### 7. Test du déploiement

1. Visitez votre URL Vercel
2. Connectez-vous avec admin/admin123
3. Testez les fonctionnalités principales

## 🐛 Résolution des problèmes

### Erreur de build frontend
- Vérifiez que `package.json` est valide (pas de caractères spéciaux)
- Assurez-vous que toutes les dépendances sont listées

### Erreur de connexion backend
- Vérifiez les variables d'environnement Vercel
- Testez la connection MongoDB
- Vérifiez les CORS dans `server.py`

### Erreur 404 API
- Vérifiez que `vercel.json` route correctement `/api/*`
- Assurez-vous que `server.py` utilise le préfixe `/api`

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs Vercel
2. Testez localement d'abord
3. Contactez support@abougeni.org

**Déploiement réussi = Application accessible avec admin/admin123** ✅