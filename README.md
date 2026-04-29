# 🧠 NLP Toolkit

A sleek, dark-themed web application that brings together 4 powerful NLP tools in one place — all running locally on your machine with state-of-the-art open-source Transformer models.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-black?style=for-the-badge&logo=flask)
![Transformers](https://img.shields.io/badge/🤗_Transformers-4.0+-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

| Tool | Description | Model |
|------|-------------|-------|
| 🔄 **Paraphraser** | Generate 3 diverse rephrased versions of any text | `humarin/chatgpt_paraphraser_on_T5_base` |
| ✍️ **Humanizer** | Rewrite AI-generated text to sound natural & human-like | Paraphraser + rule-based post-processing |
| ✓ **Grammar Fix** | Correct spelling, punctuation & sentence structure | `pszemraj/flan-t5-large-grammar-synthesis` |
| ☰ **Summarizer** | Condense long articles into concise summaries | `facebook/bart-large-cnn` |

- 🎨 **Modern Dark UI** — responsive sidebar layout with real-time feedback
- ⚡ **Lazy Loading** — models download on first use; Flask starts instantly
- 🖥️ **CPU & GPU Support** — auto-detects CUDA; falls back to CPU
- ⌨️ **Keyboard Shortcuts** — `Ctrl + Enter` to submit
- 📋 **One-Click Copy** — copy any result instantly

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/mfaaizi/NLP_Toolkit_beginner.git
cd NLP_Toolkit_beginner
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```

Open your browser and go to **http://localhost:5000**

> **Note:** On first use, each tool will download its model (~1.5 GB total) from Hugging Face. This is a one-time download.

---

## 📸 Screenshots

<img width="1918" height="878" alt="image" src="https://github.com/user-attachments/assets/ffbc3bae-08fd-4acc-b41e-fe25511d969e" />

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python) |
| ML / NLP | Hugging Face Transformers, PyTorch |
| Frontend | Vanilla HTML5, CSS3, JavaScript |
| Styling | Custom dark theme with CSS Grid & Flexbox |

---

## 📡 API Endpoints

All endpoints accept `POST` requests with JSON body `{"text": "your input here"}`.

| Endpoint | Input | Output |
|----------|-------|--------|
| `/paraphrase` | Any text | `{ "results": ["v1", "v2", "v3"] }` |
| `/humanize` | AI-generated text | `{ "result": "humanized text" }` |
| `/grammar` | Text with errors | `{ "result": "corrected text" }` |
| `/summarize` | Long text / article | `{ "result": "summary" }` |

### Example (cURL)
```bash
curl -X POST http://localhost:5000/paraphrase \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
```

---

## 📁 Project Structure
nlp-toolkit/
│
├── app.py                  # Flask server + model inference logic
├── requirements.txt        # Python dependencies
│
├── templates/
│   └── index.html          # Single-page application UI
│
└── static/
├── css/
│   └── style.css       # Dark theme, responsive layout
└── js/
└── main.js         # Frontend interactivity & API calls

---

## ⚙️ Configuration

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | Hugging Face token for higher rate limits | None |
| `TRANSFORMERS_CACHE` | Custom model cache directory | `~/.cache/huggingface/` |

```bash
# Windows PowerShell
$env:HF_TOKEN = "hf_your_token_here"

# Linux / macOS
export HF_TOKEN="hf_your_token_here"
```

### Windows Symlink Warning
If you see a warning about symlinks on Windows, you can safely ignore it. To suppress it:
```powershell
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
```
Or enable **Developer Mode** in Windows Settings for native symlink support.

---

## 💻 System Requirements

| Spec | Minimum | Recommended |
|------|---------|-------------|
| RAM | 8 GB | 16 GB+ |
| Storage | 5 GB (for models) | 5 GB+ |
| GPU | Optional | NVIDIA GPU with 4 GB+ VRAM |
| OS | Windows 10 / macOS / Linux | Any modern OS |

---

## 🐛 Troubleshooting

### "Running scripts is disabled on this system" (Windows)
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Out of Memory / Slow on CPU
- Close other applications to free RAM
- Use shorter input text (< 500 words)
- Restart the app to clear cached models

### Model Download Stuck
- Check your internet connection
- Set a Hugging Face token if you hit rate limits
- Models are cached at `C:\Users\<You>\.cache\huggingface\` (Windows) or `~/.cache/huggingface/` (Linux/macOS)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Hugging Face](https://huggingface.co) for the Transformers library & model hub
- [humarin](https://huggingface.co/humarin) for the ChatGPT Paraphraser model
- [pszemraj](https://huggingface.co/pszemraj) for the FLAN-T5 Grammar model
- [Facebook AI](https://ai.facebook.com) for BART-large-CNN

---
