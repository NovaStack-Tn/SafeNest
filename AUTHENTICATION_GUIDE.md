# 🔐 Guide d'Authentification - SafeNest

## ❗ Erreur 401 Unauthorized

Si vous voyez l'erreur **401 (Unauthorized)**, cela signifie que vous devez vous **connecter** d'abord.

---

## 🚀 Comment se Connecter

### **Option 1: Via l'Interface Web**

1. **Accédez à la page de login:**
   ```
   http://localhost:5173/login
   ```

2. **Entrez vos identifiants:**
   - Email/Username
   - Password

3. **Le token sera automatiquement sauvegardé** dans `localStorage`

4. **Accédez à la page Visitors:**
   ```
   http://localhost:5173/visitors
   ```

---

### **Option 2: Via API Direct (pour tester)**

Si vous voulez tester sans passer par l'interface:

```bash
# 1. Obtenir un token JWT
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "votre_username",
    "password": "votre_password"
  }'
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**2. Sauvegarder le token dans le navigateur:**
```javascript
// Ouvrez la console du navigateur (F12)
localStorage.setItem('access_token', 'VOTRE_TOKEN_ACCESS_ICI');

// Rafraîchissez la page
location.reload();
```

---

## 🔧 Créer un Utilisateur de Test

Si vous n'avez pas encore d'utilisateur:

```bash
cd backend
python manage.py createsuperuser
```

**Suivez les instructions:**
```
Username: admin
Email: admin@safenest.com
Password: votre_password
Password (again): votre_password
```

**Ensuite connectez-vous avec ces identifiants!**

---

## 📝 Endpoints d'Authentification

### **1. Obtenir un Token**
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOi...",  // Token valide 5 minutes
  "refresh": "eyJ0eXAiOi..."  // Token valide 24 heures
}
```

---

### **2. Rafraîchir un Token**
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "votre_refresh_token"
}
```

**Réponse:**
```json
{
  "access": "nouveau_access_token"
}
```

---

## 🛠️ Utilisation du Token

Une fois connecté, toutes les requêtes doivent inclure le header:

```http
Authorization: Bearer VOTRE_ACCESS_TOKEN
```

**Exemple avec axios:**
```typescript
const token = localStorage.getItem('access_token');

axios.get('http://localhost:8000/api/visitor-assets/visitors/', {
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

---

## ⏰ Durée de Validité

| Type | Durée | Utilisation |
|------|-------|-------------|
| **Access Token** | 5 minutes | Pour toutes les requêtes API |
| **Refresh Token** | 24 heures | Pour obtenir un nouveau access token |

**Quand le token expire:**
- L'API retourne **401 Unauthorized**
- Utilisez le refresh token pour obtenir un nouveau access token
- Ou reconnectez-vous

---

## 🔍 Vérifier si vous êtes Connecté

**Ouvrez la console du navigateur (F12):**
```javascript
// Vérifier le token
const token = localStorage.getItem('access_token');
console.log('Token:', token);

// Vérifier si valide
if (token) {
  console.log('✅ Token présent');
} else {
  console.log('❌ Pas de token - Connectez-vous!');
}
```

---

## 🐛 Résolution des Problèmes

### **Problème: 401 Unauthorized**

**Solutions:**

1. **Vérifiez que vous êtes connecté:**
   ```
   http://localhost:5173/login
   ```

2. **Vérifiez le token dans localStorage:**
   ```javascript
   console.log(localStorage.getItem('access_token'));
   ```

3. **Token expiré? Reconnectez-vous**

4. **Backend ne tourne pas? Démarrez-le:**
   ```bash
   cd backend
   python manage.py runserver
   ```

---

### **Problème: Token existe mais 401 quand même**

**Le token est peut-être expiré:**

1. **Supprimez l'ancien token:**
   ```javascript
   localStorage.removeItem('access_token');
   ```

2. **Reconnectez-vous:**
   ```
   http://localhost:5173/login
   ```

---

### **Problème: Pas de page de login**

**La page de login existe déjà dans votre app!**

```typescript
// frontend/src/pages/Login.tsx
import { Login } from './pages/Login';
```

**Route:**
```
http://localhost:5173/login
```

---

## 📋 Checklist de Démarrage

Avant d'utiliser l'application:

- [ ] Backend démarré: `python manage.py runserver`
- [ ] Frontend démarré: `npm run dev`
- [ ] Utilisateur créé: `python manage.py createsuperuser`
- [ ] Connecté via: `http://localhost:5173/login`
- [ ] Token dans localStorage
- [ ] Accès à `/visitors` sans erreur 401

---

## 🎯 Flux Complet

```
1. Créer un utilisateur
   └─> python manage.py createsuperuser

2. Démarrer le backend
   └─> python manage.py runserver

3. Démarrer le frontend
   └─> npm run dev

4. Se connecter
   └─> http://localhost:5173/login
   └─> Entrer username/password
   └─> Token sauvegardé automatiquement

5. Accéder aux visiteurs
   └─> http://localhost:5173/visitors
   └─> ✅ Pas d'erreur 401!
```

---

## 💡 Astuce pour le Développement

**Pour éviter de se reconnecter à chaque fois:**

Le refresh token dure **24 heures**. Après la première connexion, votre token sera valide toute la journée!

---

## ✅ Résumé

**L'erreur 401 signifie simplement:**
- 🔐 Vous devez vous connecter
- 🔑 Ou votre token a expiré

**Solution:**
1. Allez sur `/login`
2. Connectez-vous
3. Le token sera sauvegardé automatiquement
4. Retournez sur `/visitors`
5. ✨ Ça fonctionne!

---

## 🚀 Commandes Rapides

```bash
# Créer un superuser
cd backend
python manage.py createsuperuser

# Démarrer le backend
python manage.py runserver

# Dans un autre terminal - Démarrer le frontend
cd frontend
npm run dev

# Ouvrir le navigateur
# http://localhost:5173/login
```

**Voilà! Vous êtes prêt à utiliser SafeNest!** 🎉
