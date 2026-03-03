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

## 檔案說明
- `crs_analysis.py` - 假設分析腳本（將 TWD67 當作 WGS84）
- `correct_crs_conversion.py` - 正確轉換分析腳本（使用 pyproj）
- `requirements.txt` - 依賴套件列表
- `data/` - 資料資料夾
- `output/` - 輸出結果資料夾
- `discussion.md` - 討論文件
