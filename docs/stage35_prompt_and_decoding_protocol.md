# Stage 35 Prompt and Decoding Protocol

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Specification References:**
- `data/model_comparison/stage35/registry/stage35_prompt_template.json`
- `data/model_comparison/stage35/registry/stage35_decoding_config.json`
- `data/model_comparison/stage35/registry/stage35_safety_settings.json`

---

## 1. Frozen Zero-Shot Prompt Templates

### 1.1 Condition C1 (`C1_GEMINI_ZERO_SHOT`)
- **Template ID:** `S35-PROMPT-GEMINI-V1`
- **SHA-256 Digest:** `0000b7346093c8564dff0ef3eaca703986d1322ad4abbc7fc23ed03f68c15d84`
- **Prompt Structure:**
  ```text
  පහත දැක්වෙන සිංහල වාක්‍යය කුඩා ළමුන්ට පහසුවෙන් තේරුම් ගත හැකි වන පරිදි සරල කරන්න.
  අර්ථය වෙනස් නොකරන්න. නම්, දිනයන් සහ විශේෂ ස්ථාන නම් එලෙසම තබන්න.
  සරල කරන ලද වාක්‍යය පමණක් ප්‍රතිදානය කරන්න.

  මූලික වාක්‍යය: {source_text}
  සරල කළ වාක්‍යය:
  ```

### 1.2 Condition C2 (`C2_MT5_ZERO_SHOT`)
- Prefix-based instruction for mT5 sequence-to-sequence input:
  `simplify sinhala: {source_text}`

### 1.3 Condition C3 (`C3_MBART_ZERO_SHOT`)
- Direct source text conditioning with forced target language BOS token `si_LK`.

---

## 2. Frozen Decoding Parameters

| Condition | Decoding Mode | Temperature | Top-p | Beam Count | Max Tokens / Length | Early Stopping | Target BOS Token |
|---|---|---|---|---|---|---|---|
| `C0_RULE_BASELINE` | Deterministic Rules | N/A | N/A | N/A | N/A | N/A | N/A |
| `C1_GEMINI_ZERO_SHOT` | Greedy / Low Temp | 0.0 | 0.95 | N/A | 1024 | N/A | N/A |
| `C2_MT5_ZERO_SHOT` | Beam Search | N/A | N/A | 4 | 256 | True | N/A |
| `C3_MBART_ZERO_SHOT` | Beam Search | N/A | N/A | 4 | 256 | True | `si_LK` |

---

## 3. Gemini Safety Settings Dictionary
Condition C1 uses an explicit, non-default safety settings dictionary:
- `HARM_CATEGORY_HARASSMENT`: `BLOCK_MEDIUM_AND_ABOVE`
- `HARM_CATEGORY_HATE_SPEECH`: `BLOCK_MEDIUM_AND_ABOVE`
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`: `BLOCK_MEDIUM_AND_ABOVE`
- `HARM_CATEGORY_DANGEROUS_CONTENT`: `BLOCK_MEDIUM_AND_ABOVE`
- `HARM_CATEGORY_CIVIC_INTEGRITY`: `BLOCK_MEDIUM_AND_ABOVE`
