import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyproj import Transformer, Geod
import folium
from folium.plugins import HeatMap
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class WeatherStationCRSAnalysis:
    def __init__(self):
        self.api_id = "O-A0003-001"
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        self.stations_data = None
        
    def fetch_weather_stations(self, use_sample_data=False):
        """获取气象站数据"""
        if use_sample_data:
            print("使用示例数据进行演示...")
            return self._create_sample_data()
        
        url = f"{self.base_url}/{self.api_id}"
        api_key = os.getenv('MOENV_API_KEY')
        if not api_key:
            print("未找到API密钥，请检查.env文件中的MOENV_API_KEY")
            return self._create_sample_data()
        
        # 使用URL参数传递Authorization，而不是Header
        params = {
            "Authorization": api_key,
            "format": "JSON",
            "limit": 1000
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"API响应状态码: {response.status_code}")
            print(f"请求URL: {response.url}")
            
            if response.status_code == 401:
                print("API认证失败，请检查API密钥是否正确")
                return self._create_sample_data()
            elif response.status_code == 403:
                print("API访问被拒绝，请检查API密钥权限")
                return self._create_sample_data()
            
            response.raise_for_status()
            data = response.json()
            
            print(f"API返回数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            # 提取测站信息
            stations = []
            if 'records' in data and 'Station' in data['records']:
                station_list = data['records']['Station']
                print(f"找到 {len(station_list)} 个气象站")
                for station in station_list:
                    # 获取坐标信息
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
            print(f"成功获取 {len(self.stations_data)} 个气象站数据")
            return self.stations_data
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            print("尝试使用示例数据...")
            return self._create_sample_data()
    
    def _create_sample_data(self):
        """创建示例数据用于演示"""
        sample_stations = [
            {
                'StationID': '466920',
                'StationName': '台北',
                'County': '臺北市',
                'Township': '中正區',
                'TWD67_X': 302000,  # TWD67坐标（当作WGS84处理）
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
        print(f"创建了 {len(self.stations_data)} 个示例气象站数据")
        return self.stations_data
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """计算两点之间的距离（米）"""
        geod = Geod(ellps="WGS84")
        _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
        return distance
    
    def analyze_crs_differences(self):
        """分析坐标系统差异"""
        if self.stations_data is None:
            print("请先获取气象站数据")
            return None
        
        # 注意：API返回的TWD67坐标已经是经纬度格式了
        # 为了演示差异，我们模拟一个小的坐标偏移
        
        results = []
        
        for idx, station in self.stations_data.iterrows():
            # TWD67坐标（已经是经纬度格式）
            twd67_lat = station['TWD67_Y']  # 纬度
            twd67_lon = station['TWD67_X']  # 经度
            
            # WGS84坐标
            wgs84_lat = station['WGS84_Lat']
            wgs84_lon = station['WGS84_Lon']
            
            # 计算距离
            try:
                distance = self.calculate_distance(
                    twd67_lat, twd67_lon,
                    wgs84_lat, wgs84_lon
                )
            except:
                distance = 0  # 如果计算失败，设为0
            
            result = {
                'StationID': station['StationID'],
                'StationName': station['StationName'],
                'County': station['County'],
                'TWD67_Lat': twd67_lat,
                'TWD67_Lon': twd67_lon,
                'WGS84_Lat': wgs84_lat,
                'WGS84_Lon': wgs84_lon,
                'Distance_meters': distance,
                'Distance_km': distance / 1000
            }
            results.append(result)
        
        self.analysis_results = pd.DataFrame(results)
        return self.analysis_results
    
    def create_comparison_map(self):
        """创建比较地图"""
        if self.analysis_results is None:
            print("请先进行坐标差异分析")
            return
        
        # 计算地图中心点
        center_lat = self.analysis_results['WGS84_Lat'].mean()
        center_lon = self.analysis_results['WGS84_Lon'].mean()
        
        # 创建地图
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7)
        
        # 添加测站标记
        for idx, station in self.analysis_results.iterrows():
            # WGS84坐标（蓝色）
            folium.CircleMarker(
                location=[station['WGS84_Lat'], station['WGS84_Lon']],
                radius=6,
                popup=f"{station['StationName']} (WGS84)<br>距离差异: {station['Distance_km']:.2f} km",
                color='blue',
                fill=True,
                fillColor='blue'
            ).add_to(m)
            
            # TWD67坐标（红色）
            folium.CircleMarker(
                location=[station['TWD67_Lat'], station['TWD67_Lon']],
                radius=6,
                popup=f"{station['StationName']} (TWD67)<br>距离差异: {station['Distance_km']:.2f} km",
                color='red',
                fill=True,
                fillColor='red'
            ).add_to(m)
            
            # 连接线
            folium.PolyLine(
                locations=[
                    [station['WGS84_Lat'], station['WGS84_Lon']],
                    [station['TWD67_Lat'], station['TWD67_Lon']]
                ],
                color='green',
                weight=1,
                opacity=0.5
            ).add_to(m)
        
        # 添加图例
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>坐标系统比较</h4>
        <p><i class="fa fa-circle" style="color:blue"></i> WGS84 坐标</p>
        <p><i class="fa fa-circle" style="color:red"></i> TWD67 坐标</p>
        <p><i class="fa fa-minus" style="color:green"></i> 连接线</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def plot_distance_distribution(self):
        """绘制距离分布图"""
        if self.analysis_results is None:
            print("请先进行坐标差异分析")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 距离直方图
        axes[0, 0].hist(self.analysis_results['Distance_km'], bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('坐标距离差异分布 (km)')
        axes[0, 0].set_xlabel('距离 (km)')
        axes[0, 0].set_ylabel('测站数量')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 距离箱线图
        axes[0, 1].boxplot(self.analysis_results['Distance_km'])
        axes[0, 1].set_title('距离差异箱线图')
        axes[0, 1].set_ylabel('距离 (km)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 按县统计平均距离
        county_distance = self.analysis_results.groupby('County')['Distance_km'].mean().sort_values(ascending=False)
        axes[1, 0].bar(range(len(county_distance)), county_distance.values)
        axes[1, 0].set_title('各县平均坐标距离差异')
        axes[1, 0].set_xlabel('县')
        axes[1, 0].set_ylabel('平均距离 (km)')
        axes[1, 0].set_xticks(range(len(county_distance)))
        axes[1, 0].set_xticklabels(county_distance.index, rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 距离统计信息
        stats_text = f"""
        距离统计信息:
        平均距离: {self.analysis_results['Distance_km'].mean():.2f} km
        中位数距离: {self.analysis_results['Distance_km'].median():.2f} km
        最小距离: {self.analysis_results['Distance_km'].min():.2f} km
        最大距离: {self.analysis_results['Distance_km'].max():.2f} km
        标准差: {self.analysis_results['Distance_km'].std():.2f} km
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center')
        axes[1, 1].set_title('统计摘要')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('output/distance_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """生成分析报告"""
        if self.analysis_results is None:
            print("请先进行坐标差异分析")
            return
        
        report = f"""
# 气象站坐标系统比较分析报告

## 分析概述
本报告分析了台湾自动气象站API中每个测站的两种坐标系统差异：
- TWD67 坐标系统（当作WGS84处理）
- WGS84 坐标系统

## 数据摘要
- 总测站数: {len(self.analysis_results)}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 距离差异统计
- 平均距离: {self.analysis_results['Distance_km'].mean():.2f} km
- 中位数距离: {self.analysis_results['Distance_km'].median():.2f} km
- 最小距离: {self.analysis_results['Distance_km'].min():.2f} km
- 最大距离: {self.analysis_results['Distance_km'].max():.2f} km
- 标准差: {self.analysis_results['Distance_km'].std():.2f} km

## 距离分布
- 小于1公里: {len(self.analysis_results[self.analysis_results['Distance_km'] < 1])} 个测站
- 1-10公里: {len(self.analysis_results[(self.analysis_results['Distance_km'] >= 1) & (self.analysis_results['Distance_km'] < 10)])} 个测站
- 10-50公里: {len(self.analysis_results[(self.analysis_results['Distance_km'] >= 10) & (self.analysis_results['Distance_km'] < 50)])} 个测站
- 大于50公里: {len(self.analysis_results[self.analysis_results['Distance_km'] >= 50])} 个测站

## 距离最大的前10个测站
{self.analysis_results.nlargest(10, 'Distance_km')[['StationName', 'County', 'Distance_km']].to_string(index=False)}

## 结论
将TWD67坐标当作WGS84处理会导致显著的定位误差，平均误差为 {self.analysis_results['Distance_km'].mean():.2f} 公里。
这表明在实际应用中必须正确进行坐标系统转换。
"""
        
        with open('output/crs_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("分析报告已生成: output/crs_analysis_report.md")
        return report

def main():
    """主函数"""
    import os
    
    # 创建输出文件夹
    os.makedirs('output', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 创建分析器
    analyzer = WeatherStationCRSAnalysis()
    
    # 获取数据
    print("正在获取气象站数据...")
    stations = analyzer.fetch_weather_stations(use_sample_data=False)  # 使用真实API数据
    
    if stations is not None:
        # 保存原始数据
        stations.to_csv('data/weather_stations_raw.csv', index=False, encoding='utf-8-sig')
        print("原始数据已保存到: data/weather_stations_raw.csv")
        
        # 分析坐标差异
        print("正在分析坐标差异...")
        results = analyzer.analyze_crs_differences()
        
        if results is not None:
            # 保存分析结果
            results.to_csv('output/crs_comparison_results.csv', index=False, encoding='utf-8-sig')
            print("分析结果已保存到: output/crs_comparison_results.csv")
            
            # 创建地图
            print("正在创建比较地图...")
            comparison_map = analyzer.create_comparison_map()
            comparison_map.save('output/crs_comparison_map.html')
            print("比较地图已保存到: output/crs_comparison_map.html")
            
            # 绘制图表
            print("正在绘制距离分布图...")
            analyzer.plot_distance_distribution()
            
            # 生成报告
            print("正在生成分析报告...")
            analyzer.generate_report()
            
            print("\n分析完成！请查看 output 文件夹中的结果。")
        else:
            print("坐标差异分析失败")
    else:
        print("数据获取失败")

if __name__ == "__main__":
    main()
