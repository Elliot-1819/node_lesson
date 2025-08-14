Goal: A full pipeline to run automatically all of the files in the neon db to then transform the file into fun and easy to learn content to put into lesson template for my interactive lessons 

Simple start and simple testing 

# Check list
[] Build the architehture/infrastructures, dependacies and the working code that will make everything work perfectly
[] Build step by step in the pipeline while testing after everystep
[] Ensure true testing is working
[] Full trial runs with example data 
[] Optimisation

# Lesson templates: 

Definition → 3rd Person (Tim)

Template: 3rd Person with Tim
Interactive Component: Follow Tim discovering the concept
Learning Content Style: "Tim is learning about [term]. Watch as he discovers what it means..."
Conclusion Content Style: "Tim now understands [term]. You can apply this same understanding when..."

Mechanism → 2nd Person View

Template: 2nd Person View
Interactive Component: Guided walkthrough - "You control each step to see how it works"
Learning Content Style: "You're about to see exactly how [process] works step by step..."
Conclusion Content Style: "Now you understand how this works. When you see [trigger], you'll know [outcome] follows..."

Procedure → Decision Tree

Template: Decision Tree
Interactive Component: Step-by-step branching choices
Learning Content Style: "Each trading procedure has decision points. Choose your path..."
Conclusion Content Style: "You've navigated the procedure. Remember: if [condition], then [action]..."

Comparison → Game

Template: Game
Interactive Component: Scenario simulation with competing options
Learning Content Style: "Two approaches compete. Test both and see which wins..."
Conclusion Content Style: "You've tested both. Choose [A] when... Choose [B] when..."

Example → 3rd Person (Tim) 

Template: 3rd Person with Tim
Interactive Component: Follow Tim through real trading scenarios
Learning Content Style: "Tim just encountered this exact situation. See what happens..."
Conclusion Content Style: "Tim's experience shows you [key insight]. Watch for this pattern when..."

# Lesson Builder Pipeline — Implementation Checklist

## ⬜ Step 1 — Fetch Work (Flatten pages → sections)
- [ ] Read pages from `lesson_dirty` (Neon)
- [ ] Parse `page_content` JSON array per page and emit one record per section
- [ ] Output artifact `.out/step1_sections.json` with fields:
  - `section_id` (computed = `page_id * 10000 + section_serial_id`),
  - `page_id`, `page_title`, `title`, `text`, `topic`, `keywords`
- [ ] Recommended dev flow: process one page at a time (use `--limit 1`)

## ⬜ Step 2 — Normalize & Split
- [ ] Write normalization function (punctuation, lowercase)
- [ ] Implement sentence splitting
- [ ] Drop exact duplicates (order-preserving)
  - Note: Near-duplicate detection is intentionally deferred to a later phase if needed; duplicates are rare and exact dedupe keeps this step simple and fast.

## ⬜ Step 3 — Auto-label (Rules → Tiny Model)
- [ ] Write regex/rule patterns for each info-type (Definition, Mechanism, Procedure, Comparison, Example)
- [ ] Implement rules engine
- [ ] Add fallback classifier call (tiny model ≤50M params)
- [ ] Store `{text, type, prob, rule_hit}` for each sentence
Definition: Follows format "X is Y"
Mechanism: Contains cause→effect chains
Procedure: Contains numbered lists or action sequences
Comparison: Contains multiple options being analyzed
Example: Contains specific scenarios or concrete instances

## ⬜ Step 4 — Score Sentences
- [ ] Implement TF-IDF scoring
- [ ] Add entity/number boost
- [ ] Add rule_hit bonus + model probability
- [ ] Apply length penalty (>40 tokens)
- [ ] Calculate final score

## ⬜ Step 5 — Select Minimal Teaching Set
- [ ] Group into `teaching_units[]`
- [ ] select only the ones with high enough performance
- [ ] Skip section if <2 useful sentences


## ⬜ Step 6 — Decide Step Count
- [ ] If ≥3 distinct types → 2 steps (Def+Mech / Example+Risk)
- [ ] Else 1 step

## ⬜ Step 7 — Fill Interactive Templates
- [ ] Create template definitions with slots for each info-type
- [ ] Map teaching_units → template slots
- [ ] Validate slot completeness

## ⬜ Step 8 — Micro-rewrite (Style Only)
- [ ] Implement LLM call (small model, temp ≤ 0.3)
- [ ] Lock facts — no new data generated
- [ ] Convert to 2nd-person conversational tone

## ⬜ Step 9 — Determine Difficulty
- [ ] Calculate keyword density (% domain vocab tokens)
- [ ] If density > threshold → send metadata to small LLM to guess difficulty
- [ ] Else fallback to rules:
  - Def/Example → Beginner
  - + Mechanism/Comparison → Intermediate
  - + Procedure/Risk w/ numbers → Master

## ⬜ Step 10 — Quality Gates
- [ ] Check for empty slots
- [ ] Check for contradictions
- [ ] Ensure reading level ≤ Grade 9
- [ ] Enforce max tokens per step
- [ ] Drop steps that fail QC

## step 10.5 
- [ ] add embedding model 

## ⬜ Step 11 — Persist
- [ ] Define `lesson` DB schema:
  ```sql
  lesson {
    lesson_id SERIAL PRIMARY KEY,
    section_id INT,
    step_count INT,
    steps JSONB,
    info_types TEXT[],
    keywords TEXT[],
    difficulty TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT now(),
    version INT


## Architecture 
Goal- build scalable architecture that is clean and easy to read

Project root
```
.
├── src/                      # Application code
│   ├── main.py               # CLI entry / step orchestrator (per-step)
│   ├── config/
│   │   ├── settings.py       # Env + thresholds (reads .env)
│   │   └── templates.json    # Interactive template definitions
│   ├── db/
│   │   ├── models.py         # Dataclass models
│   │   ├── schema.sql        # Future DB DDL (reference)
│   │   └── db_utils.py       # DB fetch helpers (flatten lesson_dirty)
│   ├── pipeline/
│   │   ├── step1_fetch.py
│   │   ├── step2_normalize.py
│   │   ├── step3_label.py
│   │   ├── step4_score.py
│   │   ├── step5_select.py
│   │   ├── step6_steps.py
│   │   ├── step7_templates.py
│   │   ├── step8_rewrite.py
│   │   ├── step9_difficulty.py
│   │   ├── step10_quality.py
│   │   └── step11_persist.py
│   ├── services/
│   │   ├── llm_service.py    # Local Qwen wrapper
│   │   ├── classifier.py     # Rules-first classifier
│   │   └── keyword_service.py
│   └── utils/
│       ├── text_clean.py
│       ├── scoring.py
│       └── logging_utils.py
├── tests/
│   ├── test_scaffold.py
│   └── test_step2_normalize.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                      # Environment variables
└── README.md
```

### Dev flow (page-by-page, section-by-section)
- Fetch one page and flatten its sections:
  - `python -m src.main step1 --limit 1 --out-path .out/step1_sections.json`
- Pick a `section_id` from that file and process it:
  - `python -m src.main step2 --in-path .out/step1_sections.json --section-id <ID> --out-path .out/step2_sentences.json`
  - Repeat Step 2 for each section in the page, then move to the next page.


# true testing (main:pytest)
Goal: Ensure each step works by testing errors, format, output and performance for every step and seeing the results to see where it goes wrong or where does the performance goes lower.

+ add alerts for everydecision my code makes
1. Unit Tests (Core Logic)

Purpose: Instant feedback when you break rules, scoring, or template filling.
Coverage:

Regex/rule detection for info-types

Scoring function math

Template slot validator

Why keep: These fail fast and pinpoint exactly where the bug is.

2. Golden Set Tests (Regression Guard)

Purpose: Detect if outputs unexpectedly change for key examples.
Coverage:

50 curated sections → locked final lesson JSONs

Why keep: Catches silent regressions anywhere in the pipeline without testing every step individually.

3. Integration Tests (DB + End-to-End)

Purpose: Ensure the whole pipeline actually works when wired together with the DB.
Coverage:

Fetch → Process → Persist → Query flow

Checks schema matches

Why keep: Confirms your “happy path” works in production-like conditions.

4. LLM Guard Tests (Safety & Schema)

Purpose: Make sure LLM rewrites don’t introduce wrong facts or break format.
Coverage:

Schema validation with pydantic

Fact-check: all facts in output exist in original text

Why keep: Protects your content quality and avoids subtle trust issues.