# AI Health Check Frontend

Next.js MVP shell for founder-facing AI assurance diagnostics.

- Next.js
- TypeScript
- Tailwind
- shadcn-style local primitives
- Recharts
- Framer Motion-ready dependency

Pages:

- `/dashboard`: static synthetic demo dashboard.
- `/evaluate`: live workflow selection, demo/manual/upload evidence, preflight validation, per-test selection, results, and benchmark provenance.
- `/reports`: static synthetic demo report.
- `/taxonomy`: live backend taxonomy registry browser with normalized diagnostic fields.
- `/benchmarks`: static synthetic reference benchmark view.

CSV and JSON uploads are operational for the six Golden Workflows and are
processed ephemerally. Raw PDF/image document extraction is not implemented.

Run:

```powershell
cd frontend
npm install
npm run dev
```

Safe validation commands:

```powershell
npm run type-check
npm run lint
npm run build
```
