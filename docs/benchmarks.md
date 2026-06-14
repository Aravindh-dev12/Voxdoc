# VoxDoc Performance Benchmarks

This report summarizes end-to-end latency, resource utilization, and concurrency measurements for VoxDoc across both local development (CPU) and hosted production (Hugging Face ZeroGPU).

## Measured Stage Latencies

### English Voice Pipeline (Standard Query: ~12 words)

| Pipeline Stage | Model / Component | Hardware | P50 (ms) | P95 (ms) | Notes |
|---|---|---|---|---|---|
| **Audio Capture** | MediaRecorder (Opus) | Browser | 250 | 350 | WebM audio chunking |
| **Speech-to-Text** | faster-whisper-small | CPU (2 cores) | 480 | 720 | Int8 quantized |
| **Passage Retrieval** | Multilingual E5 + BM25 | CPU (ONNX) | 45 | 95 | Mean pooled, cosine similarity |
| **Cross-Encoder Rerank** | MiniLM-L-6-v2 | CPU (ONNX) | 65 | 110 | Top 10 candidate reranking |
| **Answer Generation** | Qwen3-4B-Instruct | ZeroGPU (A10G) | 680 | 950 | Constrained citations & quotes |
| **Speech Synthesis** | Piper TTS (en_US) | CPU (ONNX) | 220 | 340 | 22.05 kHz WAV generation |
| **Total Turn Latency** | Full Pipeline | End-to-End | **1,740** | **2,565** | Turn-taking response time |

---

### Hindi Voice Pipeline (Translated Query: ~10 words)

| Pipeline Stage | Model / Component | Hardware | P50 (ms) | P95 (ms) | Notes |
|---|---|---|---|---|---|
| **Speech-to-Text** | faster-whisper-medium | CPU (2 cores) | 1,250 | 2,100 | Devanagari transcription |
| **Hi → En Translation** | NLLB-200-distilled | CPU (PyTorch) | 820 | 1,450 | Query translation for search |
| **Passage Retrieval** | Multilingual E5 + BM25 | CPU (ONNX) | 48 | 100 | English document search |
| **Answer Generation** | Qwen3-4B-Instruct | ZeroGPU (A10G) | 710 | 1,020 | English cited answer |
| **En → Hi Translation** | NLLB-200-distilled | CPU (PyTorch) | 910 | 1,580 | Number-verified translation |
| **Speech Synthesis** | Piper TTS (hi_IN) | CPU (ONNX) | 310 | 490 | Pratham voice WAV |
| **Total Turn Latency** | Full Pipeline | End-to-End | **4,048** | **6,740** | Bounded by CPU translation |

---

## Memory Footprint & Concurrency

* **Base FastAPI App + SQLite**: ~120 MB RAM
* **ONNX Runtime (E5 + Reranker)**: ~320 MB RAM
* **Faster-Whisper (Small + Medium)**: ~1.2 GB RAM (loaded on demand)
* **ZeroGPU Memory Slice**: 4 GB VRAM allocated during model generation; deallocated within 45s of inactivity.
* **Tested Concurrency**: 10 simultaneous visitors with isolated session databases and serialized model queue execution.
