# Agentic Report Swarm

**Agentic Report Swarm** adalah sistem *Agentic AI* berbasis Python yang menggunakan konsep **SuperAgent** untuk merencanakan, membuat, dan mengorkestrasi **swarm** berisi beberapa agen LLM spesialis (ResearchAgent, TrendsAgent, InsightsAgent, WriterAgent).  
Melalui satu prompt sederhana seperti:

> "Buatkan laporan market analysis Q4 untuk e-commerce fashion di Indonesia."

Sistem ini:
1. Membuat *Plan* otomatis  
2. Menjalankan agen-agen paralel  
3. Menggabungkan hasil  
4. Menghasilkan laporan lengkap dalam format Markdown  

Proyek ini dirancang sebagai **MVP** yang solid untuk menunjukkan pola *Agentic Architecture* modern di portofolio profesional.

---

## 🚀 Fitur Utama

- **SuperAgent** → memahami prompt, membuat rencana kerja, mengatur eksekusi
- **Multi-Agent Swarm** → ResearchAgent, TrendsAgent, InsightsAgent, WriterAgent
- **Task Planning** → sistem memecah tugas besar menjadi subtugas
- **Parallel Execution** (opsional)
- **Clean OOP Architecture** → mudah di-extend, testable, modular
- **LLM-only (OpenAI API)** → tanpa dependency data eksternal
- **CLI Interface** → jalankan dari terminal
- (Opsional) **Web UI** (FastAPI)

---

## 🧩 Arsitektur

```
User Input
     ↓
SuperAgent → Planner → Plan (SubTasks)
     ↓
 SwarmManager → spawn specialized agents
     ↓
ResearchAgent   TrendsAgent   InsightsAgent
     ↓
      WriterAgent
     ↓
Report Aggregator → Final Markdown Report
```

---

## 📦 Instalasi

### 1. Clone repo
```bash
git clone https://github.com/<your_username>/agentic-report-swarm
cd agentic-report-swarm
```

### 2. Buat virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependency
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Copy `.env.example` → `.env`
```bash
cp .env.example .env
```

Isi API key OpenAI kamu di `.env`:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxx
```

---

## ▶️ Cara Menjalankan (CLI)

```bash
python -m src.app --topic "e-commerce fashion Indonesia Q4" --length short
```

Output akan muncul sebagai file markdown di:

```
demos/example_reports/
```

---

## 🧪 Pengujian

Jalankan test unit (mock mode):

```bash
pytest -q
```

---

## 📂 Struktur Proyek

```
agentic-report-swarm/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ demos/
│  └─ example_reports/
├─ src/
│  ├─ app.py
│  └─ superagent/
│     ├─ planner.py
│     ├─ plan_schema.py
│     ├─ superagent.py
│     ├─ swarm_manager.py
│     ├─ memory.py
│     ├─ aggregator.py
│     ├─ adapters/
│     │  └─ openai_adapter.py
│     └─ agents/
│        ├─ base.py
│        ├─ research.py
│        ├─ trends.py
│        ├─ insights.py
│        └─ writer.py
└─ tests/
   ├─ test_planner.py
   └─ test_research_agent.py
```

---

## 📝 Roadmap
- [x] MVP SuperAgent + Swarm
- [ ] Add FastAPI Web UI
- [ ] Add PDF & chart generator
- [ ] Add MCP tools (FileTool, SearchTool)
- [ ] Add dynamic agent spawning
- [ ] Add Agent memory + Knowledge Base

---

## 📄 License
MIT License © 2025

---

## ⭐ Untuk Recruiter / Reviewer

Proyek ini dibuat untuk menunjukkan:
- pemahaman agentic architecture modern  
- kemampuan merancang multi-agent OOP modular  
- pengalaman menggunakan OpenAI API  
- implementasi Swarm pattern  
- kemampuan membuat sistem AI tingkat menengah yang extensible  

Terima kasih telah membaca!  
