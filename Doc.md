# SafeNest: Smart Access & Incident Management Platform — AI & LLM Integration Plan

This plan structures the selected project into concrete components: Django apps, models, services, pipelines for **face tracking/recognition**, and **LLM-powered assistants** (chatbot, recommendations, incident analysis). It’s organized for an MVP you can demo in weeks, with stretch goals.

---

## 1) High‑Level Architecture
- **Client**: Web UI (Django Templates or React) + WebRTC camera stream (optional) + WebSocket for live alerts.
- **Backend**: Django (auth, RBAC, APIs), Django Channels (real-time), Celery workers (AI pipelines), Redis (broker/cache), PostgreSQL (+ pgvector), MinIO/S3 (media).
- **AI Services**:
  - Face detection/embedding: **InsightFace** (or DeepFace) + ONNX Runtime.
  - Anomaly detection: scikit-learn or PyOD (Isolation Forest).
  - LLM layer: OpenAI/Local (Ollama) via a **Tools/Agents** service for function-calling (logs search, incident creation, recommendations).
- **Observability**: Prometheus + Grafana.

```text
Browser <WebRTC/WS> ⇄ Django Channels (ASGI)
REST/GraphQL ⇄ Django API (DRF)
                ⇄ Celery Workers (AI tasks)
                ⇄ PostgreSQL (+pgvector)
                ⇄ MinIO/S3 (faces, frames)
                ⇄ Redis (queue/cache)
```

---

## 2) Django Apps (Monorepo)
1. **core/** – settings, users, orgs, roles, teams, audit middleware.
2. **security/** – sessions, login events, anomaly rules, alerts.
3. **incidents/** – incident CRUD, workflows, evidence, timelines.
4. **faces/** – cameras, streams, detections, identities, embeddings.
5. **llm/** – chat sessions, prompts, tools (function-calls), RAG over logs.
6. **dashboard/** – KPIs, charts, realtime panels.

---

## 3) Data Model (key tables)

### core/models.py
- **Organization**(name, settings)
- **User**(extends AbstractUser; org FK; role = Admin/SecOfficer/Employee)
- **Role** + **Permission** (or use django-guardian)

### security/models.py
- **LoginEvent**(user, ip, geo, user_agent, success, ts, risk_score)
- **AnomalyRule**(name, rule_type [time, geo, device], threshold, active)
- **Alert**(severity, message, related_object, status, created_by, ts)

### incidents/models.py
- **Incident**(title, type, severity, status, assignee, created_by, org, opened_at, closed_at)
- **IncidentEvent**(incident, action, meta, actor, ts)
- **Evidence**(incident, file, kind [frame, image, log], hash)

### faces/models.py
- **Camera**(org, name, rtsp_url, location, active)
- **FaceIdentity**(org, person_label, person_meta JSON)
- **FaceEmbedding**(identity FK, vector [pgvector], model_name, created_at)
- **FaceDetection**(camera, frame_url, bbox, embedding_vector, similarity, identity [nullable], ts)

### llm/models.py
- **ChatSession**(org, user, bot_type [assistant/recommendation/analysis], title)
- **Message**(session, role [user/assistant/tool], content, ts)
- **PromptTemplate**(name, purpose, template_text)

> Use **pgvector** to store `FaceEmbedding.vector` and enable ANN search.

---

## 4) Face Tracking & Recognition Pipeline

### Option A: Server-Side RTSP → Worker
- Configure **Camera.rtsp_url**.
- Celery worker pulls frames (OpenCV), runs detection (RetinaFace), extracts **embedding** (ArcFace), queries pgvector for nearest identities.
- Store `FaceDetection` with bbox + similarity + optional `identity` link.
- Emit WebSocket event to UI: `face.detected` (with snapshot thumbnail).

### Option B: Browser Capture → Backend
- WebRTC getUserMedia → send frames via WebSocket or chunked upload.
- Backend/worker performs same pipeline, sends events back.

### Enrollment Flow
1. Admin creates **FaceIdentity** (label + meta like employee_id).
2. Upload 3–5 images per person; worker normalizes, computes embeddings → **FaceEmbedding** rows.
3. Recognition uses cosine similarity; configurable threshold (e.g., 0.35–0.5 depending on model scaling).

### Privacy & Security
- Consent & policy per **Organization**.
- Store embeddings (vectors) rather than raw faces where possible; keep raw frames as **Evidence** only when needed.
- Retention policy scheduler (delete old frames after N days).

---

## 5) Anomaly Detection & Alerts
- **Rules engine** (deterministic): time windows, country allow-list, device fingerprint, failed login bursts.
- **Statistical/ML**: per-user baseline of `LoginEvent` time/geo; Isolation Forest on features (hour, country, success rate, device entropy).
- On trigger → create **Alert** and optionally an **Incident** automatically, notify via email/SMS/Webhook.

---

## 6) LLM Integrations (three bots)

### 6.1 Assistant Chat Bot ("Cassistant")
Purpose: Help users navigate SafeNest, answer "how-to" and explain incidents.
- Tools:
  - `search_logs(query, time_range)` → returns matching LoginEvent/Alerts.
  - `open_incident(id)` / `create_incident(args)`.
  - `who_is(label)` → query FaceIdentity.
  - `show_camera(id)` → signed URL for last detections.
- Prompt Template (system):
  - "You are SafeNest Assistant. Be concise, cite objects by ID and time. When high-risk events appear, recommend opening an incident."

### 6.2 Recommendation Bot
Purpose: Suggest actions/policies.
- Inputs: recent Alerts/Incidents, anomaly stats.
- Outputs: recommended rules (e.g., block geo X; enforce 2FA for group Y; tighten similarity threshold for camera Z).
- Tool: `propose_rule(rule_type, params)` (draft in UI for admin approval).

### 6.3 Analysis Bot
Purpose: Summarize a day/week of security posture.
- Does RAG over:
  - Alerts, Incidents, FaceDetections.
  - System changes and outcomes.
- Vector store: pgvector with embeddings of serialized objects.
- Output: executive summary + hotspots + trend charts.

---

## 7) RAG & Prompt Engineering
- **Indexers**: nightly Celery task serializes objects (Alerts, Incidents, LoginEvents, FaceDetections) → chunk → embed → upsert into pgvector.
- **Message Orchestration**: guardrails (JSON schema), function-calling to SafeNest tools, enforce role-based data filtering per Organization.
- **Prompt Patterns**:
  - *Instruction + Context + Tools + Format*.
  - Provide **policy constraints** (no PII leakage across orgs, confidence thresholds).

---

## 8) Key APIs (DRF)
- `POST /api/faces/enroll/` → {identity_id, images[]}
- `POST /api/faces/detect/` → {camera_id|image, return_embeddings?}
- `GET /api/faces/detections?camera_id&since=`
- `GET /api/faces/identities/:id`
- `POST /api/security/login-events` (ingest from auth signals)
- `GET /api/security/alerts`
- `POST /api/incidents/` / `PATCH /api/incidents/:id`
- `WS /ws/alerts/` (Django Channels)
- `POST /api/llm/chat` (session, message)

---

## 9) UI Pages
1. **Dashboard**: KPIs (failed logins, open incidents, top cameras, risk map), live alert stream.
2. **Cameras**: grid of cameras, last detections, search by label.
3. **Faces**: enrollment wizard, identity gallery, merge/split identities.
4. **Incidents**: kanban + detail with timeline and evidence viewer.
5. **Rules**: manage anomaly rules and thresholds.
6. **LLM Studio**: chat console (assistant/analysis), recommendations panel with "Apply" button.

---

## 10) MVP Scope (2–3 weeks)
- Auth + RBAC (Admin, SecOfficer, Employee)
- LoginEvent capture + deterministic anomaly rules
- Alerts + WebSocket feed
- Incidents CRUD + evidence upload
- Faces: enrollment + single-image recognition (no live stream yet)
- Assistant Bot with 2 tools: `search_logs`, `create_incident`

**Stretch**
- RTSP ingestion worker, live camera wall
- Isolation Forest model + weekly Analysis Bot
- Recommendations Bot → draft rules

---

## 11) Tech Stack Choices
- **Django 5**, **DRF**, **Django Channels**
- **PostgreSQL 16** + **pgvector**
- **Redis** (Celery broker)
- **Celery** workers for AI
- **InsightFace/ArcFace** (embeddings), **RetinaFace** (detection), **ONNX Runtime**
- **OpenCV** for RTSP
- **MinIO/S3** for media
- **Plotly/Chart.js** for charts

---

## 12) Security & Compliance
- Per‑org data isolation; row‑level filters.
- Signed URLs for media; hash evidence.
- Consent banners and retention policies.
- Secrets via env; audit middleware logs all admin actions.

---

## 13) Example Pseudocode Snippets

**Face Enrollment Task**
```python
@shared_task
def enroll_identity(identity_id, image_urls):
    imgs = [load_img(u) for u in image_urls]
    embs = [arcface_embed(crop_face(i)) for i in imgs]
    for e in embs:
        FaceEmbedding.objects.create(identity_id=identity_id, vector=e)
```

**Recognition**
```python
def recognize(embedding, topk=3):
    sql = """
    SELECT id, identity_id, 1 - (vector <=> %s) AS similarity
    FROM faces_faceembedding
    ORDER BY vector <-> %s
    LIMIT %s
    """
    return db.query(sql, [embedding, embedding, topk])
```

**LLM Tool Schema (function-call)**
```json
{
  "name": "create_incident",
  "description": "Open a new incident with severity and context",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {"type":"string"},
      "severity": {"type":"string", "enum":["low","med","high"]},
      "context": {"type":"string"}
    },
    "required": ["title","severity"]
  }
}
```

---

## 14) Milestones & Deliverables
**Week 1**: Core apps, RBAC, LoginEvent capture, Alerts list, Incidents CRUD.
**Week 2**: Faces enrollment + recognition API, WebSocket alerts, Dashboard v1.
**Week 3**: Assistant bot with 2 tools, report page; demo + docs.
**Stretch**: RTSP ingestion, ML anomalies, recommendation engine.

---

## 15) Demo Scenarios (for grading)
1. Employee logs in from unusual country → alert fires → admin opens incident.
2. Upload a photo; system matches a known identity → shows history and related incidents.
3. Ask the assistant: “Show high-risk events from yesterday and open an incident.” It executes tools and returns links.

---

## 16) Next Steps
- Confirm MVP scope above.
- Decide on **InsightFace** vs **DeepFace**.
- Choose LLM provider (cloud vs local) and finalize tool list.
- I can then generate: **models.py**, **serializers.py**, **router/endpoints**, and a **docker-compose.yml** to run everything.

