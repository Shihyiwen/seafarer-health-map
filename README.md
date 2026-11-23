# 船員健康風險地圖（健康資訊管理 期中作業）

EMHA 史宜文 P14848A10｜健康資訊管理（115-1，郭年真老師）

以生成式 AI（Claude Skill＋vibe coding）建構的散裝船隊「離岸醫療可近性」互動海圖雛形，疊加港口醫療能量、JWC 戰爭風險列名區域（JWLA-035）與瘧疾／黃熱病／登革熱風險港口。**所有船舶、船員與事件資料皆為模擬。**

## 檔案
- `index.html`：網站本體（含報告：背景、問題、方法、雛形、發現、限制、參考資料）
- `data/events.csv`：235 筆模擬醫療事件；`data/ports.csv`：50 個港口與醫療分級、風險標記
- `generate_data.py`：資料產生器（固定亂數種子，可重現所有數字）
- `skill/seafarer-medical-coder/SKILL.md`：船長醫療報告編碼 Skill

## 發布到 GitHub Pages
1. GitHub 新增 public repository，例如 `seafarer-health-map`。
2. 把本資料夾所有檔案上傳到 repository 根目錄（Add file → Upload files）。
3. Settings → Pages → Source 選 `Deploy from a branch`，Branch 選 `main`、資料夾 `/ (root)` → Save。
4. 約 1 分鐘後網址為 `https://<你的帳號>.github.io/seafarer-health-map/`，把這個網址交到 NTU COOL。

## 重現資料
```bash
mkdir -p data && python3 generate_data.py
```
