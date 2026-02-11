# Hakkaman - PTT 省錢版每日通知 Line Bot

每天自動爬取 [PTT Lifeismoney 省錢版](https://www.ptt.cc/bbs/Lifeismoney/) 文章，並透過 LINE Bot 發送通知。

## 功能

- 爬取 PTT 省錢版最新文章
- 過濾今日文章，排除公告、集中串等非優惠資訊
- 依推文數排序，熱門優惠優先顯示
- 透過 LINE Bot 每日推播通知
- GitHub Actions 定時執行（每天早上 8:00 台灣時間）

## 專案結構

```
hakkaman/
├── app.py          # 主程式進入點，串接爬蟲與 LINE 推播
├── crawler.py      # PTT 爬蟲與文章格式化
├── line.py         # LINE Bot 推播功能
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── daily-notify.yml  # GitHub Actions 設定
```

## 安裝

1. clone repo

```bash
git clone https://github.com/JuneLin2001/hakkaman.git
cd hakkaman
```

2. 設定 python venv
3. 安裝套件 `pip install -r requirements.txt`

## 設定環境變數

參考 `.env.example` 建立 `.env` 檔案：

```env
CHANNEL_ACCESS_TOKEN=你的LINE_Channel_Access_Token
USER_ID=你的LINE_User_ID
```

## 使用

### 本機執行

```bash
python app.py
```

### GitHub Actions 自動排程

1. 前往 GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. 新增以下 Secrets：
   - `CHANNEL_ACCESS_TOKEN`
   - `USER_ID`
3. 推送至 GitHub 後，workflow 會在每天 08:00（台灣時間）自動執行
4. 也可以在 **Actions** 頁面手動觸發 `workflow_dispatch`
