# RedSage v2: Running the Application

RedSage v2 is a local-first, human-in-the-loop workflow companion. It never
executes security tooling; all evidence is pasted or imported by the operator.

There are two ways to run the app.

## Dev Mode (two terminals)

Frontend dev server with hot reload, backend with live API docs.

Terminal 1 - backend:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/api/v1/health
- Interactive docs: http://127.0.0.1:8000/docs

Terminal 2 - frontend:

```powershell
cd frontend
npm install
npm run dev
```

- UI: http://127.0.0.1:5173

In dev mode the backend enables CORS for `http://127.0.0.1:5173` and
`http://localhost:5173`. The React app calls the backend directly.

## Prod-Like Local Mode (single command)

Build the frontend, then run only the backend. FastAPI serves the built UI
from `frontend/dist` on the same origin as the API.

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000.

Behavior:

- `GET /` serves `frontend/dist/index.html`
- Static assets (`/assets/*.js`, `/assets/*.css`) are served by FastAPI
- API endpoints remain under `/api/v1/*`
- Export/import archives and report downloads continue to stream correctly
  because API routes are registered before the SPA fallback
- If `frontend/dist/index.html` does not exist, `GET /` returns a helpful
  message with the exact build command instead of a blank page

There is no separate production web server; uvicorn handles both the API and
the static UI.

## Tests and build checks

Backend tests:

```powershell
python -m pytest
```

Backend compile check:

```powershell
python -m compileall backend
```

Frontend production build:

```powershell
cd frontend
npm run build
```
