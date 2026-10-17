# Stage 35 Prompt and Decoding Protocol

## 1. Prompt Specifications
- Parameterized template SHA-256: `38d1558231846bdfa67c617b07db27d532b851adbc0e2a537f002b489d70034a`.
- Literal prompts with restricted text isolated in external write-once protected storage.

## 2. Decoding Settings
- **Gemini:** `temperature=0.0`, `top_p=0.95`, `seed=42`.
- **mT5:** `num_beams=4`, `max_length=256`, `no_repeat_ngram_size=3`.
- **mBART:** `forced_bos_token=si_LK`, `num_beams=4`, `max_length=256`.
