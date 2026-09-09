#!/usr/bin/env python
from __future__ import annotations
import os, sys, json, argparse, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "resources" / "datasets.yaml"
COUNTS_DIR = ROOT / "resources" / "counts"


def count_words(text: str) -> int:
    return len(text.split())


def normalize(text: str) -> str:
    """NFC — the normalization the tokenizer should also apply (canonical Devanagari)."""
    return unicodedata.normalize("NFC", text)


def load_registry() -> dict:
    import yaml

    with open(REGISTRY) as f:
        return yaml.safe_load(f)


def _source(name: str) -> dict:
    for s in load_registry()["sources"]:
        if s["name"] == name:
            return s
    raise KeyError(f"unknown source '{name}' (see resources/datasets.yaml)")


def usable_sources() -> list[str]:
    return [s["name"] for s in load_registry()["sources"] if s.get("status") == "use"]


_TEXT_FALLBACKS = ("text", "Article", "content", "sentence")


def _text_of(row: dict, key: str) -> str:
    v = row.get(key)
    if isinstance(v, str) and v:
        return v
    for k in _TEXT_FALLBACKS:
        v = row.get(k)
        if isinstance(v, str) and v:
            return v
    return next((v for v in row.values() if isinstance(v, str) and v), "")


def iter_documents(name: str, limit: int | None = None, normalize_nfc: bool = False):
    from datasets import load_dataset

    s = _source(name)
    if s.get("status") != "use":
        raise ValueError(
            f"source '{name}' is status={s.get('status')} — {s.get('reason','')}"
        )
    kw = dict(path=s["hf_dataset"], split=s.get("split", "train"), streaming=True)
    if s.get("hf_config"):
        kw["name"] = s["hf_config"]
    if s.get("data_files"):
        kw["data_files"] = s["data_files"]
    ds = load_dataset(**kw)
    key = s.get("text_key", "text")
    n = 0
    for row in ds:
        t = _text_of(row, key)
        if not t:
            continue
        yield normalize(t) if normalize_nfc else t
        n += 1
        if limit and n >= limit:
            break


def _count(names: list[str], limit: int | None):
    import numpy, array, time

    COUNTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        t0 = time.time()
        counts = array.array("i")
        for t in iter_documents(name, limit=limit):
            counts.append(min(count_words(t), 2_000_000_000))
        a = numpy.frombuffer(counts, dtype=numpy.int32)
        res = dict(
            source=name,
            n_docs=int(a.size),
            total_words=int(a.sum(dtype=numpy.int64)),
            mean=float(a.mean()),
            median=float(numpy.median(a)),
            min=int(a.min()),
            max=int(a.max()),
            limit=limit,
            elapsed_sec=round(time.time() - t0, 1),
        )
        with open(COUNTS_DIR / f"{name}.json", "w") as f:
            json.dump(res, f, indent=2)
        print(
            f"{name:14} n={res['n_docs']:>10,} words={res['total_words']:>14,} "
            f"mean={res['mean']:.1f} median={res['median']}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser(
        "count", help="stream + count words, write resources/counts/*.json"
    )
    c.add_argument(
        "sources", nargs="*", help="source names (default: all `use` sources)"
    )
    c.add_argument("--limit", type=int, default=None, help="cap documents per source")
    ls = sub.add_parser("list", help="print the usable sources + registry counts")
    args = ap.parse_args()
    if args.cmd == "list":
        for s in load_registry()["sources"]:
            print(
                f"{s['name']:14} {s.get('status'):8} "
                f"docs={s.get('documents','?'):>10} words={s.get('words','?')}"
            )
    elif args.cmd == "count":
        _count(args.sources or usable_sources(), args.limit)


if __name__ == "__main__":
    main()
