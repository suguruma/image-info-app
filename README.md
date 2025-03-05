# 🖼 画像処理アプリ

🚀 **このアプリは、画像をアップロードして「リサイズ」「フォーマット変換」「2値化」「圧縮」などの処理ができる Web アプリです。**  
📡 **Azure 上で動作し、アップロード履歴を Azure Blob Storage に保存します。**

---

## 📌 主な機能

- ✅ **画像アップロード（JPG / PNG）**
- ✅ **リサイズ（ピクセル指定 or 比率指定）**
- ✅ **フォーマット変換（PNG / JPEG）**
- ✅ **2値化処理（しきい値調整可）**
- ✅ **画像の圧縮（JPEG の品質調整）**
- ✅ **Azure Blob Storage にアップロード履歴を保存**
- ✅ **履歴の可視化（アップロード履歴のグラフ表示）**
- ✅ **処理後の画像を ZIP 形式でダウンロード可能**

---

## 🛠 必要な環境

このアプリを実行するには、以下の環境が必要です。

### **1. 必要なライブラリ**
`requirements.txt` に必要なライブラリを記載しています。

```
streamlit
numpy
pillow
matplotlib
azure-storage-blob
python-dotenv
pandas
plotly
```

以下のコマンドでライブラリをインストールしてください。

```sh
pip install -r requirements.txt
```

---

### **2. Azure の設定**
Azure Blob Storage を使用するため、環境変数を設定する必要があります。

#### **Azure での環境変数設定**
Azure Portal → 「App Service」→「構成（Configuration）」→「アプリケーション設定」に以下を追加してください。

| 設定キー | 設定値 |
|---------|------|
| `AZURE_STORAGE_ACCOUNT` | ストレージアカウント名 |
| `AZURE_STORAGE_KEY` | ストレージアカウントのアクセスキー |

---

## 🚀 アプリの実行方法（ローカル）

### **1. リポジトリをクローン**
```sh
git clone https://github.com/your-repository/image-processing-app.git
cd image-processing-app
```

### **2. 環境変数を設定（ローカル環境用）**
`~/.streamlit/secrets.toml` を作成し、以下の内容を記載

```toml
[secrets]
AZURE_STORAGE_ACCOUNT = "your_storage_account"
AZURE_STORAGE_KEY = "your_storage_key"
```

### **3. アプリを起動**
```sh
streamlit run app.py
```

### **4. ブラウザでアクセス**
ブラウザで `http://localhost:8501` にアクセスして動作を確認してください。

---

## 📡 Azure へのデプロイ方法

### **1. GitHub にプッシュ**
変更をコミットし、GitHub にプッシュします。

```sh
git add .
git commit -m "Update README and app"
git push origin main
```

### **2. Azure でデプロイ**
Azure Portal の「App Service」→「デプロイセンター」で「GitHub 連携」を設定し、自動デプロイを有効にしてください。

### **3. アプリの URL**
デプロイが完了すると、以下の URL でアクセスできます。

```
https://your-app-name.azurewebsites.net
```

---

## 📊 アップロード履歴の確認

1. **Streamlit のサイドバーで「履歴を表示」ボタンをクリック**
2. **アップロード履歴がテーブル表示される**
3. **日ごとのアップロード数が折れ線グラフで表示される**

---

## 📝 ライセンス

MIT License

---
