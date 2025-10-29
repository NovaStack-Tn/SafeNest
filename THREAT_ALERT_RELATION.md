# 🔗 Relation Threat ↔ Alert - Documentation Complète

## ✅ Implémentation Terminée

La relation entre **Threats (Menaces)** et **Alerts (Alertes)** a été complètement intégrée dans le frontend de SafeNest.

---

## 📊 Architecture de la Relation

### Modèle de Données (Backend)

```python
# models.py
class Alert(models.Model):
    # ... autres champs ...
    
    # 🔗 Relation avec Threat (One-to-Many, Optionnelle)
    threat = models.ForeignKey(
        Threat, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alerts'  # threat.alerts.all()
    )
```

**Type:** ForeignKey optionnelle  
**Relation:** Une Threat → Plusieurs Alerts  
**Inverse:** `threat.alerts.all()` retourne toutes les alertes liées  
**Cascade:** SET_NULL (si le Threat est supprimé, l'Alert garde null)

---

## 🎨 Frontend - Nouvelles Fonctionnalités

### 1. ✅ **CreateAlertModal.tsx** - Lier une Alerte à une Menace

**Nouveau champ ajouté:**
```typescript
{/* Related Threat */}
<select value={formData.threat}>
  <option value="">No related threat</option>
  {threats?.map(threat => (
    <option value={threat.id}>
      {threat.title} ({threat.severity} - {threat.status})
    </option>
  ))}
</select>
```

**Fonctionnalités:**
- ✅ Dropdown de sélection de menace (optionnel)
- ✅ Affiche titre, sévérité et statut de chaque menace
- ✅ Icône Link2 pour identifier visuellement le lien
- ✅ Description explicative "Link this alert to an existing threat for correlation"
- ✅ Query automatique des menaces disponibles

**Interface:**
```
┌─────────────────────────────────────────┐
│ Create New Alert                    ✕   │
├─────────────────────────────────────────┤
│ Title *                                 │
│ [Failed login attempt              ]   │
│                                         │
│ Description *                           │
│ [Multiple failed logins...         ]   │
│                                         │
│ Alert Type    │  Severity              │
│ [Intrusion  ▼] │ [High     ▼]         │
│                                         │
│ Source                                  │
│ [IDS System                        ]   │
│                                         │
│ 🔗 Related Threat (Optional)           │
│ [Brute Force Attack (high - new)  ▼]  │
│ └─ Link this alert to an existing...   │
│                                         │
│         [Cancel]  [Create Alert]       │
└─────────────────────────────────────────┘
```

---

### 2. ✅ **ThreatDetailModal.tsx** - Afficher les Alertes Liées

**Nouvel onglet ajouté:**
```typescript
tabs = [
  { id: 'details', label: 'Details', icon: AlertTriangle },
  { id: 'alerts', label: 'Related Alerts', icon: Bell, count: alertCount },
  { id: 'ai-analysis', label: 'AI Analysis', icon: Sparkles },
  ...
]
```

**Fonctionnalités:**
- ✅ Onglet "Related Alerts" avec compteur de badges
- ✅ Query automatique: `GET /api/threat-intelligence/alerts/?threat={id}`
- ✅ Affichage en cartes des alertes liées
- ✅ Badges de sévérité et statut pour chaque alerte
- ✅ Message si aucune alerte liée

**Interface:**
```
┌─────────────────────────────────────────────────────────┐
│ Brute Force Attack Campaign (high)                  ✕  │
├─────────────────────────────────────────────────────────┤
│ [Details] [Related Alerts (3)] [AI Analysis] ...       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 🔔 Failed login - IP 192.168.1.100  [high] [new] │ │
│ │ Multiple failed authentication attempts...        │ │
│ │ Type: unauthorized_access • 10:30 AM              │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 🔔 Failed login - IP 192.168.1.100  [high] [ack] │ │
│ │ Continued brute force attempts...                 │ │
│ │ Type: unauthorized_access • 10:32 AM              │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 🔔 Account locked - user admin    [medium] [res] │ │
│ │ Account locked due to failed attempts             │ │
│ │ Type: system • 10:35 AM                           │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**État vide:**
```
        🔔
  No Related Alerts
  
No alerts have been linked
  to this threat yet
```

---

### 3. ✅ **ThreatIntel.tsx** - Badge Compteur d'Alertes

**Ajouté sur chaque carte de menace:**
```typescript
{threat.alert_count > 0 && (
  <span className="badge-orange">
    <Bell /> {threat.alert_count} alerts
  </span>
)}
```

**Rendu visuel:**
```
┌────────────────────────────────────────────────────┐
│ Brute Force Attack Campaign                        │
│ [critical] [investigating] [🔔 3 alerts]           │
│                                                    │
│ Multiple failed login attempts detected from      │
│ suspicious IP addresses targeting admin accounts  │
│                                                    │
│ Type: cyber • Source: IDS • Oct 29, 2025         │
│                                                    │
│                      [View Details] [🗑️]          │
└────────────────────────────────────────────────────┘
```

---

## 🔌 API Backend (Déjà Implémenté)

### Serializer - ThreatSerializer

```python
class ThreatSerializer(serializers.ModelSerializer):
    alert_count = serializers.SerializerMethodField()
    
    def get_alert_count(self, obj):
        return obj.alerts.count()  # ✅ Compte les alertes liées
```

**Champs retournés:**
```json
{
  "id": 1,
  "title": "Brute Force Attack",
  "severity": "high",
  "status": "investigating",
  "alert_count": 3,  // ✅ Nombre d'alertes liées
  ...
}
```

### Endpoints Utilisés

```http
# Récupérer les menaces avec compteur d'alertes
GET /api/threat-intelligence/threats/
Response: [ { "id": 1, "alert_count": 3, ... }, ... ]

# Récupérer les alertes d'une menace spécifique
GET /api/threat-intelligence/alerts/?threat=1
Response: [ { "id": 5, "threat": 1, ... }, ... ]

# Créer une alerte liée à une menace
POST /api/threat-intelligence/alerts/
Body: {
  "title": "Failed login",
  "threat": 1,  // ✅ Lien vers la menace
  ...
}
```

---

## 💡 Cas d'Usage

### Scénario 1: Création d'Alerte Autonome
```
1. Le système détecte un événement suspect
2. Génère automatiquement une alerte (sans threat)
3. L'analyste examine l'alerte
4. Décide s'il s'agit d'une vraie menace
```

### Scénario 2: Lier Plusieurs Alertes à une Menace
```
1. Plusieurs alertes similaires arrivent:
   - "Failed login from IP A"
   - "Failed login from IP B"
   - "Failed login from IP C"

2. L'analyste crée une menace:
   - "Distributed Brute Force Campaign"

3. L'analyste lie toutes les alertes à cette menace
   
4. Dashboard affiche:
   - Menace: "Distributed Brute Force" [🔔 3 alerts]
```

### Scénario 3: Création d'Alerte Liée Directement
```
1. Une menace "Ransomware Attack" existe déjà
2. Un nouvel événement est détecté
3. L'analyste crée une alerte et la lie immédiatement:
   - Alert: "Suspicious file encryption"
   - Threat: "Ransomware Attack" (sélectionné)
```

---

## 🎯 Avantages de cette Relation

### 1. **Corrélation des Événements** 🔍
- Grouper plusieurs alertes sous une seule menace
- Vue d'ensemble des campagnes d'attaque
- Détection de patterns

### 2. **Priorisation** 📊
- Voir rapidement quelles menaces ont le plus d'alertes
- Badge orange attire l'attention
- Tri par nombre d'alertes possible

### 3. **Analyse Contextuelle** 🧠
- Comprendre l'évolution d'une menace
- Timeline des événements liés
- Impact global évalué

### 4. **Workflow Amélioré** ⚡
- Créer alerte → Lier threat (1 clic)
- Voir threat → Liste alertes (1 clic)
- Navigation intuitive

---

## 📊 Statistiques et Métriques

### Dashboard Impact

**Avant:**
```
Active Threats: 5
```

**Après:**
```
Active Threats: 5
├─ Brute Force (🔔 3 alerts)
├─ Phishing Campaign (🔔 7 alerts)
├─ DDoS Attack (🔔 2 alerts)
├─ Insider Threat (🔔 0 alerts)
└─ Data Exfiltration (🔔 1 alert)
```

**Insight:** La "Phishing Campaign" avec 7 alertes nécessite une attention prioritaire!

---

## 🔄 Flux de Données

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  CreateAlertModal                                       │
│  ↓ POST /alerts/ { threat: 1 }                         │
│  ├─ useQuery(['threats']) // Dropdown                  │
│  └─ useMutation // Create avec threat_id               │
│                                                         │
│  ThreatDetailModal                                      │
│  ↓ GET /alerts/?threat=1                               │
│  ├─ useQuery(['threat-alerts', id])                    │
│  └─ Affiche liste des alertes liées                    │
│                                                         │
│  ThreatCard                                             │
│  ├─ Affiche alert_count depuis threat                  │
│  └─ Badge orange si > 0                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
                       ↕️  HTTP
┌─────────────────────────────────────────────────────────┐
│                     BACKEND                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ThreatSerializer                                       │
│  ├─ alert_count = SerializerMethodField()              │
│  └─ get_alert_count() → obj.alerts.count()             │
│                                                         │
│  AlertViewSet                                           │
│  ├─ Filter by threat_id query param                    │
│  └─ Returns alerts for specific threat                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
                       ↕️  ORM
┌─────────────────────────────────────────────────────────┐
│                    DATABASE                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  threat_intelligence_threat                             │
│  ├─ id (PK)                                            │
│  ├─ title                                              │
│  └─ ...                                                │
│       ↑                                                │
│       │ ForeignKey (related_name='alerts')             │
│       │                                                │
│  threat_intelligence_alert                              │
│  ├─ id (PK)                                            │
│  ├─ threat_id (FK, nullable)                           │
│  └─ ...                                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist d'Implémentation

### Frontend
- ✅ CreateAlertModal: Dropdown de sélection de threat
- ✅ CreateAlertModal: Icône Link2 et texte explicatif
- ✅ CreateAlertModal: Query des threats disponibles
- ✅ ThreatDetailModal: Nouvel onglet "Related Alerts"
- ✅ ThreatDetailModal: Query des alertes liées
- ✅ ThreatDetailModal: Badge count sur l'onglet
- ✅ ThreatDetailModal: Affichage en cartes des alertes
- ✅ ThreatIntel: Badge alert_count sur cartes de menaces
- ✅ ThreatIntel: Icône Bell dans le badge

### Backend
- ✅ Alert.threat ForeignKey (déjà implémenté)
- ✅ ThreatSerializer.alert_count (déjà implémenté)
- ✅ AlertSerializer.threat_details (déjà implémenté)
- ✅ API filter by threat ID (déjà implémenté)

---

## 🎉 Résultat Final

**La relation Threat ↔ Alert est maintenant complètement fonctionnelle!**

### Utilisateur peut:
1. ✅ Créer une alerte seule OU liée à une menace
2. ✅ Voir toutes les alertes d'une menace
3. ✅ Identifier rapidement les menaces avec beaucoup d'alertes
4. ✅ Naviguer intuitivement entre menaces et alertes
5. ✅ Corréler les événements de sécurité

### Bénéfices:
- 🎯 Meilleure visibilité des campagnes d'attaque
- 📊 Priorisation basée sur le nombre d'alertes
- 🔍 Analyse contextuelle améliorée
- ⚡ Workflow plus efficace
- 🧠 Intelligence de menace enrichie

---

**SafeNest Threat Intelligence est maintenant une solution complète de gestion des menaces et alertes!** 🚀
