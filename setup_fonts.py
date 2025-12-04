"""
フォント設定スクリプト
Streamlit Cloud環境で日本語フォントを確実にセットアップ
"""
import subprocess
import sys
import os

def install_fonts():
    """Linux環境で日本語フォントをインストール"""
    try:
        # Linux環境かチェック
        if sys.platform.startswith('linux'):
            print("Linux環境を検出: 日本語フォントをインストール中...")

            # apt-getでNoto Fontsをインストール
            subprocess.run([
                'apt-get', 'update'
            ], check=False, capture_output=True)

            subprocess.run([
                'apt-get', 'install', '-y',
                'fonts-noto-cjk',
                'fonts-noto-cjk-extra'
            ], check=False, capture_output=True)

            print("フォントインストール完了")

            # matplotlibのフォントキャッシュをクリア
            import matplotlib.font_manager as fm
            fm._rebuild()
            print("フォントキャッシュを再構築しました")

    except Exception as e:
        print(f"フォントインストールエラー（無視して続行）: {e}")

if __name__ == "__main__":
    install_fonts()
