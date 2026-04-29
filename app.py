import os
import re
import random
import torch
from flask import Flask, render_template, request, jsonify
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM, 
    pipeline,
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ─── Device & Dtype ─────────────────────────────────────────────────────────
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
print(f"[INFO] Using device: {DEVICE} | dtype: {TORCH_DTYPE}")

# ─── Model Cache ────────────────────────────────────────────────────────────
_MODEL_CACHE = {}

MODEL_CONFIG = {
    "paraphraser": {
        "name": "humarin/chatgpt_paraphraser_on_T5_base",
        "type": "t5",
    },
    "grammar": {
        "name": "grammarly/coedit-large",
        "type": "t5",
        "prompt": "Fix grammatical errors in this sentence: {text}",
    },
    "summarizer": {
        "name": "facebook/bart-large-cnn",
        "type": "pipeline",
    },
}


def _load_t5_model(key: str):
    cfg = MODEL_CONFIG[key]
    model_name = cfg["name"]
    print(f"[LOAD] Loading {key}: {model_name} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        torch_dtype=TORCH_DTYPE,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    if not torch.cuda.is_available():
        model = model.to(DEVICE)
    _MODEL_CACHE[key] = (tokenizer, model)
    print(f"[LOAD] {key} ready.")
    return _MODEL_CACHE[key]


def _load_pipeline_model(key: str):
    cfg = MODEL_CONFIG[key]
    model_name = cfg["name"]
    print(f"[LOAD] Loading {key}: {model_name} ...")

    # Let pipeline auto-detect task from model to avoid "Unknown task" errors
    pipe = pipeline(
        model=model_name,
        tokenizer=model_name,
        device=0 if torch.cuda.is_available() else -1,
        torch_dtype=TORCH_DTYPE,
    )
    _MODEL_CACHE[key] = pipe
    print(f"[LOAD] {key} ready.")
    return _MODEL_CACHE[key]


def get_model(key: str):
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    cfg = MODEL_CONFIG[key]
    if cfg["type"] == "t5":
        return _load_t5_model(key)
    elif cfg["type"] == "pipeline":
        return _load_pipeline_model(key)
    else:
        raise ValueError(f"Unknown model type for {key}")


# ─── Humanizer Post-processing ──────────────────────────────────────────────
_CONTRACTIONS = [
    (r'\bdo not\b', "don't"),
    (r'\bdoes not\b', "doesn't"),
    (r'\bdid not\b', "didn't"),
    (r'\bis not\b', "isn't"),
    (r'\bare not\b', "aren't"),
    (r'\bwas not\b', "wasn't"),
    (r'\bwere not\b', "weren't"),
    (r'\bhave not\b', "haven't"),
    (r'\bhas not\b', "hasn't"),
    (r'\bhad not\b', "hadn't"),
    (r'\bwill not\b', "won't"),
    (r'\bwould not\b', "wouldn't"),
    (r'\bcould not\b', "couldn't"),
    (r'\bshould not\b', "shouldn't"),
    (r'\bcannot\b', "can't"),
    (r'\bI am\b', "I'm"),
    (r'\byou are\b', "you're"),
    (r'\bthey are\b', "they're"),
    (r'\bit is\b', "it's"),
    (r'\bthat is\b', "that's"),
    (r'\bthere is\b', "there's"),
]

_FORMAL_TO_CASUAL = {
    r'\butilize\b': 'use',
    r'\butilizes\b': 'uses',
    r'\bnevertheless\b': 'still',
    r'\bfurthermore\b': 'also',
    r'\bhowever\b': 'but',
    r'\btherefore\b': 'so',
    r'\badditionally\b': 'plus',
    r'\bconsequently\b': 'as a result',
    r'\bmoreover\b': 'also',
    r'\bthus\b': 'so',
}

_FILLERS = ["So, ", "Well, ", "You know, ", "Honestly, ", "Look, "]


def _humanize_post_process(text: str) -> str:
    for pattern, replacement in _CONTRACTIONS:
        if random.random() > 0.25:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    processed = []
    for i, sent in enumerate(sentences):
        if len(sent) > 25 and i > 0 and random.random() > 0.88:
            sent = random.choice(_FILLERS) + sent[0].lower() + sent[1:]
        processed.append(sent)
    text = ' '.join(processed)
    for pattern, replacement in _FORMAL_TO_CASUAL.items():
        if random.random() > 0.4:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/paraphrase", methods=["POST"])
def paraphrase():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    try:
        tokenizer, model = get_model("paraphraser")
        model.eval()

        inputs = tokenizer(
            f"paraphrase: {text}",
            return_tensors="pt",
            padding="longest",
            max_length=512,
            truncation=True,
        )
        if torch.cuda.is_available():
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                num_beams=5,
                num_return_sequences=3,
                no_repeat_ngram_size=2,
                repetition_penalty=2.5,
                early_stopping=True,
                max_length=512,
            )

        results = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        seen = set()
        unique = [x for x in results if not (x in seen or seen.add(x))]
        return jsonify({"results": unique})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/humanize", methods=["POST"])
def humanize():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    try:
        tokenizer, model = get_model("paraphraser")
        model.eval()

        inputs = tokenizer(
            f"humanize: {text}",
            return_tensors="pt",
            padding="longest",
            max_length=512,
            truncation=True,
        )
        if torch.cuda.is_available():
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                do_sample=True,
                temperature=0.92,
                top_p=0.95,
                top_k=60,
                repetition_penalty=1.15,
                no_repeat_ngram_size=2,
                max_length=512,
                num_return_sequences=1,
            )

        result = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        result = _humanize_post_process(result)
        return jsonify({"result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/grammar", methods=["POST"])
def grammar():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    try:
        tokenizer, model = get_model("grammar")
        model.eval()

        # Use the proper prompt format for this model
        prompt = MODEL_CONFIG["grammar"]["prompt"].format(text=text)

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            padding="longest",
            max_length=512,
            truncation=True,
        )
        if torch.cuda.is_available():
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=512,
                num_beams=4,
                early_stopping=True,
            )

        result = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return jsonify({"result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    try:
        summarizer = get_model("summarizer")
        words = text.split()
        if len(words) > 900:
            chunks = []
            for i in range(0, len(words), 900):
                chunk = " ".join(words[i:i+900])
                out = summarizer(
                    chunk,
                    max_length=130,
                    min_length=25,
                    do_sample=False,
                )
                chunks.append(out[0]["summary_text"])
            result = " ".join(chunks)
        else:
            out = summarizer(
                text,
                max_length=130,
                min_length=25,
                do_sample=False,
            )
            result = out[0]["summary_text"]

        return jsonify({"result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)