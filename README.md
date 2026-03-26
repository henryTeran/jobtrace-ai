# JobTrace AI

Backend FastAPI pour synchroniser des emails Gmail et Outlook, detecter les candidatures, extraire des informations metier, stocker les donnees et produire des rapports PDF mensuels.

## 1. Installation (WSL + Conda)

### Prerequis
- WSL Ubuntu actif
- Conda installe
- Python 3.11

### Setup environnement
```bash
cd /home/henry/projects/jobtrace-ai
conda env create -f environment.yml
conda activate jobtrace
cp .env.example .env
```

Si besoin via pip:
```bash
pip install -r requirements.txt
```

## 2. Configuration OAuth Google (Gmail)

1. Aller sur Google Cloud Console.
1. Creer un projet et activer Gmail API.
1. Configurer un ecran de consentement OAuth.
1. Creer des identifiants OAuth2 Web Application.
1. Ajouter l'URI de redirection:
   - `http://localhost:8000/auth/google/callback`
1. Renseigner dans `.env`:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

Scope utilise: `https://www.googleapis.com/auth/gmail.readonly`

## 3. Configuration OAuth Microsoft (Outlook/Hotmail)

1. Aller sur Azure Portal > App registrations.
1. Creer une application.
1. Ajouter l'URI de redirection:
   - `http://localhost:8000/auth/microsoft/callback`
1. Creer un Client Secret.
1. Ajouter la permission API Microsoft Graph deleguee:
   - `Mail.Read`
1. Renseigner dans `.env`:
   - `MICROSOFT_CLIENT_ID`
   - `MICROSOFT_CLIENT_SECRET`
   - `MICROSOFT_TENANT_ID` (ex: `common`)

Scope utilise: `Mail.Read`

## 4. Lancement

```bash
python run.py
```

Docs Swagger:
- http://localhost:8000/docs

Healthcheck:
- `GET /health`

## 5. Endpoints

### Auth
- `GET /auth/google/login`
- `GET /auth/google/callback?code=...`
- `GET /auth/microsoft/login`
- `GET /auth/microsoft/callback?code=...`

### Emails
- `POST /emails/sync`

Exemple body:
```json
{
  "providers": ["gmail", "outlook"],
  "limit_per_provider": 50
}
```

### Reports
- `GET /reports/monthly`
- `POST /reports/pdf`

Exemple body PDF:
```json
{
  "months": ["2026-02", "2026-03"],
  "output_filename": "report_mars_2026.pdf"
}
```

## 6. Architecture

```text
jobtrace-ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── auth_google.py
│   │   ├── auth_microsoft.py
│   │   ├── emails.py
│   │   └── reports.py
│   ├── connectors/
│   │   ├── gmail_connector.py
│   │   └── outlook_connector.py
│   ├── services/
│   │   ├── email_normalizer.py
│   │   ├── email_filter.py
│   │   ├── email_extractor.py
│   │   ├── sync_service.py
│   │   ├── monthly_report_service.py
│   │   └── pdf_service.py
│   └── utils/
│       ├── logger.py
│       └── dates.py
├── reports/
├── data/
├── .env.example
├── environment.yml
├── requirements.txt
├── README.md
└── run.py
```

## 7. Notes techniques

- Les tokens OAuth sont stockes localement en base SQLite (`oauth_tokens`).
- Les emails sont dedoublonnes avec une contrainte unique (`provider`, `message_id`).
- Le PDF contient un tableau par mois avec style professionnel et lisible.
- Le traitement est modulaire et pret a evoluer vers un CRM.
