#!/usr/bin/env python3
"""template/.claude/skills 配下の各スキルを、Claude Desktop / claude.ai からインポートできる .skill ファイルに変換する。

.skill ファイルの中身は「スキル名のフォルダ/SKILL.md ...」を格納した zip。
元のスキルファイルは変更せず、dist/skills/ に出力する。

使い方:
    python3 scripts/package_skills.py
"""

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "template" / ".claude" / "skills"
OUTPUT_DIR = ROOT / "dist" / "skills"

# claude.ai のアップロード時に許可されている frontmatter のキー
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

# zip に含めないファイル
IGNORED_NAMES = {".DS_Store"}


def sanitize_frontmatter(text: str) -> str:
    """SKILL.md の frontmatter から Claude Code 固有のキー（disable-model-invocation など）を取り除く。"""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("frontmatter が見つかりません")

    kept_lines = []
    skipping = False
    for line in match.group(1).splitlines():
        key_match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if key_match:
            skipping = key_match.group(1) not in ALLOWED_KEYS
        if not skipping:
            kept_lines.append(line)

    return "---\n" + "\n".join(kept_lines) + "\n---\n" + text[match.end():]


def validate(skill_dir: Path, frontmatter_text: str) -> None:
    """name と description が要件を満たしているか確認する。"""
    name = re.search(r"^name:\s*(.+)$", frontmatter_text, re.M)
    description = re.search(r"^description:\s*(.+)$", frontmatter_text, re.M)
    if not name or not description:
        raise ValueError(f"{skill_dir.name}: name または description がありません")
    if name.group(1).strip() != skill_dir.name:
        raise ValueError(f"{skill_dir.name}: name とフォルダ名が一致しません")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", skill_dir.name):
        raise ValueError(f"{skill_dir.name}: name は小文字英数字とハイフンの64文字以内にしてください")
    if len(description.group(1).strip()) > 1024:
        raise ValueError(f"{skill_dir.name}: description が1024文字を超えています")


def package(skill_dir: Path) -> Path:
    skill_md = skill_dir / "SKILL.md"
    sanitized = sanitize_frontmatter(skill_md.read_text(encoding="utf-8"))
    validate(skill_dir, sanitized.split("---\n")[1])

    output_path = OUTPUT_DIR / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(skill_dir.rglob("*")):
            if not file.is_file() or file.name in IGNORED_NAMES:
                continue
            arcname = f"{skill_dir.name}/{file.relative_to(skill_dir).as_posix()}"
            if file == skill_md:
                zf.writestr(arcname, sanitized)
            else:
                zf.write(file, arcname)
    return output_path


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    skill_dirs = sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))
    for skill_dir in skill_dirs:
        output_path = package(skill_dir)
        print(f"作成: {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
