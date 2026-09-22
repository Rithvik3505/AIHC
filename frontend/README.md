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
- `/evaluate`: live backend workflow list and live synthetic Golden Workflow runs.
- `/reports`: static synthetic demo report.
- `/taxonomy`: live backend taxonomy registry browser with normalized diagnostic fields.
- `/benchmarks`: static synthetic reference benchmark view.

The upload panel is an evidence-contract disclosure surface. It does not upload
customer files in the current MVP.

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
