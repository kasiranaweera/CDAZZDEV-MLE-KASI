<div align="center">

# Task 2 — Generative AI: Mental Health Triage Fine-Tuning Pipeline

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/13Nsr9-NEXRNUgtAS5BncQJB5FB2Dmg7s?usp=sharing)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/🤗%20Model-mental--health--triage--phi3--qlora-yellow)](https://huggingface.co/kasi-ranaweera/mental-health-triage-phi3-qlora)
[![W&B](https://img.shields.io/badge/W%26B-Training%20Run-orange)](https://wandb.ai/kasi-ranaweera/mental-health-triage-finetune)

</div>

---

## Overview

A complete QLoRA fine-tuning pipeline that adapts Phi-3-mini-4k-instruct for structured mental health triage — given a person's self-described emotional state, the model classifies severity, concern type, recommended action, risk flags, and generates an empathetic opening and follow-up question, all in validated JSON.

---

## Use Case

**Input:** A person's self-described emotional or psychological state (free-text).

**Output (structured JSON):**
```json
{
  "severity": "crisis | high | moderate | low",
  "concern_type": "...",
  "recommended_action": "...",
  "risk_flags": ["..."],
  "empathetic_opening": "...",
  "follow_up_question": "..."
}
```

**Correct response:** All fields present, severity matches described symptoms, recommendations align with clinical protocols (Columbia Protocol, PHQ-9). **Incorrect:** Missing fields, misclassified severity, or fabricated clinical terms (hallucination).

---

## Results

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-----------|------------|-------|
| ROUGE-L | 0.3494 | 0.3899 | **+0.0405** |
| BERTScore F1 | 0.8742 | 0.8931 | **+0.0189** |
| Hallucination Rate | — | **10.0%** | — |

---

## Training Configuration

| Parameter | Value | Justification |
|-----------|-------|--------------|
| Student model | `Phi-3-mini-4k-instruct` | 3.8B params fits T4 VRAM under 4-bit quant; strong instruction-following baseline |
| Teacher model | `Groq llama-3.3-70b-versatile` (primary); `openai/gpt-oss-120b` (fallback) | Fundamentally different from student — avoids circular training signal |
| Quantization | 4-bit NF4, double quantization | Best bits-per-quality ratio; double quant reduces memory further |
| LoRA rank (r) | 16 | Midpoint between capacity (r=32, higher VRAM) and speed (r=8, insufficient for clinical vocab) |
| LoRA alpha | 32 | 2× ratio — empirically validated convention for stronger adapter influence |
| Target modules | All 7 projection modules | Covers both attention and MLP for full domain adaptation |
| Learning rate | 2e-4 | Empirically validated for QLoRA regimes |
| LR scheduler | cosine | Prevents late-epoch format drift |
| Batch size | 2 | T4 VRAM (15 GB) constraint |
| Gradient accumulation | 8 steps | Simulates effective batch size of 16 |
| Epochs | 3 | Val loss decreases across all 3 — see W&B run |
| Max sequence length | 512 | Covers all triage examples with headroom |

---

## Dataset

| Split | Size | Share |
|-------|------|-------|
| Train | 113 | 80% |
| Validation | 14 | 10% |
| Test | 15 | 10% |
| **Total** | **142** | — |

- **Diversity:** 4 severity levels (crisis, high, moderate, low) × 12 concern types × varied demographics
- **Format:** JSONL, Phi-3 chat template (`system` / `user` / `assistant` turns)
- **Teacher system prompt:** See Cell 7 of the notebook

---


## Fine-Tuned Model

🤗 **Hugging Face Hub:** [kasi-ranaweera/mental-health-triage-phi3-qlora](https://huggingface.co/kasi-ranaweera/mental-health-triage-phi3-qlora)

Merged model (LoRA adapters merged into base weights via `merge_and_unload()`) — ready for direct inference without PEFT.

---

## W&B Training Run

📊 [View training dashboard](https://wandb.ai/kasi-ranaweera/mental-health-triage-finetune) — training loss, validation loss per epoch, and gradient norms.

---

## RAG Fallback Layer

When the fine-tuned model's perplexity-normalised confidence falls below **0.65**, the system retrieves relevant context from a ChromaDB vector store (10 clinical reference documents, embedded with `all-MiniLM-L6-v2`) and re-queries the model with the augmented prompt.

A concrete before/after example is included in **Cell 30** of the notebook.

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Fine-tuning | TRL `SFTTrainer` · PEFT `LoraConfig` |
| Quantization | BitsAndBytes (4-bit NF4) |
| Base model | Hugging Face `transformers` |
| Evaluation | `rouge-score` · `bert-score` |
| RAG | ChromaDB · `sentence-transformers` |
| Experiment tracking | Weights & Biases |
| Teacher inference | Groq SDK |

---

## Known Limitations

- Groq free-tier rate limits required 0.5s delays between generation calls — dataset generation took ~15 min
- T4 VRAM (15 GB) constrained batch size to 2; gradient accumulation compensates
- Phi-3-mini tokeniser treats JSON as multi-token sequences — ROUGE-L is noisier than BERTScore for this task
- Hallucination labels applied by rule-based logical checks, not clinical expert review

---

← [Back to root README](../README.md)