# web_sota – Fleet-standard webapp (retractable sidebar, multiple pages)

**start.ps1** launches backend and SPA frontend, then opens the app in the browser.

- **Backend**: FastAPI on **10746** — `/health`, `/api/help`, `/api/scriptlets`, `/status`, `/tool`.
- **Frontend**: Vite + React on **10747** — retractable sidebar, routes: Overview, Help, Scriptlets, Status. Proxies `/api` and `/health` to backend.
- **start.ps1**: Kills 10746 and 10747, starts backend, waits for listen, runs `npm install` (if needed) and `npm run dev` in web_sota, opens `http://127.0.0.1:10747/`.

**Fleet manifest**: `startPath`: `web_sota/start.ps1`, `port`: 10747 (user-facing), `healthPath`: `/health` (backend; frontend proxies it).
