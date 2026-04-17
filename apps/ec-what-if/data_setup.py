"""
起動時にサンプルデータを自動再生成する。
create_sample_data.py が training_data.csv より新しい場合に再実行。
app.py の train_models() から呼び出される。
"""
import os
import subprocess
import sys


def ensure_fresh_data():
    """create_sample_data.py が更新されていれば training_data.csv を再生成。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    regen_script = os.path.join(script_dir, "create_sample_data.py")
    data_path = os.path.join(script_dir, "sample_data", "training_data.csv")

    if not os.path.exists(regen_script):
        return

    need_regen = False
    if not os.path.exists(data_path):
        need_regen = True
    else:
        try:
            if os.path.getmtime(regen_script) > os.path.getmtime(data_path):
                need_regen = True
        except OSError:
            need_regen = True

    if need_regen:
        subprocess.run(
            [sys.executable, regen_script],
            check=True,
            cwd=script_dir,
            capture_output=True,
        )
