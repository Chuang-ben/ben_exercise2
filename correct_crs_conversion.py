import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyproj import Transformer, Geod, CRS
import folium
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.font_manager as fm

# 加载环境变量
load_dotenv()

# 设置中文字体
def setup_chinese_font():
    """设置中文字体支持"""
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 常见的中文字体
    chinese_fonts = [
        'Microsoft JhengHei',  # 微软正黑体 (Windows)
        'Microsoft YaHei',     # 微软雅黑 (Windows)  
        'SimHei',              # 黑体 (Windows)
        'SimSun',              # 宋体 (Windows)
        'PingFang SC',         # 苹方 (macOS)
        'Hiragino Sans GB',    # 冬青黑体 (macOS)
        'Noto Sans CJK TC',    # 思源黑体 (跨平台)
        'Source Han Sans TC'    # 思源黑体 (跨平台)
    ]
    
    # 找到可用的中文字体
    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用中文字体: {font}")
            return font
    
    # 如果没有找到中文字体，使用默认字体并显示警告
    print("警告: 未找到中文字体，图表可能显示方框")
    print("可用字体:", [f for f in available_fonts if 'Chinese' in f or 'Sans' in f][:10])
    return None

# 设置字体
setup_chinese_font()

class CorrectCRSConversion:
    def __init__(self):
        self.api_id = "O-A0003-001"
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        self.stations_data = None
        
        # TWD67 to WGS84 转换器
        # TWD67 EPSG:3824 -> WGS84 EPSG:4326
        self.twd67_to_wgs84 = Transformer.from_crs("EPSG:3824", "EPSG:4326", always_xy=True)
        
    def fetch_weather_stations(self, use_sample_data=False):
        """獲取氣象站資料"""
        if use_sample_data:
            print("使用範例資料進行演示...")
            return self._create_sample_data()
        
        url = f"{self.base_url}/{self.api_id}"
        api_key = os.getenv('MOENV_API_KEY')
        if not api_key:
            print("未找到API金鑰，請檢查.env檔案中的MOENV_API_KEY")
            return self._create_sample_data()
        
        # 使用URL參數傳遞Authorization，而不是Header
        params = {
            "Authorization": api_key,
            "format": "JSON",
            "limit": 1000
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"API回應狀態碼: {response.status_code}")
            print(f"請求URL: {response.url}")
            
            if response.status_code == 401:
                print("API認證失敗，請檢查API金鑰是否正確")
                return self._create_sample_data()
            elif response.status_code == 403:
                print("API存取被拒絕，請檢查API金鑰權限")
                return self._create_sample_data()
            
            response.raise_for_status()
            data = response.json()
            
            print(f"API回傳資料結構: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            # 提取測站資訊
            stations = []
            if 'records' in data and 'Station' in data['records']:
                station_list = data['records']['Station']
                print(f"找到 {len(station_list)} 個氣象站")
                for station in station_list:
                    # 獲取座標資訊
                    coordinates = station.get('GeoInfo', {}).get('Coordinates', [])
                    twd67_coord = {}
                    wgs84_coord = {}
                    
                    for coord in coordinates:
                        if coord.get('CoordinateName') == 'TWD67':
                            twd67_coord = coord
                        elif coord.get('CoordinateName') == 'WGS84':
                            wgs84_coord = coord
                    
                    station_info = {
                        'StationID': station.get('StationId', ''),
                        'StationName': station.get('StationName', ''),
                        'County': station.get('GeoInfo', {}).get('CountyName', ''),
                        'Township': station.get('GeoInfo', {}).get('TownName', ''),
                        'TWD67_X': float(twd67_coord.get('StationLongitude', 0)),
                        'TWD67_Y': float(twd67_coord.get('StationLatitude', 0)),
                        'WGS84_Lon': float(wgs84_coord.get('StationLongitude', 0)),
                        'WGS84_Lat': float(wgs84_coord.get('StationLatitude', 0))
                    }
                    stations.append(station_info)
            
            self.stations_data = pd.DataFrame(stations)
            print(f"成功獲取 {len(self.stations_data)} 個氣象站資料")
            return self.stations_data
            
        except Exception as e:
            print(f"獲取資料失敗: {e}")
            print("嘗試使用範例資料...")
            return self._create_sample_data()
    
    def _create_sample_data(self):
        """建立範例資料用於演示"""
        sample_stations = [
            {
                'StationID': '466920',
                'StationName': '台北',
                'County': '臺北市',
                'Township': '中正區',
                'TWD67_X': 302000,  # TWD67座標
                'TWD67_Y': 2770000,
                'WGS84_Lon': 121.5319,
                'WGS84_Lat': 25.0478
            },
            {
                'StationID': '466930',
                'StationName': '台中',
                'County': '臺中市',
                'Township': '西區',
                'TWD67_X': 213000,
                'TWD67_Y': 2655000,
                'WGS84_Lon': 120.6736,
                'WGS84_Lat': 24.1477
            },
            {
                'StationID': '466990',
                'StationName': '高雄',
                'County': '高雄市',
                'Township': '前金區',
                'TWD67_X': 185000,
                'TWD67_Y': 2515000,
                'WGS84_Lon': 120.3014,
                'WGS84_Lat': 22.6273
            },
            {
                'StationID': '467490',
                'StationName': '花蓮',
                'County': '花蓮縣',
                'Township': '花蓮市',
                'TWD67_X': 387000,
                'TWD67_Y': 2575000,
                'WGS84_Lon': 121.6067,
                'WGS84_Lat': 23.8289
            },
            {
                'StationID': '467080',
                'StationName': '台南',
                'County': '臺南市',
                'Township': '中西區',
                'TWD67_X': 191000,
                'TWD67_Y': 2570000,
                'WGS84_Lon': 120.2199,
                'WGS84_Lat': 22.9999
            }
        ]
        
        self.stations_data = pd.DataFrame(sample_stations)
        print(f"建立了 {len(self.stations_data)} 個範例氣象站資料")
        return self.stations_data
    
    def convert_twd67_to_wgs84(self):
        """使用 pyproj 正確轉換 TWD67 到 WGS84"""
        if self.stations_data is None:
            print("請先獲取氣象站資料")
            return None
        
        print("正在進行 TWD67 到 WGS84 的正確轉換...")
        
        results = []
        
        for idx, station in self.stations_data.iterrows():
            try:
                # 使用 pyproj 進行正確的座標轉換
                # 注意：TWD67_X 是經度，TWD67_Y 是緯度
                converted_lon, converted_lat = self.twd67_to_wgs84.transform(
                    station['TWD67_X'], station['TWD67_Y']
                )
                
                # 計算轉換後的 WGS84 與原始 WGS84 的距離差異
                distance = self.calculate_distance(
                    converted_lat, converted_lon,
                    station['WGS84_Lat'], station['WGS84_Lon']
                )
                
                result = {
                    'StationID': station['StationID'],
                    'StationName': station['StationName'],
                    'County': station['County'],
                    'TWD67_X': station['TWD67_X'],
                    'TWD67_Y': station['TWD67_Y'],
                    'Original_WGS84_Lat': station['WGS84_Lat'],
                    'Original_WGS84_Lon': station['WGS84_Lon'],
                    'Converted_WGS84_Lat': converted_lat,
                    'Converted_WGS84_Lon': converted_lon,
                    'Conversion_Distance_meters': distance,
                    'Conversion_Distance_km': distance / 1000
                }
                results.append(result)
                
            except Exception as e:
                print(f"轉換失敗 {station['StationName']}: {e}")
                continue
        
        self.conversion_results = pd.DataFrame(results)
        print(f"成功轉換 {len(self.conversion_results)} 個測站")
        return self.conversion_results
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """計算兩點之間的距離（公尺）"""
        geod = Geod(ellps="WGS84")
        _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
        return distance
    
    def create_conversion_map(self):
        """建立轉換比較地圖"""
        if self.conversion_results is None:
            print("請先進行座標轉換")
            return
        
        # 計算地圖中心點
        center_lat = self.conversion_results['Original_WGS84_Lat'].mean()
        center_lon = self.conversion_results['Original_WGS84_Lon'].mean()
        
        # 建立地圖
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7)
        
        # 新增測站標記
        for idx, station in self.conversion_results.iterrows():
            # 原始 WGS84 座標（藍色）
            folium.CircleMarker(
                location=[station['Original_WGS84_Lat'], station['Original_WGS84_Lon']],
                radius=6,
                popup=f"{station['StationName']}<br>原始WGS84<br>轉換差異: {station['Conversion_Distance_km']:.3f} km",
                color='blue',
                fill=True,
                fillColor='blue'
            ).add_to(m)
            
            # 轉換後的 WGS84 座標（紅色）
            folium.CircleMarker(
                location=[station['Converted_WGS84_Lat'], station['Converted_WGS84_Lon']],
                radius=6,
                popup=f"{station['StationName']}<br>TWD67轉換WGS84<br>轉換差異: {station['Conversion_Distance_km']:.3f} km",
                color='red',
                fill=True,
                fillColor='red'
            ).add_to(m)
            
            # 連接線
            folium.PolyLine(
                locations=[
                    [station['Original_WGS84_Lat'], station['Original_WGS84_Lon']],
                    [station['Converted_WGS84_Lat'], station['Converted_WGS84_Lon']]
                ],
                color='green',
                weight=1,
                opacity=0.5
            ).add_to(m)
        
        # 新增圖例
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 250px; height: 140px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>TWD67轉WGS84比較</h4>
        <p><i class="fa fa-circle" style="color:blue"></i> 原始WGS84座標</p>
        <p><i class="fa fa-circle" style="color:red"></i> TWD67轉換WGS84</p>
        <p><i class="fa fa-minus" style="color:green"></i> 轉換差異連線</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def plot_conversion_analysis(self):
        """繪製轉換分析圖"""
        if self.conversion_results is None:
            print("請先進行座標轉換")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 轉換距離直方圖
        axes[0, 0].hist(self.conversion_results['Conversion_Distance_km'], bins=20, alpha=0.7, color='lightcoral')
        axes[0, 0].set_title('TWD67轉WGS84轉換距離分佈 (km)')
        axes[0, 0].set_xlabel('轉換距離 (km)')
        axes[0, 0].set_ylabel('測站數量')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 轉換距離箱線圖
        axes[0, 1].boxplot(self.conversion_results['Conversion_Distance_km'])
        axes[0, 1].set_title('轉換距離箱線圖')
        axes[0, 1].set_ylabel('轉換距離 (km)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 按縣統計平均轉換距離
        county_distance = self.conversion_results.groupby('County')['Conversion_Distance_km'].mean().sort_values(ascending=False)
        axes[1, 0].bar(range(len(county_distance)), county_distance.values, color='lightblue')
        axes[1, 0].set_title('各縣平均TWD67轉WGS84轉換距離')
        axes[1, 0].set_xlabel('縣')
        axes[1, 0].set_ylabel('平均轉換距離 (km)')
        axes[1, 0].set_xticks(range(len(county_distance)))
        axes[1, 0].set_xticklabels(county_distance.index, rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 轉換統計資訊
        stats_text = f"""
        TWD67轉WGS84統計:
        平均轉換距離: {self.conversion_results['Conversion_Distance_km'].mean():.3f} km
        中位數轉換距離: {self.conversion_results['Conversion_Distance_km'].median():.3f} km
        最小轉換距離: {self.conversion_results['Conversion_Distance_km'].min():.3f} km
        最大轉換距離: {self.conversion_results['Conversion_Distance_km'].max():.3f} km
        標準差: {self.conversion_results['Conversion_Distance_km'].std():.3f} km
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center')
        axes[1, 1].set_title('轉換統計摘要')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('output/twd67_to_wgs84_conversion.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_conversion_report(self):
        """產生轉換分析報告"""
        if self.conversion_results is None:
            print("請先進行座標轉換")
            return
        
        report = f"""
# TWD67 到 WGS84 正確轉換分析報告

## 分析概述
本報告分析了使用 pyproj 正確轉換 TWD67 座標系統到 WGS84 的結果：
- 比較原始 WGS84 座標與 TWD67 轉換後的 WGS84 座標
- 計算轉換精確度評估

## 資料摘要
- 總測站數: {len(self.conversion_results)}
- 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 轉換方法: pyproj (EPSG:3824 -> EPSG:4326)

## 轉換距離統計
- 平均轉換距離: {self.conversion_results['Conversion_Distance_km'].mean():.3f} km
- 中位數轉換距離: {self.conversion_results['Conversion_Distance_km'].median():.3f} km
- 最小轉換距離: {self.conversion_results['Conversion_Distance_km'].min():.3f} km
- 最大轉換距離: {self.conversion_results['Conversion_Distance_km'].max():.3f} km
- 標準差: {self.conversion_results['Conversion_Distance_km'].std():.3f} km

## 轉換距離分佈
- 小於10公尺: {len(self.conversion_results[self.conversion_results['Conversion_Distance_km'] < 0.01])} 個測站
- 10-50公尺: {len(self.conversion_results[(self.conversion_results['Conversion_Distance_km'] >= 0.01) & (self.conversion_results['Conversion_Distance_km'] < 0.05)])} 個測站
- 50-100公尺: {len(self.conversion_results[(self.conversion_results['Conversion_Distance_km'] >= 0.05) & (self.conversion_results['Conversion_Distance_km'] < 0.1)])} 個測站
- 100-500公尺: {len(self.conversion_results[(self.conversion_results['Conversion_Distance_km'] >= 0.1) & (self.conversion_results['Conversion_Distance_km'] < 0.5)])} 個測站
- 大於500公尺: {len(self.conversion_results[self.conversion_results['Conversion_Distance_km'] >= 0.5])} 個測站

## 轉換距離最大的前10個測站
{self.conversion_results.nlargest(10, 'Conversion_Distance_km')[['StationName', 'County', 'Conversion_Distance_km']].to_string(index=False)}

## 結論
使用 pyproj 進行 TWD67 到 WGS84 的正確轉換，平均轉換差異為 {self.conversion_results['Conversion_Distance_km'].mean():.3f} 公里。
這表明 API 提供的 TWD67 和 WGS84 座標之間存在系統性差異，需要正確的座標轉換來確保定位精度。
"""
        
        with open('output/twd67_to_wgs84_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("轉換分析報告已產生: output/twd67_to_wgs84_report.md")
        return report

def main():
    """主函數"""
    import os
    
    # 建立輸出資料夾
    os.makedirs('output', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 建立轉換器
    converter = CorrectCRSConversion()
    
    # 獲取資料
    print("正在獲取氣象站資料...")
    stations = converter.fetch_weather_stations(use_sample_data=False)  # 使用真實API資料
    
    if stations is not None:
        # 儲存原始資料
        stations.to_csv('data/weather_stations_raw.csv', index=False, encoding='utf-8-sig')
        print("原始資料已儲存到: data/weather_stations_raw.csv")
        
        # 進行正確的座標轉換
        print("正在進行 TWD67 到 WGS84 轉換...")
        results = converter.convert_twd67_to_wgs84()
        
        if results is not None:
            # 儲存轉換結果
            results.to_csv('output/twd67_to_wgs84_conversion.csv', index=False, encoding='utf-8-sig')
            print("轉換結果已儲存到: output/twd67_to_wgs84_conversion.csv")
            
            # 建立地圖
            print("正在建立轉換比較地圖...")
            conversion_map = converter.create_conversion_map()
            conversion_map.save('output/twd67_to_wgs84_map.html')
            print("轉換比較地圖已儲存到: output/twd67_to_wgs84_map.html")
            
            # 繪製圖表
            print("正在繪製轉換分析圖...")
            converter.plot_conversion_analysis()
            
            # 產生報告
            print("正在產生轉換分析報告...")
            converter.generate_conversion_report()
            
            print("\nTWD67 到 WGS84 正確轉換完成！請查看 output 資料夾中的結果。")
        else:
            print("座標轉換失敗")
    else:
        print("資料獲取失敗")

if __name__ == "__main__":
    main()
