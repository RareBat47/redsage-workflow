# RedSage v2: Safe Demo Walkthrough

This walkthrough uses only inert, local evidence. RedSage never executes a scan,
never opens a socket to a target, and never runs the commands it displays. All
testing is performed manually by the human operator outside the application;
the operator pastes the resulting output into RedSage as evidence.

Prerequisites:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd frontend; npm install; cd ..
```

## Demo A: Dev mode (two terminals)

Terminal 1:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## Demo B: Prod-like mode (one process)

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Walkthrough

1. Create a project: click **+ New Project**, enter `Demo Audit`, confirm.

2. Lock the scope:
   - Click **Configure & Lock Scope**, enter `juice-shop.local`, confirm.
   - The header badge changes to **SCOPE LOCKED**.

3. Select task **2.2 Web Content & Directory Discovery** in the task tree.
   - A suggested command is shown. Copying is enabled only when the resolved
     target is in the locked whitelist.

4. Submit inert evidence: paste the following into the Evidence tray:

   ```text
   ffuf -u https://juice-shop.local/FUZZ
   [Status: 200, Size: 1024]
   /backup.zip  [Status: 200, Size: 1048576]
   ```

   Click **Verify Evidence**. Because no `CO_API_KEY` is configured, the local
   deterministic verifier runs offline. The verdict card shows a **PASS**
   badge, a grounded quotation, and the extracted file `/backup.zip`.

5. Note the **Saved as EVID-XXXXXXXXXX** line; open **Evidence Library** to see
   the artifact metadata, SHA-256 digest, and the full artifact in the drawer.

6. A governed proposal appears in the left panel: **Investigate Exposed Asset:
   /backup.zip**. Approve it to create a new Phase 4 task, or dismiss it.

7. Log a finding: click **+ Log Finding**, enter `Backup archive exposure`,
   choose severity, and leave the evidence ID from the latest verification.
   Creating a confirmed finding requires a valid linked evidence ID.

8. Open **Report Studio**. The readiness panel may show warnings; the Markdown
   report includes scope, methodology, assets, confirmed findings with
   **Evidence Ref**, and the **Appendix: Evidence Register & Integrity Log**.
   Click **Download Report (.md)**.

9. Export/import: click **Export Project** to download the project ZIP; then
   click **Import Project** to restore it as a new project with all rows and
   artifacts remapped.

## Expected end state

- Scope locked and recorded in the audit trail.
- One artifact on disk under `data/projects/{project_id}/artifacts/`.
- One pending or approved governed proposal.
- At least one finding linked to evidence.
- A downloadable Markdown report with the evidence register appendix.
