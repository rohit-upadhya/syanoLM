# Devanagari / Indic Tokenization — paper collection

Papers on tokenizing Devanagari-script and Indic languages for LLMs — fertility, the
"tokenizer tax", morphology-aware BPE, and vocab/embedding transfer. Downloaded 2026-08-23.

Directly relevant to this project: your `SmoLLM-109M-base` tokenizer has **0% Devanagari
coverage** and **7.67 tok/word** on Nepali (measured). These papers explain why that happens
and how a custom Nepali BPE fixes it.

## ⭐ Start here (most relevant)
| File | arXiv | Why it matters |
|---|---|---|
| `Nepali_tokenization_effects_perplexity_finetuning.pdf` | [2404.18071](https://arxiv.org/abs/2404.18071) | **Nepali-specific.** Tokenization choices → perplexity & fine-tuning for Nepali LMs. Closest to your exact task. |
| `Tokenizer_Tax_Indian_languages_crosslingual_cost.pdf` | [2607.24276](https://arxiv.org/abs/2607.24276) | Quantifies & *explains* the cross-lingual cost of subword tokenization for Indian languages (the ~6–13× tax). |
| `Evaluating_tokenizer_performance_official_Indian_languages.pdf` | [2411.12240](https://arxiv.org/abs/2411.12240) | Benchmarks tokenizer fertility across official Indian languages incl. Nepali — good baselines to compare your BPE against. |
| `HindiLLM_Devanagari_BPE_tokenizer.pdf` | [2412.20357](https://arxiv.org/abs/2412.20357) | Builds a custom byte-level Devanagari BPE for Hindi to cut fertility — near-identical recipe to yours. |

## Tokenizer design & morphology
| File | arXiv | Notes |
|---|---|---|
| `BHARATI_morphology_aware_tokenizers_Indic_fertility.pdf` | [2607.23319](https://arxiv.org/abs/2607.23319) | Morphology-aware SentencePiece BPE for Indian languages + subword fertility analysis (sandhi/agglutination). |
| `MorphBPE_morpho_aware_tokenizer.pdf` | [2502.00894](https://arxiv.org/abs/2502.00894) | Morpho-aware BPE + two morphology eval metrics (consistency F1, morphological edit distance). |
| `Multilingual_tokenization_lens_of_Indian_languages.pdf` | [2506.17789](https://arxiv.org/abs/2506.17789) | Tokenizer evaluation methodology through Indian-language morphology. |
| `BrahmicTokenizer_131K_Indic_dropin_o200k.pdf` | [2605.29379](https://arxiv.org/abs/2605.29379) | Indic-capable 131K vocab drop-in for o200k_base — a "reuse an Indic tokenizer" alternative. |

## The "tokenizer tax" / fairness
| File | arXiv | Notes |
|---|---|---|
| `Token_Tax_systematic_bias_multilingual_tokenization.pdf` | [2509.05486](https://arxiv.org/abs/2509.05486) | Systematic bias in multilingual tokenization; defines fertility & parity metrics. |

## Vocab extension / embedding transfer (relevant if you ever transplant instead of retrain)
| File | arXiv | Notes |
|---|---|---|
| `Token_embedding_init_for_vocab_extension.pdf` | [2608.03494](https://arxiv.org/abs/2608.03494) | How to initialize new token embeddings when swapping/extending a vocab — the smart-init methods (WECHSEL/FOCUS family) discussed earlier. |

## Takeaways for your build
- **Fertility is the metric.** Report tokens/word on held-out Nepali; target ≤1.5 (yours is 7.67 now).
- **Byte-level BPE needs Devanagari in training** or every char → 3 byte tokens. Train the tokenizer *on Nepali*.
- **Normalize first** (NFC + matra/nukta/ZW) — see 2404.18071.
- Consider **morphology-aware** variants (BHARATI/MorphBPE) if plain BPE fertility stalls.
