#!/usr/bin/env python3
"""Curate per-talk keyword lists with a cheap model, cached in keywords.json.

Slide titles are not keywords. A .tex file yields frame titles like
"Ex 1: Lawvere theories", "How this talk will go", or "Minor difficulty during
talk" -- presentational scaffolding, rhetoric, and navigation mixed in with the
actual subjects. This script hands each talk's title and full ordered list of
frame titles to a model and asks for the topics, using the speaker's own words.

Results are cached in keywords.json (slug -> [keyword, ...]) and committed, so
rebuild_html.py needs no network and produces the same index.html every run.
Only talks missing from the cache are sent to the model, so adding a talk costs
one short request.

Model access is the `claude` CLI in headless mode, which uses the existing
Claude Code login -- no API key, no extra dependency in this repo.

Usage:
    python3 curate_keywords.py                 # curate talks not yet cached
    python3 curate_keywords.py --force         # re-curate everything
    python3 curate_keywords.py --only SLUG     # re-curate one talk
    python3 curate_keywords.py --model sonnet  # default is haiku
    python3 curate_keywords.py --jobs 1        # serial; default runs 4 at once
    python3 curate_keywords.py --dry-run       # show what would be sent
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, "keywords.json")
MAX_KEYWORDS = 8
BATCH_SIZE = 6

# Reuse rebuild_html.py's manifest reading and .tex parsing rather than
# duplicating the brace-matching extractors.
_spec = importlib.util.spec_from_file_location(
    "rebuild_html", os.path.join(HERE, "rebuild_html.py"))
rebuild_html = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rebuild_html)


INSTRUCTIONS = """\
You are curating keyword lists for a mathematician's archive of past talks. The \
keywords sit under each talk on a listing page, so a reader can tell at a glance \
what the talk is about and can text-search the page.

You are given, for each talk, its title and the ordered list of its slide titles. \
Slide titles are raw material, not keywords. Return the topics.

Rules:
- Up to %(max)d keywords per talk, in the order the topics appear in the talk. \
Return fewer when the talk has fewer real topics. Never pad the list.
- A keyword is a noun phrase naming a subject: "Density comonads", "Lawvere \
theories", "Wiring diagrams", "Categorical databases".
- Drop slides that are navigation, rhetoric, or logistics rather than content: \
"How this talk will go", "Why are we here?", "This is the subject of the talk", \
"Taking stock", "Minor difficulty during talk", "Supplementary material", \
"A word of thanks", "What just happened?".
- Strip presentational scaffolding from the front of a title: "Ex 1: Lawvere \
theories" becomes "Lawvere theories"; "Operad 3: probabilities" becomes \
"probabilities"; "Aside: ..." and "Interlude: ..." lose the prefix. A title that \
names a slide rather than a subject -- "Extra slide: proof of theorem 1", \
"Arrangements 1 of 3", "Example", "Notation" -- is dropped, not stripped.
- When a slide title is a full sentence or a claim, reduce it to the subject it \
is about: "Left Kan extension along anything preserves pra" becomes "Left Kan \
extensions"; "Comonoids in Poly are categories (Ahman-Uustalu)" becomes \
"Comonoids in Poly".
- Use the speaker's own vocabulary. Never invent a term, and never paraphrase one \
technical term into a different one. Keep notation as the speaker writes it \
(Poly, Cat^#, C-set, Int(Poly_+)).
- Deduplicate, including near-duplicates that differ only in wording.
- Some slide titles arrive mangled by LaTeX stripping, with a symbol missing \
(", its endofunctors, and its monoidal structures"). Recover the noun phrase if \
it is clear from the surrounding titles; otherwise drop the entry.

Return a single JSON object mapping each talk's slug to its array of keyword \
strings. Include every slug you were given. Output the JSON alone: no prose, no \
markdown fences, no commentary.
""" % {"max": MAX_KEYWORDS}


def build_task(entry, frame_titles):
    """Render one talk as a block of the model prompt."""
    lines = [f"slug: {entry['slug']}"]
    title = entry.get("title_corrected") or entry.get("title") or ""
    if title:
        lines.append(f"talk title: {title}")
    lines.append("slide titles:")
    for t in frame_titles:
        lines.append(f"  - {t}")
    return "\n".join(lines)


def prompt_for(batch):
    """Full prompt for one batch of (entry, frame_titles) pairs."""
    blocks = "\n\n".join(build_task(e, ft) for e, ft in batch)
    return f"{INSTRUCTIONS}\n\nTalks:\n\n{blocks}\n"


def strip_fences(s):
    """Models often wrap JSON in markdown fences; take what is inside."""
    s = s.strip()
    m = re.search(r'```(?:json)?\s*(.*?)```', s, re.DOTALL)
    if m:
        return m.group(1).strip()
    return s


def call_model(prompt, model):
    """Run the prompt through the headless claude CLI, return parsed JSON."""
    try:
        proc = subprocess.run(
            ["claude", "-p", "--model", model, "--output-format", "text",
             "--no-session-persistence"],
            input=prompt, capture_output=True, text=True, timeout=600,
        )
    except FileNotFoundError:
        sys.exit("error: the `claude` CLI is not on PATH; "
                 "install Claude Code or curate keywords.json by hand.")
    except subprocess.TimeoutExpired:
        print("  WARNING: model call timed out", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(f"  WARNING: claude exited {proc.returncode}: "
              f"{proc.stderr.strip()[:300]}", file=sys.stderr)
        return None
    try:
        return json.loads(strip_fences(proc.stdout))
    except json.JSONDecodeError as e:
        print(f"  WARNING: could not parse model output ({e}); "
              f"got: {proc.stdout.strip()[:300]}", file=sys.stderr)
        return None


def clean(keywords):
    """Normalize one talk's returned list; drop anything unusable."""
    out = []
    seen = set()
    for k in keywords if isinstance(keywords, list) else []:
        if not isinstance(k, str):
            continue
        k = re.sub(r'\s+', ' ', k).strip().strip('.,;:')
        # A keyword that runs on is a sentence the model failed to reduce.
        if not (2 <= len(k) <= 70):
            continue
        if k.lower() in seen:
            continue
        seen.add(k.lower())
        out.append(k)
    return out[:MAX_KEYWORDS]


def ungrounded(keywords, frame_titles):
    """Keywords whose wording is not found in the slide titles.

    The model is told to use the speaker's own vocabulary; a keyword that does
    not appear in the source is one it coined. Trimming a plural is fine, so
    compare on a stem. Reported for review, not dropped -- an occasional
    legitimate reduction ("Comonoids in Poly" from a longer title) lands here."""
    blob = " || ".join(frame_titles).lower()
    return [k for k in keywords if k.lower().rstrip('s') not in blob]


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="haiku",
                    help="model for the claude CLI (default: haiku)")
    ap.add_argument("--force", action="store_true",
                    help="re-curate talks already in keywords.json")
    ap.add_argument("--only", metavar="SLUG", action="append",
                    help="curate just this slug (repeatable); implies --force")
    ap.add_argument("--limit", type=int,
                    help="stop after this many talks (for spot-checking)")
    ap.add_argument("--jobs", type=int, default=4,
                    help="batches to run concurrently (default: 4)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the prompts instead of calling the model")
    args = ap.parse_args()

    cache = load_cache()
    manifest = rebuild_html.read_manifest()

    pending = []
    for entry in manifest:
        slug = entry["slug"]
        if args.only:
            if slug not in args.only:
                continue
        elif slug in cache and not args.force:
            continue
        tex = rebuild_html.find_source_tex(entry.get("source_dir", ""))
        if not tex:
            continue
        frame_titles = rebuild_html.extract_frame_titles(tex)
        if not frame_titles:
            continue
        entry["title_corrected"] = (
            rebuild_html.MANUAL_TITLES.get(slug)
            or rebuild_html.extract_title_from_tex(tex)
            or entry.get("title", ""))
        pending.append((entry, frame_titles))

    if args.limit:
        pending = pending[:args.limit]

    if not pending:
        print("Nothing to curate; keywords.json is up to date.")
        return

    batches = [pending[i:i + BATCH_SIZE]
               for i in range(0, len(pending), BATCH_SIZE)]

    if args.dry_run:
        for n, batch in enumerate(batches, 1):
            slugs = [e["slug"] for e, _ in batch]
            print(f"\n----- batch {n}: {', '.join(slugs)} -----")
            print(prompt_for(batch))
        return

    print(f"Curating {len(pending)} talk(s) with model '{args.model}' "
          f"in {len(batches)} batch(es) of {BATCH_SIZE}, {args.jobs} at a time.")

    # One CLI call per batch; the calls are independent, and each takes long
    # enough that running them serially dominates the wall clock.
    lock = threading.Lock()
    counter = {"done": 0, "curated": 0}

    def run_batch(batch):
        slugs = [e["slug"] for e, _ in batch]
        result = call_model(prompt_for(batch), args.model)
        by_slug = {e["slug"]: ft for e, ft in batch}
        with lock:
            counter["done"] += 1
            print(f"  [{counter['done']}/{len(batches)}] {', '.join(slugs)}")
            if not isinstance(result, dict):
                print("    skipped (no usable response); rerun to retry",
                      file=sys.stderr)
                return
            for slug in slugs:
                if slug not in result:
                    print(f"    WARNING: model omitted {slug}", file=sys.stderr)
                    continue
                kws = clean(result[slug])
                if not kws:
                    print(f"    WARNING: no usable keywords for {slug}",
                          file=sys.stderr)
                    continue
                coined = ungrounded(kws, by_slug[slug])
                if coined:
                    print(f"    CHECK {slug}: not in the slide titles: "
                          f"{', '.join(coined)}", file=sys.stderr)
                cache[slug] = kws
                counter["curated"] += 1
            for extra in set(result) - set(slugs):
                print(f"    WARNING: model returned unrequested slug {extra}",
                      file=sys.stderr)
            save_cache(cache)  # checkpoint: an interrupted run keeps its work
            sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(run_batch, batches))
    curated = counter["curated"]

    print(f"\nCurated {curated} talk(s); keywords.json now holds {len(cache)}.")
    print("Review below, then run rebuild_html.py.\n")
    for entry, _ in pending:
        slug = entry["slug"]
        if slug in cache:
            print(f"[{slug}] " + " | ".join(cache[slug]))


if __name__ == "__main__":
    main()
