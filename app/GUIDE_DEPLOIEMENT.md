# 🚀 Guide de mise en ligne — DM Energie Solutions

## Architecture
- **Frontend** (ce que vous voyez) → dossier `frontend/` → hébergé sur **Vercel** (gratuit)
- **Backend** (génération PDF) → dossier `backend/` → hébergé sur **Railway** (gratuit)
- Domaine → **dmenergiesolutions.fr** → connecté à Vercel

---

## ÉTAPE 1 — Déployer le Backend sur Railway

1. Créez un compte sur [railway.app](https://railway.app) (gratuit, connexion avec GitHub)
2. Cliquez "New Project" → "Deploy from GitHub repo"
3. Uploadez le dossier `backend/` sur un repo GitHub privé
4. Railway détecte automatiquement Python et installe les dépendances
5. Notez l'URL générée, ex: `https://dm-backend.railway.app`
6. ⚠️ Copiez cette URL — vous en aurez besoin à l'étape 3

## ÉTAPE 2 — Déployer le Frontend sur Vercel

1. Créez un compte sur [vercel.com](https://vercel.com) (gratuit, connexion avec GitHub)
2. Cliquez "New Project" → uploadez le dossier `frontend/`
3. Vercel déploie automatiquement en quelques secondes
4. Vous obtenez une URL temporaire, ex: `https://dm-app.vercel.app`

## ÉTAPE 3 — Connecter le Backend au Frontend

1. Ouvrez le fichier `frontend/index.html`
2. Ligne 2 du bloc `<script>`, remplacez :
   ```
   const API_URL = 'https://votre-backend.railway.app';
   ```
   par votre vraie URL Railway, ex:
   ```
   const API_URL = 'https://dm-backend.railway.app';
   ```
3. Re-déployez le frontend sur Vercel

## ÉTAPE 4 — Connecter votre domaine dmenergiesolutions.fr

### Sur Vercel :
1. Allez dans votre projet → "Settings" → "Domains"
2. Ajoutez `app.dmenergiesolutions.fr`
3. Vercel vous donne des valeurs DNS à copier

### Sur votre registrar (OVH, Gandi, etc.) :
1. Connectez-vous à votre espace client
2. Allez dans "Zone DNS" de dmenergiesolutions.fr
3. Ajoutez un enregistrement CNAME :
   - Nom : `app`
   - Valeur : `cname.vercel-dns.com`
4. Attendez 5-30 minutes que ça se propage

✅ Votre app sera accessible sur `https://app.dmenergiesolutions.fr`

---

## Structure des fichiers

```
app/
├── backend/
│   ├── app.py              # API Flask
│   ├── pdf_engine.py       # Moteur PDF
│   ├── requirements.txt    # Dépendances Python
│   ├── Procfile            # Config déploiement
│   ├── Logo_DM.PNG
│   ├── Qualipac_v2_transparent.png
│   └── ventil_v2_transparent.png
└── frontend/
    └── index.html          # App complète
```

---

## En cas de problème

- **Le PDF ne se génère pas** → Vérifiez que l'URL dans `API_URL` est correcte
- **Erreur CORS** → Le backend autorise déjà `dmenergiesolutions.fr`
- **Le site ne s'affiche pas** → Attendez 30 min après avoir changé les DNS

---

## Support

Pour toute modification de l'application (nouveaux tarifs, nouvelles prestations,
changements de design), partagez le fichier `index.html` et `pdf_engine.py`
avec Claude et décrivez ce que vous souhaitez changer.
