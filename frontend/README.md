# 🎨 Synthetic Data Studio - Frontend

Modern, interactive web client for **Synthetic Data Studio**, built with Next.js 15, React 19, TypeScript, and Tailwind CSS v4.

---

## 🚀 Features

- **Prompt Input Console**: Natural language input with quick-select example domain templates.
- **DataScout Strategy Card**: Displays heuristic & online search recommendations from Hugging Face and Kaggle.
- **Interactive Data Table**: Responsive preview with column sorting, row indices, and status indicators.
- **Live Metric Badges**: Real-time generation duration telemetry, row counts, and strategy badges.
- **Client-Side Exporters**: Instant file generation and downloads in CSV, JSON, and JSONL formats without server round-trips.
- **Dark Glassmorphic UI**: High-contrast, accessibility-focused design using curated color tokens.

---

## 🛠 Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v4
- **Icons & Assets**: Custom SVG icons and UI assets

---

## 🏃 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Copy `.env.example` to `.env.local` if your FastAPI backend runs on a non-default host or port:

```bash
cp .env.example .env.local
```

Default configuration:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📜 Available Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Starts the Next.js development server on port 3000 |
| `npm run build` | Compiles the production build |
| `npm run start` | Runs the compiled production server |
| `npm run lint` | Runs ESLint analysis |
| `npx tsc --noEmit` | Performs TypeScript static type checking |

---

## 📁 Component Structure

```
frontend/app/
├── components/
│   ├── ControlBar.tsx         # Row count selector & generation trigger
│   ├── DataScoutCard.tsx      # Recommended public datasets & synthetic plans
│   ├── DataTable.tsx          # Tabular preview with sticky headers & formatting
│   ├── EmptyState.tsx         # Engaging zero-data state with suggested prompts
│   ├── ExportBar.tsx          # CSV / JSON / JSONL client download handlers
│   ├── Header.tsx             # Studio branding & external repository links
│   ├── LoadingSkeleton.tsx    # Animated shimmer placeholder while generating
│   ├── PromptInput.tsx        # Textarea with hotkeys & example prompts
│   └── Toast.tsx              # Transient notification alert system
├── lib/
│   └── api.ts                 # Typed fetch client connecting to FastAPI backend
├── layout.tsx                 # Root HTML shell & viewport metadata
├── page.tsx                   # Main studio view orchestrating state
└── globals.css                # Global Tailwind CSS definitions
```
