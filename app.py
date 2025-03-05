import streamlit as st
import numpy as np
from PIL import Image
import io
import zipfile
import os
from azure.storage.blob import BlobServiceClient
import time
import concurrent.futures

# 環境変数を取得
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")

# Azure Storage に接続
blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_STORAGE_KEY
)
container_name = "upload-history"
blob_client = blob_service_client.get_container_client(container_name)

# タイトル & UI 設定
st.set_page_config(page_title="画像処理アプリ", layout="wide")
st.title("📷 画像処理アプリ")
st.write("画像をアップロードして、リサイズ・フォーマット変換・2値化・圧縮ができます。")

# サイドバー設定
st.sidebar.header("⚙️ 設定")

# ✅ リサイズ方法の選択
resize_method = st.sidebar.radio("リサイズ方法を選択", ["なし", "幅・高さを指定", "比率でリサイズ"])

if resize_method == "幅・高さを指定":
    width = st.sidebar.number_input("幅 (ピクセル)", min_value=1, value=300)
    height = st.sidebar.number_input("高さ (ピクセル)", min_value=1, value=300)
    resize_ratio = None  # 手動指定の場合は比率なし

elif resize_method == "比率でリサイズ":
    resize_ratio = st.sidebar.slider("リサイズ比率（%）", min_value=10, max_value=200, value=100) / 100
    width, height = None, None  # 比率指定の場合はピクセル値なし

else:
    width, height, resize_ratio = None, None, None  # なしの場合はリサイズなし

convert_option = st.sidebar.selectbox("フォーマット変換", ["なし", "PNG", "JPEG"])
compression_quality = st.sidebar.slider("📉 圧縮率 (JPEG)", min_value=10, max_value=100, value=85) if convert_option == "JPEG" else None

grayscale_option = st.sidebar.checkbox("グレースケール画像を作成")
binarization_option = st.sidebar.checkbox("2値化画像を作成")
threshold = st.sidebar.slider("2値化しきい値", min_value=0, max_value=255, value=128) if binarization_option else None

# 画像アップロード
uploaded_files = st.file_uploader("画像を選択してください（JPG, PNG）", type=["jpg", "png"], accept_multiple_files=True)

# キャッシュを活用して画像を処理
@st.cache_data
def process_image(image, idx):
    """画像処理（リサイズ・グレースケール・2値化）"""
    file_name, ext = os.path.splitext(image.name)
    img = Image.open(image)

    # ✅ リサイズ処理
    if resize_method == "幅・高さを指定":
        img = img.resize((width, height))

    elif resize_method == "比率でリサイズ":
        new_width = int(img.width * resize_ratio)
        new_height = int(img.height * resize_ratio)
        img = img.resize((new_width, new_height))

    # グレースケール
    gray_img = img.convert("L") if grayscale_option else None

    # 2値化
    bin_img = gray_img.point(lambda x: 255 if x > threshold else 0, mode="1") if binarization_option and gray_img else None

    return img, gray_img, bin_img, file_name

# 画像の処理
if uploaded_files:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(process_image, file, idx): file for idx, file in enumerate(uploaded_files)}
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    img, gray_img, bin_img, file_name = future.result()

                    # UI表示
                    st.subheader(f"📷 {file.name}")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.image(img, caption="元画像", use_container_width=True)

                    if gray_img:
                        with col2:
                            st.image(gray_img, caption="グレースケール", use_container_width=True)

                    if bin_img:
                        with col3:
                            st.image(bin_img, caption="2値化", use_container_width=True)

                    # Blob Storage に履歴保存
                    log_data = f"{file_name},{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    blob_client.upload_blob(f"logs/{file_name}.txt", log_data, overwrite=True)

                    # ZIP に追加
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    zip_file.writestr(f"{file_name}.png", buffer.getvalue())

                except Exception as e:
                    st.error(f"エラー: {e}")

    # ZIPダウンロードボタン
    zip_buffer.seek(0)
    st.download_button("📥 すべての画像をダウンロード（ZIP）", data=zip_buffer, file_name="processed_images.zip", mime="application/zip")

#######################

import pandas as pd
import plotly.express as px

# アップロード履歴のデータを取得する関数
def get_upload_history():
    """Azure Blob Storage の logs フォルダ内の履歴を取得"""
    blobs = blob_client.list_blobs(name_starts_with="logs/")
    log_files = [blob.name for blob in blobs]
    
    # ログデータを格納
    data = []

    for log in log_files:
        blob_data = blob_client.get_blob_client(log).download_blob().readall()
        content = blob_data.decode("utf-8").strip()
        file_name, upload_time = content.split(",")
        data.append({"ファイル名": file_name, "アップロード日時": upload_time})

    # DataFrame に変換
    if data:
        df = pd.DataFrame(data)
        df["アップロード日時"] = pd.to_datetime(df["アップロード日時"])  # 日時型に変換
        return df
    else:
        return None

# Streamlit UI に追加
st.sidebar.header("📊 アップロード履歴の可視化")

if st.sidebar.button("履歴を表示"):
    df = get_upload_history()

    if df is not None:
        st.subheader("📅 アップロード履歴一覧")
        st.dataframe(df)

        # 日ごとのアップロード数を集計
        df["日付"] = df["アップロード日時"].dt.date
        upload_counts = df.groupby("日付").size().reset_index(name="アップロード数")

        # グラフを描画
        st.subheader("📈 日ごとのアップロード数")
        fig = px.line(upload_counts, x="日付", y="アップロード数", markers=True, title="日別アップロード数の推移")
        st.plotly_chart(fig)

    else:
        st.warning("📂 アップロード履歴がありません")