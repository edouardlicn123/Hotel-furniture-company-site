import os
import argparse
from pathlib import Path
from datetime import datetime

# 默认要包含的文件扩展名（根据当前项目进度优化，聚焦核心代码和配置）
INCLUDE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json',
    '.yaml', '.yml', '.md', '.txt', '.toml', '.ini', '.cfg', '.env.example',
    '.dockerfile', 'dockerfile', '.sh', '.bat', '.sql', '.java', '.go', '.rs',
    '.c', '.cpp', '.h', '.php', '.rb', '.swift', '.kt'
}

# 默认要排除的目录和文件（增强排除，避免无关或敏感内容）
EXCLUDE_DIRS = {
    '__pycache__', '.git', '.svn', '.hg', '.idea', '.vscode', 'node_modules',
    '.venv', 'venv', 'env', '.env', 'dist', 'build', 'target', '.next',
    '.gradle', '.cache', '.pytest_cache', '.mypy_cache', 'coverage', 'code2ai',
    '.github', 'docs', 'examples'  # 新增：排除 GitHub workflows、docs、examples 等非核心代码目录
}

EXCLUDE_FILES = {
    '.gitignore', '.DS_Store', 'Thumbs.db', 'project_review_*.txt'  # 新增：排除生成的 review 文件
}

DB_EXTENSIONS = {'.sqlite', '.sqlite3', '.db', '.mdb'}

def should_exclude(path: Path) -> bool:
    """
    判断是否应该排除某个路径（文件或目录）
    """
    # 直接匹配名称
    if path.name in EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES:
        return True

    # 数据库文件
    if path.suffix.lower() in DB_EXTENSIONS:
        return True

    # 备份文件或临时文件
    if path.name.endswith('~') or path.name.startswith('.#'):
        return True

    # 关键增强：彻底排除 code2ai 目录及其任何子内容
    if 'code2ai' in path.parts:
        return True

    # 新增：排除 .polygon 等测试或缓存目录（根据当前项目结构）
    if path.name.startswith('.polygon'):
        return True

    return False

def should_include(path: Path) -> bool:
    """判断文件是否应该被包含（聚焦核心代码）"""
    return path.suffix.lower() in INCLUDE_EXTENSIONS or path.name.lower() == 'dockerfile'

def collect_files(root_dir: Path):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_path = Path(dirpath)

        # 原地修改 dirnames，提前跳过所有需要排除的目录（提升效率）
        dirnames[:] = [
            d for d in dirnames
            if not should_exclude(current_path / d)
        ]

        for filename in filenames:
            file_path = current_path / filename

            # 跳过明确要排除的文件
            if should_exclude(file_path):
                continue

            # 只包含指定扩展名的文件
            if should_include(file_path):
                files.append(file_path)

    return sorted(files)

def generate_output_path(root: Path, user_output: str) -> Path:
    """
    生成最终输出路径。
    如果用户只指定了目录（如 code2ai/），则自动在该目录下生成带时间戳的文件。
    """
    output = Path(user_output).expanduser().resolve()

    # 如果是目录或仅指定了 code2ai，则生成带时间戳的文件名
    if output.is_dir() or output.suffix == "" or output.name == "code2ai":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"project_review_{timestamp}.txt"
        target_dir = root / "code2ai" if output.name == "code2ai" else output
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / filename

    # 用户指定了完整文件名，直接使用（会覆盖同名文件）
    output.parent.mkdir(parents=True, exist_ok=True)
    return output

def main():
    parser = argparse.ArgumentParser(
        description="将项目文件整合为单个 txt 文件，供 AI 审查使用（已优化监控范围，聚焦核心代码）"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="项目根目录路径（默认当前目录）"
    )
    parser.add_argument(
        "-o", "--output",
        default="code2ai/",
        help="输出文件路径。如果只指定目录（如 code2ai/），会自动生成带时间戳的文件名"
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=500_000,  # 500KB
        help="单个文件最大字节数，超过则跳过（默认 500KB）"
    )

    args = parser.parse_args()
    root = Path(args.project_dir).resolve()

    if not root.is_dir():
        print(f"错误：路径 {root} 不存在或不是目录")
        return

    # 生成输出路径
    output_path = generate_output_path(root, args.output)

    # 收集文件
    files = collect_files(root)

    print(f"正在处理项目目录：{root}")
    print(f"找到 {len(files)} 个待包含的文件（已优化排除非核心内容）")
    print(f"将写入：{output_path}\n")

    skipped = 0
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f"# 项目文件汇总（用于 AI 审查）\n")
        outfile.write(f"# 项目路径：{root}\n")
        outfile.write(f"# 生成时间：{datetime.now().isoformat()}\n")
        outfile.write(f"# 共包含 {len(files)} 个文件\n\n")
        outfile.write("=" * 80 + "\n\n")

        for file_path in files:
            rel_path = file_path.relative_to(root)
            try:
                size = file_path.stat().st_size
                if size > args.max_size:
                    print(f"跳过过大文件：{rel_path} ({size/1024:.1f} KB)")
                    skipped += 1
                    continue

                content = file_path.read_text(encoding="utf-8", errors="replace")

                outfile.write(f"### 文件: {rel_path}\n")
                outfile.write(f"# 大小: {size} 字节\n")
                outfile.write("```\n")
                outfile.write(content)
                if not content.endswith("\n"):
                    outfile.write("\n")
                outfile.write("```\n")
                outfile.write("\n" + "-" * 80 + "\n\n")

            except Exception as e:
                print(f"读取失败：{rel_path} ({e})")
                skipped += 1

    total_mb = output_path.stat().st_size / 1024 / 1024
    print(f"\n完成！已生成文件：")
    print(f"   {output_path}")
    if skipped > 0:
        print(f"（跳过了 {skipped} 个文件）")
    print(f"文件总大小约：{total_mb:.2f} MB")

if __name__ == "__main__":
    main()
