---
title: VoxDoc
emoji: 🎙️
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.32.0
python_version: '3.12'
app_file: app.py
pinned: false
preload_from_hub:
  - Qwen/Qwen3-4B-Instruct-2507
  - intfloat/multilingual-e5-small onnx/model.onnx,tokenizer.json
  - Xenova/ms-marco-MiniLM-L-6-v2 onnx/model.onnx,tokenizer.json
  - Systran/faster-whisper-small
  - Systran/faster-whisper-medium
  - facebook/nllb-200-distilled-600M
---

# VoxDoc

**The Voice-Native Interrogation Agent & Compounding Memory Runtime.**

Styled in a **clean white theme with forest green buttons and accent lines**, fully responsive for all screen sizes from mobile to ultra-wide wall displays. VoxDoc unites the four breakthrough paradigms into one unified startup platform:
- **🎙️ Wispr Flow Voice Velocity**: Frictionless oral interface. Speak at 3x typing speed with zero-latency turn-taking, verbal filler polish, and interruptible Piper audio synthesis.
- **⚔️ Proto Builder Sparring**: Move from passive reading to active document interrogation. Stress-test edge cases, find ambiguities, and challenge contractual policies.
- **🧠 Memorable Compounding Procedural Memory**: Agents accumulate verified procedural graph edges (`MemoryNode` & `MemoryEdge`) instead of wiping clean every session. Future agents compose pre-verified procedures 10x faster.
- **⚡ RightNow AI Sub-200ms Inference**: Open-weight inference with automatic prompt caching and BYOK flexibility.

Choose **Try the sample**, click **Start talking**, and ask: “How many days of paid leave do I get?” Hear the reply and inspect the source beside it. Upload a PDF, PNG/JPG/WebP image, text file or Markdown document up to 5 MB.

Choose **हिन्दी · Hindi** to ask and hear replies in Hindi. The demo uses English documents; Hindi questions are translated for document search. Voice is turn-taking, with interruptible playback.

After uploading, switch between **💬 Standard Q&A**, **⚔️ Proto Sparring**, and **🧠 Memorable Graph** to direct the intelligence mode. Check the imported text and extraction warnings. Tesseract reads scanned pages with English/Hindi language packs. Unreliable pages are rejected; OCR warnings ask you to verify important facts. Handwriting, blurred scans and table structure are not guaranteed. The demo supports at most 100 PDF pages, 20 OCR pages per upload and 12 megapixels per image.

## Built with open models

Qwen3-4B-Instruct-2507 answers on ZeroGPU. Whisper small transcribes English and medium transcribes Hindi. NLLB translates questions and cited replies and Piper generates English and Hindi audio on CPU. E5 embeddings, BM25 search, and a MiniLM reranker select document evidence on CPU. Overview questions use a separate coverage route. Answers require valid citations and exact source quotes. No paid inference API is used.

Each browser gets a separate temporary workspace. Use non-sensitive files; records can disappear on restart. Raw recordings are deleted after transcription. The Northstar handbook and Aster evaluation reference are fictional.

Free hosting has daily quotas and shared queues. Open this canonical Space page and sign in for your account's quota. The target is ten independent visitors with queued inference, not ten simultaneous real-time calls.

## Author & Contact

Developed by **Aravindhan**:
- **GitHub**: [@Aravindh-dev12](https://github.com/Aravindh-dev12)
- **Hugging Face**: [@Aravindhan11](https://huggingface.co/Aravindhan11)
- **Source Code**: [https://github.com/Aravindh-dev12/Voxdoc](https://github.com/Aravindh-dev12/Voxdoc)
- **Email**: [aravindh1653@gmail.com](mailto:aravindh1653@gmail.com)

## Licenses

React, FastAPI and faster-whisper are MIT; Qwen weights are Apache-2.0; Piper's engine is GPL-3.0. Voices have separate notices. The Hindi Pratham voice's dataset is CC-BY-NC-SA-4.0, restricting commercial use. This is a noncommercial portfolio demonstration, not a commercially licensed voice service. Model weights are downloaded from their publishers and are excluded from the source bundle.
