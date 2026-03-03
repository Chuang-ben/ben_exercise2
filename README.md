# 氣象站座標系統比較分析 (CRS Comparison)

## 專案概述
分析台灣自動氣象站API (O-A0003-001) 中每個測站的兩種座標系統差異：
- TWD67 座標系統
- WGS84 座標系統

## 分析方法

### 1. 假設分析 (`crs_analysis.py`)
**目的**: 演示錯誤使用座標系統的影響
**方法**: 將 TWD67 座標直接當作 WGS84 處理
**結果**: 顯示約 0.85 公里的定位誤差

### 2. 正確轉換分析 (`correct_crs_conversion.py`)
**目的**: 評估正確座標轉換的精度
**方法**: 使用 pyproj 正確轉換 TWD67 (EPSG:3824) 到 WGS84 (EPSG:4326)
**結果**: API 提供的兩種座標間仍有約 0.851 公里的系統性差異

## 目標
1. 將兩種座標都當作 WGS84 (EPSG:4326) 處理
2. 在同一張圖上繪製兩種座標位置
3. 統計每個測站的不同測站大約差距多遠

## 資料來源
- API ID: O-A0003-001 (自動氣象站-氣象觀測資料)
- 座標系統：TWD67 和 WGS84

## 檔案結構與說明

### 📁 主要程式檔案
- **`crs_analysis.py`** - 假設分析腳本
  - 將 TWD67 座標直接當作 WGS84 處理
  - 演示錯誤使用座標系統的影響
  - 產生基本的地圖和統計圖表
  - 輸出檔案：`crs_comparison_map.html`, `distance_analysis.png`

- **`bonus_correct_crs_conversion.py`** - 正確轉換分析腳本
  - 使用 pyproj 正確轉換 TWD67 (EPSG:3824) 到 WGS84 (EPSG:4326)
  - 評估 API 提供座標的實際精度
  - 比較原始 WGS84 與轉換後 WGS84 的差異
  - 輸出檔案：`twd67_to_wgs84_map.html`, `twd67_to_wgs84_conversion.png`

### 📋 設定檔案
- **`requirements.txt`** - Python 套件依賴列表
  - 包含所有必要的套件及其版本
  - 使用 `pip install -r requirements.txt` 安裝

- **`.env`** - 環境變數設定檔（本地使用）
  - 儲存 API 金鑰等敏感資訊
  - 已加入 `.gitignore` 不會推送到 GitHub

### 📊 資料檔案
- **`data/`** - 資料資料夾
  - `weather_stations_raw.csv` - 從 API 獲取的原始氣象站資料
  - 包含 336 個測站的 TWD67 和 WGS84 座標

### 📈 輸出結果檔案
- **`output/`** - 分析結果資料夾

#### 地圖檔案
- **`crs_comparison_map.html`** - 假設分析的互動式地圖
  - 藍色標記：原始 WGS84 座標
  - 紅色標記：TWD67 當作 WGS84 的座標
  - 綠色連線：顯示座標差異

- **`twd67_to_wgs84_map.html`** - 正確轉換分析的互動式地圖
  - 藍色標記：API 提供的原始 WGS84 座標
  - 紅色標記：TWD67 正確轉換後的 WGS84 座標
  - 綠色連線：顯示轉換精度差異

#### 圖表檔案
- **`distance_analysis.png`** - 假設分析的統計圖表
  - 距離分佈直方圖
  - 箱線圖分析
  - 各縣市平均差異比較
  - 統計摘要資訊

- **`twd67_to_wgs84_conversion.png`** - 正確轉換分析的統計圖表
  - 轉換距離分佈
  - 精度評估圖表
  - 各縣市轉換差異比較

#### 資料檔案
- **`crs_comparison_results.csv`** - 假設分析的詳細結果
  - 包含每個測站的座標和距離差異
  - 可用於進一步分析

- **`twd67_to_wgs84_conversion.csv`** - 正確轉換分析的詳細結果
  - 原始座標 vs 轉換後座標比較
  - 轉換精度評估數據

#### 報告檔案
- **`crs_analysis_report.md`** - 假設分析報告
  - 詳細的統計結果和分析
  - 距離差異分佈說明

- **`twd67_to_wgs84_report.md`** - 正確轉換分析報告
  - 轉換精度評估結果
  - API 座標品質分析

### 📝 文件檔案
- **`discussion.md`** - 討論與洞察文件
  - 兩種分析方法的比較
  - 實際應用意義
  - 災害應用中的影響評估
  - 關鍵洞察和結論

### 🔧 Git 設定檔案
- **`.gitignore`** - Git 忽略檔案設定
  - 保護敏感檔案（如 `.env`）
  - 忽略生成的輸出檔案
  - 排除 Python 快取和虛擬環境

### 🚀 使用方式
1. **安裝依賴**：`pip install -r requirements.txt`
2. **設定 API 金鑰**：在 `.env` 檔案中設定 `MOENV_API_KEY`
3. **執行假設分析**：`python crs_analysis.py`
4. **執行正確轉換分析**：`python bonus_correct_crs_conversion.py`
5. **查看結果**：開啟 `output/` 資料夾中的地圖和報告
