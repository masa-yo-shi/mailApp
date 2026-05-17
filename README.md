# Mail Classifier

メールをカテゴリ別に一覧表示し、ログイン後に自分のメールだけを閲覧できるシンプルなWebアプリです。バックエンドはFastAPI、フロントエンドはVite + Reactで構成されています。

## 使い始める手順

### 1) バックエンド起動

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY=your-secret-key
export ALLOWED_ORIGINS=http://localhost:5173

uvicorn main:app --reload
```

### 2) フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

### 3) ログイン

初期データが入っている場合、以下のユーザーでログインできます。

- johndoe / secret
- testuser / testpassword

ブラウザで http://localhost:5173 にアクセスしてください。


