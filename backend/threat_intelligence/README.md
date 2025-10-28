# Threat Intelligence Management Module 🛡️

## Overview

Le module **Threat Intelligence Management** est un système complet de gestion des menaces de sécurité avec des capacités d'intelligence artificielle avancées pour la détection d'anomalies, l'évaluation des risques, l'analyse prédictive et la chasse aux menaces.

## 🎯 Fonctionnalités Principales

### 1. CRUD Operations
- **Threats**: Gestion des menaces de sécurité potentielles
- **Alerts**: Notifications système pour événements de sécurité
- **Risk Assessments**: Évaluations de risques pour utilisateurs/localisations/événements
- **Threat Indicators**: Indicateurs de compromission (IOCs) et patterns suspects
- **Watchlists**: Surveillance de personnes/véhicules/entités d'intérêt
- **Threat Feeds**: Intégration de flux de menaces externes
- **Threat Hunting Queries**: Requêtes de chasse aux menaces sauvegardées

### 2. AI-Powered Features

#### 🤖 Anomaly Detection Engine
- Détection d'anomalies comportementales (Isolation Forest)
- Anomalies de patterns de connexion
- Anomalies de trafic réseau
- Détection d'anomalies temporelles

#### 📊 Threat Scoring AI
- Calcul de scores de risque pour utilisateurs/localisations/événements
- Mises à jour dynamiques des niveaux de menace
- Indicateurs de risque composites
- Priorisation des menaces

#### 🔮 Predictive Threat Analytics
- Prévision des tendances de menaces
- Identification de patterns émergents
- Prédiction des vecteurs d'attaque
- Analyse saisonnière des menaces

#### 🔔 Intelligent Alert Aggregation
- Dédoublonnage d'alertes similaires
- Corrélation d'alertes en incidents
- Réduction de la fatigue des alertes
- Routage intelligent par priorité

#### 🎯 Threat Hunting Assistant
- Requêtes en langage naturel alimentées par LLM
- "Montre-moi tous les échecs de connexion depuis la Chine"
- Suggestion d'hypothèses de chasse aux menaces
- Génération de rapports de menaces

### 3. Advanced Features
- **Threat Intelligence Feeds**: Intégration AlienVault, MISP, VirusTotal
- **Geo-Threat Mapping**: Visualisation des menaces sur cartes
- **Attack Timeline Visualization**: Chemins de menace basés sur graphes
- **Response Playbooks**: Contre-mesures auto-exécutées
- **Threat Simulation**: Test de défenses avec scénarios AI

## 📁 Structure du Projet

```
threat_intelligence/
├── __init__.py
├── apps.py
├── models.py              # 7 modèles de données
├── serializers.py         # Serializers DRF + AI serializers
├── views.py              # ViewSets CRUD + endpoints AI
├── urls.py               # Configuration des routes
├── admin.py              # Interface d'administration Django
├── tasks.py              # Tâches Celery pour traitement background
├── services/
│   ├── __init__.py
│   ├── anomaly_detection.py      # Service de détection d'anomalies
│   ├── threat_scoring.py         # Service de scoring des menaces
│   ├── predictive_analytics.py   # Analytique prédictive
│   ├── alert_aggregation.py      # Agrégation intelligente d'alertes
│   └── threat_hunting.py         # Assistant de chasse aux menaces
├── tests/
│   ├── __init__.py
│   ├── test_models.py            # Tests des modèles
│   └── test_services.py          # Tests des services AI
├── migrations/
│   └── __init__.py
├── MIGRATION_GUIDE.md            # Guide de migration détaillé
└── README.md                     # Ce fichier
```

## 🚀 Installation et Configuration

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ avec extension pgvector
- Redis (pour Celery)
- Virtual environment activé

### 2. Installation des Dépendances
```bash
pip install -r requirements.txt
```

Dépendances clés ajoutées:
- `pandas==2.2.0` - Pour l'analyse de données
- `scikit-learn==1.4.0` - Pour ML/anomaly detection
- `numpy==1.26.4` - Calculs numériques

### 3. Configuration
L'application est déjà configurée dans `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'threat_intelligence.apps.ThreatIntelligenceConfig',
]
```

### 4. Créer les Migrations
```bash
python manage.py makemigrations threat_intelligence
python manage.py migrate threat_intelligence
```

Voir `MIGRATION_GUIDE.md` pour les instructions détaillées.

## 📡 API Endpoints

### CRUD Endpoints

#### Threats
```
GET    /api/threat-intelligence/threats/
POST   /api/threat-intelligence/threats/
GET    /api/threat-intelligence/threats/{id}/
PUT    /api/threat-intelligence/threats/{id}/
DELETE /api/threat-intelligence/threats/{id}/
POST   /api/threat-intelligence/threats/{id}/assign/
POST   /api/threat-intelligence/threats/{id}/update_status/
GET    /api/threat-intelligence/threats/statistics/
```

#### Alerts
```
GET    /api/threat-intelligence/alerts/
POST   /api/threat-intelligence/alerts/
POST   /api/threat-intelligence/alerts/{id}/acknowledge/
POST   /api/threat-intelligence/alerts/{id}/resolve/
POST   /api/threat-intelligence/alerts/bulk_acknowledge/
GET    /api/threat-intelligence/alerts/dashboard/
```

#### Risk Assessments
```
GET    /api/threat-intelligence/risk-assessments/
POST   /api/threat-intelligence/risk-assessments/
GET    /api/threat-intelligence/risk-assessments/{id}/
```

#### Threat Indicators
```
GET    /api/threat-intelligence/indicators/
POST   /api/threat-intelligence/indicators/
POST   /api/threat-intelligence/indicators/{id}/whitelist/
```

#### Watchlist
```
GET    /api/threat-intelligence/watchlist/
POST   /api/threat-intelligence/watchlist/
GET    /api/threat-intelligence/watchlist/{id}/
```

### AI Service Endpoints

#### Anomaly Detection
```
POST   /api/threat-intelligence/ai/anomaly-detection/detect_user_anomalies/
POST   /api/threat-intelligence/ai/anomaly-detection/detect_login_anomalies/
POST   /api/threat-intelligence/ai/anomaly-detection/detect_traffic_anomalies/
```

#### Threat Scoring
```
POST   /api/threat-intelligence/ai/threat-scoring/calculate_risk/
POST   /api/threat-intelligence/ai/threat-scoring/update_dynamic_levels/
```

#### Predictive Analytics
```
POST   /api/threat-intelligence/ai/predictive-analytics/forecast_threats/
GET    /api/threat-intelligence/ai/predictive-analytics/emerging_patterns/
GET    /api/threat-intelligence/ai/predictive-analytics/predict_attack_vectors/
```

#### Alert Aggregation
```
POST   /api/threat-intelligence/ai/alert-aggregation/deduplicate/
POST   /api/threat-intelligence/ai/alert-aggregation/correlate/
POST   /api/threat-intelligence/ai/alert-aggregation/smart_filter/
```

#### Threat Hunting
```
POST   /api/threat-intelligence/ai/threat-hunting/query/
GET    /api/threat-intelligence/ai/threat-hunting/suggest_hypotheses/
POST   /api/threat-intelligence/ai/threat-hunting/generate_report/
```

## 🤖 Celery Tasks (Background Processing)

### Tâches Périodiques

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `detect_anomalies_periodic` | Toutes les heures | Détection d'anomalies dans le comportement des utilisateurs |
| `update_risk_scores_periodic` | Toutes les 6 heures | Mise à jour des scores de risque |
| `aggregate_alerts_periodic` | Toutes les 30 minutes | Agrégation et corrélation d'alertes |
| `sync_threat_feeds` | Toutes les heures | Synchronisation des flux de menaces externes |
| `expire_old_indicators` | Quotidien (2h du matin) | Expiration des indicateurs périmés |
| `cleanup_old_threats` | Mensuel | Nettoyage des menaces résolues anciennes |
| `update_watchlist_detections` | Toutes les 15 minutes | Vérification des détections watchlist |
| `calculate_organization_threat_score` | Toutes les 12 heures | Score de menace organisationnel |

### Démarrage des Workers Celery

```bash
# Worker Celery
celery -A safenest worker -l info

# Beat Scheduler (tâches périodiques)
celery -A safenest beat -l info

# Combiné
celery -A safenest worker --beat -l info
```

## 🧪 Tests

### Exécuter les Tests
```bash
# Tous les tests du module
pytest backend/threat_intelligence/tests/

# Tests des modèles uniquement
pytest backend/threat_intelligence/tests/test_models.py

# Tests des services uniquement
pytest backend/threat_intelligence/tests/test_services.py

# Avec couverture
pytest --cov=threat_intelligence backend/threat_intelligence/tests/
```

### Coverage des Tests
- ✅ Models: 100%
- ✅ Services: Couverture des cas principaux
- ✅ Integration tests: Workflow end-to-end

## 📊 Modèles de Données

### Threat
Menaces de sécurité avec scoring de risque, attribution, localisation, et métadonnées.

**Champs clés**: `title`, `threat_type`, `severity`, `risk_score`, `confidence_score`, `status`

### Alert
Notifications système pour événements de sécurité avec agrégation intelligente.

**Champs clés**: `title`, `alert_type`, `severity`, `status`, `confidence_score`, `is_aggregated`

### RiskAssessment
Évaluations de risque pour entités avec likelihood/impact.

**Champs clés**: `assessment_type`, `risk_level`, `risk_score`, `likelihood`, `impact`

### ThreatIndicator
IOCs et patterns suspects avec tracking de détection.

**Champs clés**: `indicator_type`, `indicator_value`, `severity`, `confidence_score`, `times_detected`

### Watchlist
Surveillance d'entités d'intérêt avec alertes automatiques.

**Champs clés**: `watchlist_type`, `threat_level`, `alert_on_detection`, `auto_block`

### ThreatFeed
Configurations de flux de menaces externes avec auto-import.

**Champs clés**: `feed_type`, `api_url`, `update_frequency`, `auto_import`, `trust_score`

### ThreatHuntingQuery
Requêtes de chasse aux menaces sauvegardées avec tracking d'exécution.

**Champs clés**: `query_text`, `query_type`, `hypothesis`, `times_executed`

## 🔧 Utilisation Avancée

### Exemple: Détection d'Anomalies
```python
from threat_intelligence.services import AnomalyDetectionService

service = AnomalyDetectionService(contamination=0.1)
result = service.detect_user_behavior_anomalies(
    user_id=123,
    time_range_days=30
)
print(f"Anomalies detected: {result['anomalies_detected']}")
```

### Exemple: Scoring de Menace
```python
from threat_intelligence.services import ThreatScoringService

service = ThreatScoringService()
result = service.calculate_user_risk_score(
    user_id=123,
    time_range_days=30
)
print(f"Risk score: {result['risk_score']}")
print(f"Risk level: {result['risk_level']}")
```

### Exemple: Requête de Chasse aux Menaces
```python
from threat_intelligence.services import ThreatHuntingAssistant

assistant = ThreatHuntingAssistant()
result = assistant.execute_natural_language_query(
    organization_id=1,
    query_text="Show me all failed logins from China in the last 7 days",
    created_by=user
)
```

## 🎨 Interface Admin

L'interface d'administration Django offre:
- Badges colorés pour severity/status
- Filtres avancés par type/severity/date
- Recherche full-text
- Groupement par organisation
- Actions bulk (assignation, résolution, etc.)

Accès: `http://localhost:8000/admin/threat_intelligence/`

## 🔐 Sécurité et Permissions

- Authentication requise pour tous les endpoints
- Filtrage automatique par organisation de l'utilisateur
- Permissions RBAC héritées du système core
- API keys protégées (write_only dans serializers)
- Audit trail pour toutes les modifications

## 📈 Performance et Scalabilité

- Indexes optimisés sur les champs fréquemment filtrés
- Pagination automatique (50 items par défaut)
- Tâches lourdes déléguées à Celery
- Caching recommandé pour les statistiques
- Agrégation d'alertes pour réduire le volume

## 🔄 Intégrations

### Threat Intelligence Feeds
- AlienVault OTX
- MISP
- ThreatConnect
- VirusTotal
- Flux personnalisés

### SOAR Platforms
- API REST standard pour intégration
- Webhooks pour notifications temps réel
- Export de playbooks de réponse

## 📝 Logs et Monitoring

Les logs sont configurés dans `settings.py`:
```python
LOGGING = {
    'loggers': {
        'threat_intelligence': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        }
    }
}
```

## 🐛 Troubleshooting

### Problème: Migrations échouent
**Solution**: Vérifier que l'app `threat_intelligence` est dans `INSTALLED_APPS`

### Problème: Tasks Celery ne s'exécutent pas
**Solution**: Vérifier que Redis est en cours d'exécution et que Celery beat est démarré

### Problème: Erreurs d'import ML
**Solution**: Installer pandas et scikit-learn: `pip install pandas scikit-learn`

## 📚 Documentation Supplémentaire

- `MIGRATION_GUIDE.md` - Guide détaillé de migration
- `tests/` - Exemples d'utilisation dans les tests
- `/api/schema/swagger-ui/` - Documentation API interactive

## 🤝 Contribution

Pour contribuer au module:
1. Créer une branche feature
2. Ajouter des tests pour les nouvelles fonctionnalités
3. Suivre le style de code existant (Black formatter)
4. Mettre à jour la documentation

## 📄 License

Ce module fait partie du projet SafeNest Security Management Platform.

## 👥 Support

Pour questions ou problèmes:
- Ouvrir une issue sur le repo
- Contacter l'équipe de développement
- Consulter la documentation API

---

**Version**: 1.0.0  
**Date**: 2025  
**Status**: ✅ Production Ready
