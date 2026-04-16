"""
全アプリ スモークテスト
========================
全Streamlitアプリの基本健全性を一括検証するスクリプト

検証項目:
1. ast.parse による構文チェック
2. create_sample_data.py の実行可能性（出力CSVの存在確認）
3. 必須ファイルの存在 (requirements.txt, packages.txt, .streamlit/config.toml)
4. import健全性 (streamlit関連を除く必須モジュールがimport可能か)

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --json  # JSON形式で出力
"""
import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルート（このスクリプトの親ディレクトリ）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = PROJECT_ROOT / "apps"

REQUIRED_FILES = ["app.py", "requirements.txt", "packages.txt", ".streamlit/config.toml"]


def discover_apps():
    """apps/ 配下のアプリディレクトリを列挙（commonは除く）"""
    apps = []
    for d in sorted(APPS_DIR.iterdir()):
        if d.is_dir() and d.name != "common" and (d / "app.py").exists():
            apps.append(d)
    return apps


def check_syntax(app_path):
    """ast.parse による構文チェック"""
    try:
        with open(app_path / "app.py", encoding="utf-8") as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def check_required_files(app_path):
    """必須ファイルの存在確認"""
    missing = []
    for f in REQUIRED_FILES:
        if not (app_path / f).exists():
            missing.append(f)
    return len(missing) == 0, missing


def check_sample_data(app_path):
    """create_sample_data.py を実行してCSV生成を検証"""
    create_script = app_path / "create_sample_data.py"
    if not create_script.exists():
        return None, "create_sample_data.py not found (skipped)"

    try:
        result = subprocess.run(
            [sys.executable, str(create_script)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return False, f"exit={result.returncode}: {result.stderr[:200]}"

        sample_dir = app_path / "sample_data"
        if not sample_dir.exists():
            return False, "sample_data/ directory not created"

        csv_count = len(list(sample_dir.glob("*.csv")))
        if csv_count == 0:
            return False, "no CSV files generated"

        return True, f"{csv_count} CSV files"
    except subprocess.TimeoutExpired:
        return False, "timeout (>120s)"
    except Exception as e:
        return False, str(e)


def check_imports(app_path):
    """app.py のimport文を ast で抽出し、各ライブラリがimport可能か検証"""
    try:
        with open(app_path / "app.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return False, "syntax error blocks import check"

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])

    # 標準ライブラリやstreamlit本体は除外（streamlit本体はサンドボックスでもimport可だが念のため）
    skip = {"os", "sys", "io", "re", "json", "math", "datetime", "typing",
            "collections", "warnings", "subprocess", "pathlib", "ast", "time"}
    failed = []
    for mod in modules - skip:
        try:
            __import__(mod)
        except ImportError as e:
            failed.append(f"{mod}: {e}")

    return len(failed) == 0, failed if failed else "all imports OK"


def run_smoke_test():
    apps = discover_apps()
    results = []

    for app in apps:
        name = app.name
        syntax_ok, syntax_err = check_syntax(app)
        files_ok, files_missing = check_required_files(app)
        sample_ok, sample_msg = check_sample_data(app)
        imports_ok, imports_msg = check_imports(app)

        # 全項目OKならpass
        all_ok = syntax_ok and files_ok and imports_ok and (sample_ok is None or sample_ok)

        results.append({
            "app": name,
            "passed": all_ok,
            "syntax": {"ok": syntax_ok, "error": syntax_err},
            "files": {"ok": files_ok, "missing": files_missing},
            "sample_data": {"ok": sample_ok, "msg": sample_msg},
            "imports": {"ok": imports_ok, "details": imports_msg},
        })

    return results


def print_human(results):
    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    print(f"\n=== Smoke Test Results ({passed}/{total} passed) ===\n")
    print(f"{'App':<35} {'Syntax':<8} {'Files':<8} {'Sample':<10} {'Imports':<10}")
    print("-" * 80)

    for r in results:
        s_mark = "OK" if r["syntax"]["ok"] else "FAIL"
        f_mark = "OK" if r["files"]["ok"] else "FAIL"
        sample_ok = r["sample_data"]["ok"]
        d_mark = "OK" if sample_ok else ("SKIP" if sample_ok is None else "FAIL")
        i_mark = "OK" if r["imports"]["ok"] else "FAIL"
        print(f"{r['app']:<35} {s_mark:<8} {f_mark:<8} {d_mark:<10} {i_mark:<10}")

    print()
    failed = [r for r in results if not r["passed"]]
    if failed:
        print("=== Failures ===")
        for r in failed:
            print(f"\n[{r['app']}]")
            if not r["syntax"]["ok"]:
                print(f"  syntax: {r['syntax']['error']}")
            if not r["files"]["ok"]:
                print(f"  files missing: {r['files']['missing']}")
            if r["sample_data"]["ok"] is False:
                print(f"  sample_data: {r['sample_data']['msg']}")
            if not r["imports"]["ok"]:
                print(f"  imports: {r['imports']['details']}")

    print(f"\n結果: {passed}/{total} アプリがスモークテストを通過")
    return passed == total


def save_json(results, output_path):
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nJSON saved to: {output_path}")


def main():
    print("Running smoke test on all apps...")
    results = run_smoke_test()

    all_passed = print_human(results)

    # JSON出力（常に保存）
    json_path = PROJECT_ROOT / "docs" / "task-improvement" / "smoke-test-result.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(results, json_path)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
