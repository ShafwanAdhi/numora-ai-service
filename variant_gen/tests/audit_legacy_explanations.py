#!/usr/bin/env python3
"""Recover legacy explanations only for exact bank/source core matches.

This is an audit helper. It reads the workspace bank and an archived DOCX and
writes a standalone provenance report. It never updates bank or metadata files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "variant_gen"))

from bank import load_workspace_bank  # noqa: E402


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NUMBER_WORDS = {
    "satu": "1",
    "dua": "2",
    "tiga": "3",
    "empat": "4",
    "lima": "5",
    "enam": "6",
    "tujuh": "7",
    "delapan": "8",
    "sembilan": "9",
    "sepuluh": "10",
}


def element_text(element: ET.Element) -> str:
    """Include both Word text and Office Math text nodes in document order."""
    return "".join(
        node.text or "" for node in element.iter() if node.tag.rsplit("}", 1)[-1] == "t"
    )


def docx_blocks(path: Path) -> list[dict]:
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    blocks = []
    for xml_index, child in enumerate(root.find(W + "body")):
        if child.tag == W + "p":
            text = element_text(child).strip()
            kind = "paragraph"
        elif child.tag == W + "tbl":
            rows = []
            for row in child.findall(W + "tr"):
                cells = [
                    " ".join(element_text(cell).split()) for cell in row.findall(W + "tc")
                ]
                rows.append(" | ".join(cells))
            text = "\n".join(rows).strip()
            kind = "table"
        else:
            continue
        if text:
            blocks.append({"xml_index": xml_index, "kind": kind, "text": text})
    return blocks


def question_sections(blocks: list[dict]) -> list[dict]:
    starts = []
    indicator = level = None
    for index, block in enumerate(blocks):
        text = block["text"]
        match = re.match(r"(?i)indikator\s+(\d+)", text)
        if match:
            indicator = int(match.group(1))
        match = re.match(r"(?i)level\s+(\d+)\s*$", text)
        if match:
            level = int(match.group(1))
        match = re.match(r"(?i)(?:revisi\s+)?soal\s*(\d+)", text)
        if match:
            starts.append((index, indicator, level, int(match.group(1))))

    sections = []
    for ordinal, (start, indicator, level, source_number) in enumerate(starts):
        stop = starts[ordinal + 1][0] if ordinal + 1 < len(starts) else len(blocks)
        selected = blocks[start:stop]
        text = "\n".join(block["text"] for block in selected)
        # Word exports sometimes concatenate the final option and the heading
        # (for example ``D. ...Pembahasan:``), so a leading word boundary is
        # deliberately not required here.
        marker = re.search(r"(?i)pembahasan\s*:\s*", text)
        explanation = text[marker.end():].strip() if marker else ""
        heading_match = re.match(
            r"(?i)(?:revisi\s+)?soal\s*\d+(?:\s*\([^)]*\))?", selected[0]["text"]
        )
        sections.append(
            {
                "indicator": indicator,
                "level": level,
                "source_number": source_number,
                "heading": heading_match.group(0) if heading_match else selected[0]["text"][:80],
                "block_start": start,
                "block_end_exclusive": stop,
                "xml_start": selected[0]["xml_index"],
                "xml_end": selected[-1]["xml_index"],
                "text": text,
                "explanation": explanation,
            }
        )
    return sections


def normalized_core(text: str) -> str:
    """Normalize presentation only; retain words, numbers, and their order.

    DOCX list numbering is presentation metadata, so leading numeric list
    markers are removed. Indonesian number words are normalized because the
    archive mixes e.g. ``dua buah`` with exported ``2 buah``. Punctuation,
    spacing, and glyph variants are discarded, while all alphanumeric content
    and ordering remain mandatory.
    """
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"(?m)^\s*\d+[.)]\s*", "", text)
    text = (
        text.replace("−", "-")
        .replace("–", "-")
        .replace("×", "x")
        .replace("÷", "/")
        .replace("π", "pi")
    )
    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", number, text)
    return "".join(character for character in text if character.isalnum())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def expected_key(question: dict) -> dict:
    correct = [option["id"] for option in question["options"] if option["correct"]]
    if question["format"] == "PG":
        return {"kind": "option_ids", "value": correct}
    if question["format"] == "MCMA":
        return {"kind": "option_ids", "value": correct}
    return {
        "kind": "category_labels",
        "value": ["BENAR" if option["correct"] else "SALAH" for option in question["options"]],
    }


def source_key(section: dict, fmt: str) -> dict | None:
    before_explanation = section["text"].split("Pembahasan", 1)[0]
    marker = re.search(r"(?i)\bkunci(?:\s+jawaban)?\s*:\s*", before_explanation)
    if not marker:
        return None
    tail = before_explanation[marker.end():]
    if fmt == "PG":
        match = re.match(r"\s*([A-D])(?:\s*[.)]|\s)", tail, re.I)
        return {"kind": "option_ids", "value": [match.group(1).upper()]} if match else None
    if fmt == "MCMA":
        # The archive consistently expresses MCMA keys as "Pernyataan 1, ...".
        match = re.match(
            r"\s*((?:Pernyataan\s*[1-4]\s*,?\s*(?:(?:dan|&)\s*)?)+)", tail, re.I
        )
        if not match:
            match = re.match(r"\s*([A-D](?:\s*,\s*[A-D])*(?:\s*(?:dan|&)\s*[A-D])?)", tail, re.I)
            if not match:
                return None
            ids = re.findall(r"[A-D]", match.group(1).upper())
        else:
            ids = [chr(64 + int(number)) for number in re.findall(r"[1-4]", match.group(1))]
        return {"kind": "option_ids", "value": ids}
    pairs = re.findall(r"([ABC])\s*[.)]?\s*(Benar|Salah)", tail[:180], re.I)
    if len(pairs) < 3:
        return None
    labels = {letter.upper(): label.upper() for letter, label in pairs[:3]}
    return {"kind": "category_labels", "value": [labels[x] for x in "ABC"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, default=ROOT / "variant_gen/data/q0_bank.csv")
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "variant_gen/data/drill-1-indicators-16-19/source-revision-2026-10-07.docx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/audits/2026-10-19-original-question-audit/legacy-explanations.json",
    )
    args = parser.parse_args()

    bank = load_workspace_bank(args.bank)
    targets = [bank.get(qid) for qid in bank.ids() if not bank.get(qid).get("metadata")]
    blocks = docx_blocks(args.source)
    sections = question_sections(blocks)
    source_sha256 = hashlib.sha256(args.source.read_bytes()).hexdigest()
    source_path = args.source.relative_to(ROOT).as_posix()

    entries = []
    for question in targets:
        stem = normalized_core(question["stem"])
        options = [normalized_core(option["text"]) for option in question["options"]]
        expected = expected_key(question)
        stem_candidates = []
        core_candidates = []
        keyed_candidates = []
        candidates = []
        for section in sections:
            section_core = normalized_core(section["text"])
            stem_match = stem in section_core
            option_matches = [option in section_core for option in options]
            parsed_key = source_key(section, question["format"])
            key_match = parsed_key == expected
            if stem_match:
                stem_candidates.append(section)
            if stem_match and all(option_matches):
                core_candidates.append(section)
            if stem_match and all(option_matches) and key_match:
                keyed_candidates.append(section)
            if stem_match and all(option_matches) and key_match and section["explanation"]:
                candidates.append((section, parsed_key, option_matches))

        base = {
            "question_id": question["id"],
            "question_hash": question["hash"],
        }
        if len(candidates) == 1:
            section, parsed_key, option_matches = candidates[0]
            base.update(
                {
                    "status": "RECOVERED_EXACT_CORE_MATCH",
                    "explanation": section["explanation"],
                    "provenance": {
                        "path": source_path,
                        "sha256": source_sha256,
                        "section": (
                            f"INDIKATOR {section['indicator']} / LEVEL {section['level']} / "
                            f"{section['heading']}"
                        ),
                        "document_block_start": section["block_start"],
                        "document_block_end_exclusive": section["block_end_exclusive"],
                        "document_xml_index_start": section["xml_start"],
                        "document_xml_index_end": section["xml_end"],
                    },
                    "core_match_evidence": {
                        "normalization": "NFKC_CASEFOLD_ALNUM_LIST_MARKERS_NUMBER_WORDS",
                        "stem_exact_normalized_substring": True,
                        "stem_normalized_sha256": digest(stem),
                        "options_exact_normalized_substrings": option_matches,
                        "option_normalized_sha256": [digest(option) for option in options],
                        "bank_key": expected,
                        "source_key": parsed_key,
                        "key_exact": True,
                    },
                }
            )
        else:
            if not stem_candidates:
                reason = "NO_EXACT_NORMALIZED_STEM_MATCH_IN_ARCHIVE"
            elif not core_candidates:
                reason = "STEM_MATCHED_BUT_NOT_ALL_OPTIONS_MATCHED_EXACTLY"
            elif not keyed_candidates:
                reason = "STEM_AND_OPTIONS_MATCHED_BUT_KEY_DIFFERED"
            elif not candidates:
                reason = "EXACT_CORE_MATCH_HAS_NO_SOURCE_EXPLANATION"
            else:
                reason = "AMBIGUOUS_MULTIPLE_EXACT_CORE_MATCHES"
            base.update(
                {
                    "status": "UNAVAILABLE",
                    "explanation": None,
                    "provenance": None,
                    "core_match_evidence": None,
                    "unavailable_reason": reason,
                    "candidate_count": len(candidates),
                    "rejection_evidence": {
                        "exact_stem_candidate_count": len(stem_candidates),
                        "exact_stem_and_all_options_candidate_count": len(core_candidates),
                        "exact_stem_options_key_candidate_count": len(keyed_candidates),
                        "exact_core_with_explanation_candidate_sections": [
                            {
                                "section": (
                                    f"INDIKATOR {section['indicator']} / LEVEL {section['level']} / "
                                    f"{section['heading']}"
                                ),
                                "document_block_start": section["block_start"],
                                "document_block_end_exclusive": section["block_end_exclusive"],
                            }
                            for section, _, _ in candidates
                        ],
                    },
                }
            )
        entries.append(base)

    recovered = sum(entry["status"] == "RECOVERED_EXACT_CORE_MATCH" for entry in entries)
    result = {
        "schema_version": 1,
        "scope": "workspace originals without metadata loaded by load_workspace_bank",
        "matching_policy": (
            "Recovery requires one unique archived section with exact normalized stem containment, "
            "every option, the complete answer key, and a non-empty source explanation. "
            "Question position and generated explanations are not used."
        ),
        "source": {"path": source_path, "sha256": source_sha256},
        "summary": {
            "target_count": len(entries),
            "recovered_count": recovered,
            "unavailable_count": len(entries) - recovered,
        },
        "questions": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
