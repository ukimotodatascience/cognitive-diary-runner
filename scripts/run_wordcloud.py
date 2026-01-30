from __future__ import annotations

from pathlib import Path
import os
import re

from sudachipy import dictionary
from sudachipy import tokenizer
from wordcloud import WordCloud


def split_text_by_bytes(text: str, max_bytes: int = 48000) -> list[str]:
    lines = text.splitlines()
    chunks: list[str] = []
    current = ""
    for line in lines:
        candidate = f"{current}\n{line}" if current else line
        if len(candidate.encode("utf-8")) > max_bytes:
            if current:
                chunks.append(current)
                current = line
            else:
                line_bytes = line.encode("utf-8")
                for i in range(0, len(line_bytes), max_bytes):
                    chunks.append(
                        line_bytes[i : i + max_bytes].decode("utf-8", errors="ignore")
                    )
                current = ""
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def extract_hitokoto(text: str) -> str:
    match = re.search(
        r"^### \\s*＜一言＞\\s*\\n+([\\s\\S]*?)(?:\\n### |\\Z)",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return ""
    return match.group(1).strip()


def main() -> list[Path]:
    diary_repo_path = Path(os.environ.get("DIARY_REPO_PATH", "diary"))
    diary_dir = os.environ.get("DIARY_DIR", "日記")
    output_subdir = os.environ.get("OUTPUT_SUBDIR", "ワードクラウド")
    font_path = os.environ.get(
        "FONT_PATH", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
    )

    diary_root = diary_repo_path / diary_dir
    output_dir = diary_root / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_obj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.C

    wc_config = dict(
        width=1200,
        height=800,
        background_color="white",
        font_path=font_path,
        collocations=False,
    )

    output_paths: list[Path] = []
    yearly_words: dict[str, list[str]] = {}

    for diary_path in sorted(diary_root.glob("**/*.md")):
        text = diary_path.read_text(encoding="utf-8")
        text = extract_hitokoto(text)

        text = re.sub(r"https?://\\S+", "", text)
        text = re.sub(r"[#*<>`\\[\\]()]", " ", text)
        text = re.sub(r"[0-9]+", " ", text)
        text = re.sub(r"\\s+", " ", text).strip()

        words: list[str] = []
        for chunk in split_text_by_bytes(text):
            for token in tokenizer_obj.tokenize(chunk, mode):
                part_of_speech = token.part_of_speech()[0]
                if part_of_speech in {"名詞", "動詞", "形容詞"}:
                    base_form = token.dictionary_form()
                    if base_form not in {
                        "する",
                        "いる",
                        "ある",
                        "なる",
                        "こと",
                        "もの",
                    }:
                        words.append(base_form)

        if words:
            year_key = diary_path.parent.name
            yearly_words.setdefault(year_key, []).extend(words)

        word_text = " ".join(words)
        if not word_text:
            continue

        wc = WordCloud(**wc_config)
        frequencies = wc.process_text(word_text)
        if not frequencies:
            continue
        wc.generate_from_frequencies(frequencies)

        output_path = output_dir / f"wordcloud_{diary_path.stem}.png"
        wc.to_file(output_path.as_posix())
        output_paths.append(output_path)

    for year_key, words in sorted(yearly_words.items()):
        word_text = " ".join(words)
        if not word_text:
            continue

        wc = WordCloud(**wc_config)
        frequencies = wc.process_text(word_text)
        if not frequencies:
            continue
        wc.generate_from_frequencies(frequencies)

        output_path = output_dir / f"wordcloud_{year_key}.png"
        wc.to_file(output_path.as_posix())
        output_paths.append(output_path)

    return output_paths


if __name__ == "__main__":
    generated = main()
    for path in generated:
        print(path)
