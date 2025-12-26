#!/bin/bash

# Marker Performance Optimization Guide

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║         ⚡ MARKER PERFORMANCE OPTIMIZATION GUIDE                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Why is it slow on the first run?
─────────────────────────────────────────────────────────────────────────
Marker loads large ML models (~2-5GB):
  • OCR models (Document understanding)
  • Layout analysis (Page structure)
  • Text detection (Word localization)
  • Table recognition (Structured data)

Subsequent runs are MUCH faster (cached models).

═══════════════════════════════════════════════════════════════════════════════

⚡ OPTIMIZATION STRATEGIES
─────────────────────────────────────────────────────────────────────────

1. DISABLE LLM FOR FASTER CONVERSION (Recommended for first use)
   ✓ Set "Use LLM" toggle to OFF in the web UI
   ✓ Direct marker processing only (~30-60 seconds per page)
   ✗ With LLM: additional 2-5 minutes for Ollama processing

2. USE APPROPRIATE FILE SIZE
   ✓ Single page documents: ~15-30 seconds
   ✓ 5-10 page documents: ~1-2 minutes
   ✗ Large documents (50+ pages): 10-30 minutes (use batch splitting)

3. ENABLE GPU ACCELERATION (macOS M1/M2/M3)
   Currently: Using CPU via MPS backend
   
   To improve: Ensure PyTorch uses GPU properly
   Run: python -c "import torch; print(torch.backends.mps.is_available())"

4. BATCH PROCESSING TIP
   Instead of converting one large file:
   • Split PDF into smaller chunks
   • Convert in parallel
   • 3-5x faster overall

═══════════════════════════════════════════════════════════════════════════════

📊 EXPECTED PROCESSING TIMES (Rough estimates)
─────────────────────────────────────────────────────────────────────────

Document Size   | Without LLM | With LLM (Ollama)
──────────────────────────────────────────────────
1 page          | 15-30 sec   | 1-2 min
5 pages         | 45-90 sec   | 3-5 min
10 pages        | 1-2 min     | 5-10 min
20 pages        | 2-4 min     | 10-20 min
50+ pages       | 5-10 min    | 20+ min

First run is ALWAYS slower (model loading)
Subsequent runs: 30-40% faster (cached models)

═══════════════════════════════════════════════════════════════════════════════

🎯 FASTEST SETUP (For immediate results)
─────────────────────────────────────────────────────────────────────────

1. Upload a small PDF (1-2 pages)
2. Leave "Use LLM" unchecked
3. Select output format: Markdown (fastest)
4. Click Convert
5. First conversion: ~30 seconds
6. Download results

═══════════════════════════════════════════════════════════════════════════════

🔧 ADVANCED OPTIMIZATION (For developers)
─────────────────────────────────────────────────────────────────────────

To speed up marker:

Option A: Use lightweight models
  marker \
    --batch_multiplier 0.5 \  # Use smaller batch size
    --device cpu              # Or cuda if available

Option B: Skip certain processing
  marker \
    --skip_images             # Don't extract images
    --skip_layout             # Don't analyze layout
    input.pdf

Option C: Parallel processing
  # Process multiple files at once
  marker input_dir/ --parallel

═══════════════════════════════════════════════════════════════════════════════

💡 TIPS FOR FASTER RESULTS
─────────────────────────────────────────────────────────────────────────

✅ DO:
  • Start with small test documents
  • Disable LLM for initial processing
  • Use Markdown format (fastest output)
  • Process 1-5 page documents
  • Run multiple conversions (caching helps)

❌ DON'T:
  • Process 100-page documents first
  • Enable LLM for simple documents
  • Convert high-quality image-only PDFs (slow OCR)
  • Process while system is under load

═══════════════════════════════════════════════════════════════════════════════

📈 MONITORING PROGRESS
─────────────────────────────────────────────────────────────────────────

Check what's happening:
  1. Watch the job status in web UI
  2. Check system activity:
     • High CPU = Model inference
     • High memory = Loading models
     • I/O activity = Reading/writing files

═══════════════════════════════════════════════════════════════════════════════

🚀 YOUR SETUP:
─────────────────────────────────────────────────────────────────────────

Current Configuration:
  • Marker: ✅ Ready
  • Backend: ✅ Running on port 8000
  • Frontend: ✅ Running on port 3000
  • Ollama: ✅ Running (gemma2:2b model)
  • LLM: Optional (disable for speed)

Recommended first test:
  → Upload a 2-3 page PDF
  → Uncheck "Use LLM"
  → Select Markdown format
  → Click Convert
  → Wait 30-60 seconds

═══════════════════════════════════════════════════════════════════════════════

✅ READY TO OPTIMIZE!

If conversion is still slow after these tips, check:
  1. System memory available (need 8GB+ free)
  2. Available disk space (need 5GB+ free)
  3. CPU usage: top -bn1 | head -20
  4. Memory usage: vm_stat

═══════════════════════════════════════════════════════════════════════════════

EOF
