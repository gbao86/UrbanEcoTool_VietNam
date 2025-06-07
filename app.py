import streamlit as st
import osmnx as ox
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import nearest_points
import time

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'urban_eco_tool')
}

# TCVN Standards
TCVN_STANDARDS = {
    'special': {
        'total': (12, 15),
        'park': (7, 9),
        'garden': (3, 3.6),
        'street': (1.7, 2.0)
    },
    'type1_2': {
        'total': (10, 12),
        'park': (6, 7.5),
        'garden': (2.5, 2.8),
        'street': (1.9, 2.2)
    },
    'type3_4': {
        'total': (9, 11),
        'park': (5, 7),
        'garden': (2, 2.2),
        'street': (2.0, 2.3)
    },
    'type5': {
        'total': (8, 10),
        'park': (4, 6),
        'garden': (1.6, 1.8),
        'street': (2.0, 2.5)
    }
}

# Tree types by category
TREE_TYPES = {
    'park': [
        {'name': 'Bằng lăng (Lagerstroemia speciosa)', 'space': 25, 'min_distance': 5},
        {'name': 'Sao đen (Hopea odorata)', 'space': 30, 'min_distance': 6},
        {'name': 'Dầu rái (Dipterocarpus alatus)', 'space': 35, 'min_distance': 7},
        {'name': 'Lim xanh (Erythrophleum fordii)', 'space': 30, 'min_distance': 6},
        {'name': 'Sưa đỏ (Dalbergia tonkinensis)', 'space': 25, 'min_distance': 5}
    ],
    'garden': [
        {'name': 'Hoa giấy (Bougainvillea spectabilis)', 'space': 15, 'min_distance': 3},
        {'name': 'Mai vàng (Ochna integerrima)', 'space': 20, 'min_distance': 4},
        {'name': 'Cây bông trang (Ixora coccinea)', 'space': 15, 'min_distance': 3},
        {'name': 'Cây hoa sứ (Plumeria rubra)', 'space': 20, 'min_distance': 4},
        {'name': 'Cây hoa mười giờ (Portulaca grandiflora)', 'space': 10, 'min_distance': 2}
    ],
    'street': [
        {'name': 'Bàng (Terminalia catappa)', 'space': 20, 'min_distance': 4},
        {'name': 'Xà cừ (Khaya senegalensis)', 'space': 25, 'min_distance': 5},
        {'name': 'Phượng vĩ (Delonix regia)', 'space': 25, 'min_distance': 5},
        {'name': 'Sọ khỉ (Samanea saman)', 'space': 30, 'min_distance': 6},
        {'name': 'Cây sấu (Dracontomelon duperreanum)', 'space': 25, 'min_distance': 5}
    ]
}

# Set a different Nominatim server to reduce blocking issues
ox.settings.nominatim_endpoint = "https://nominatim.openstreetmap.de"

def get_db_connection():
    return mysql.connector.connect(**db_config)

def init_db():
    """Khởi tạo database và các bảng cần thiết"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng lịch sử phân tích
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location_name VARCHAR(255) NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            analysis_mode VARCHAR(50) NOT NULL,
            analysis_parameters JSON,
            analysis_date DATETIME NOT NULL,
            suggestion_count INT NOT NULL
        )
    """)
    
    # Tạo bảng đề xuất trồng cây
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tree_planting_suggestions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            analysis_id INT NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            suggested_tree_type VARCHAR(100) NOT NULL,
            reason TEXT NOT NULL,
            priority_score FLOAT NOT NULL,
            estimated_space_sqm FLOAT NOT NULL,
            min_distance_to_other_trees FLOAT NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def save_analysis(location_name, latitude, longitude, analysis_mode, radius, suggestions):
    """Lưu kết quả phân tích vào database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lưu thông tin phân tích
    cursor.execute("""
        INSERT INTO analysis_history 
        (location_name, latitude, longitude, analysis_mode, analysis_parameters, analysis_date, suggestion_count)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
    """, (
        location_name,
        latitude,
        longitude,
        analysis_mode,
        json.dumps({'radius': radius}),
        len(suggestions)
    ))
    
    analysis_id = cursor.lastrowid
    
    # Lưu các điểm đề xuất
    for suggestion in suggestions:
        cursor.execute("""
            INSERT INTO tree_planting_suggestions 
            (analysis_id, latitude, longitude, suggested_tree_type, reason, 
             priority_score, estimated_space_sqm, min_distance_to_other_trees)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            analysis_id,
            suggestion['latitude'],
            suggestion['longitude'],
            suggestion['tree_type'],
            suggestion['reason'],
            suggestion['priority_score'],
            suggestion['space_sqm'],
            suggestion['min_distance']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_analysis_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.*, COUNT(s.id) as suggestion_count
        FROM analysis_history a
        LEFT JOIN tree_planting_suggestions s ON a.id = s.analysis_id
        GROUP BY a.id
        ORDER BY a.analysis_date DESC
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def calculate_distance(point1, point2):
    return point1.distance(point2)

def analyze_area(buildings, green_areas, G, mode, radius, latitude=None, longitude=None):
    suggestions = []
    nodes, edges = ox.graph_to_gdfs(G)
    urban_type = 'type1_2'
    if mode == "Tiêu chuẩn":
        urban_type = 'type1_2'
    elif mode == "Mật độ dày đặc":
        urban_type = 'special'
    else:
        urban_type = 'type3_4'
    standards = TCVN_STANDARDS[urban_type]
    if latitude is not None and longitude is not None:
        center_point = Point(longitude, latitude)
    else:
        center_point = Point(nodes.geometry.x.mean(), nodes.geometry.y.mean())
    buffer = center_point.buffer(radius / 111320)
    buildings_in_buffer = buildings[buildings.geometry.centroid.within(buffer)]
    green_areas_in_buffer = green_areas[green_areas.geometry.centroid.within(buffer)]
    for idx, building in buildings_in_buffer.iterrows():
        building_point = building.geometry.centroid
        nearest_road = None
        min_road_dist = float('inf')
        for _, road in edges.iterrows():
            dist = building_point.distance(road.geometry)
            if dist < min_road_dist:
                min_road_dist = dist
                nearest_road = road
        nearest_green = None
        min_green_dist = float('inf')
        for _, green in green_areas_in_buffer.iterrows():
            dist = building_point.distance(green.geometry)
            if dist < min_green_dist:
                min_green_dist = dist
                nearest_green = green
        # Tính trung điểm giữa nhà và đường
        if nearest_road is not None:
            mid_point_road = Point((building_point.x + nearest_road.geometry.centroid.x) / 2, (building_point.y + nearest_road.geometry.centroid.y) / 2)
        else:
            mid_point_road = None
        # Tính trung điểm giữa nhà và vùng xanh
        if nearest_green is not None:
            mid_point_green = Point((building_point.x + nearest_green.geometry.centroid.x) / 2, (building_point.y + nearest_green.geometry.centroid.y) / 2)
        else:
            mid_point_green = None
        # Tính trung điểm giữa đường và vùng xanh
        if nearest_road is not None and nearest_green is not None:
            mid_point_road_green = Point((nearest_road.geometry.centroid.x + nearest_green.geometry.centroid.x) / 2, (nearest_road.geometry.centroid.y + nearest_green.geometry.centroid.y) / 2)
        else:
            mid_point_road_green = None
        # Chọn điểm đề xuất dựa trên trung điểm
        if mid_point_road is not None and buffer.contains(mid_point_road):
            suggestion_point = mid_point_road
            tree_category = 'street'
            reason = 'Vị trí phù hợp cho cây đường phố, gần đường giao thông'
        elif mid_point_green is not None and buffer.contains(mid_point_green):
            suggestion_point = mid_point_green
            tree_category = 'garden'
            reason = 'Vị trí phù hợp cho vườn hoa, gần khu vực xanh'
        elif mid_point_road_green is not None and buffer.contains(mid_point_road_green):
            suggestion_point = mid_point_road_green
            tree_category = 'park'
            reason = 'Vị trí phù hợp cho công viên, có không gian rộng'
        else:
            continue
        available_trees = TREE_TYPES[tree_category]
        selected_tree = np.random.choice(available_trees)
        priority_score = 0.8
        if min_road_dist > standards['street'][0] and min_road_dist < standards['street'][1]:
            priority_score += 0.1
        if min_green_dist > standards['garden'][0] and min_green_dist < standards['garden'][1]:
            priority_score += 0.1
        space_sqm = selected_tree['space']
        min_distance = selected_tree['min_distance']
        # Thêm điểm đề xuất
        suggestions.append({
            'latitude': suggestion_point.y,
            'longitude': suggestion_point.x,
            'tree_type': selected_tree['name'],
            'reason': reason,
            'priority_score': priority_score,
            'space_sqm': space_sqm,
            'min_distance': min_distance
        })
    return suggestions

def fetch_urban_data(city_name):
    """Fetch urban boundary and green areas for a city."""
    time.sleep(1)  # Add a delay to prevent request blocking
    boundary = ox.geocode_to_gdf(city_name)
    green_tags = {
        "leisure": ["park", "garden"],
        "landuse": ["grass", "meadow"],
        "natural": ["wood", "grassland"]
    }
    green_areas = ox.features_from_place(city_name, tags=green_tags)
    return boundary, green_areas

# Initialize database
init_db()

# Streamlit UI
st.set_page_config(
    page_title="Công Cụ Đề Xuất Chọn Điểm Trồng Cây Xanh Đô Thị Việt Nam",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Công Cụ Đề Xuất Chọn Điểm Trồng Cây Xanh Đô Thị Việt Nam - Urban Greening Site Recommendation Tool for Vietnam")
page = st.sidebar.radio("Chọn chức năng", ["Phân tích", "Lịch sử", "Xem Vùng Đã Phủ Xanh"])

if page == "Phân tích":
    st.title("Phân tích khu vực")
    
    # Location input
    col1, col2 = st.columns(2)
    with col1:
        location_name = st.text_input("Tên địa điểm")
        if location_name:
            geolocator = Nominatim(user_agent="urban_eco_tool")
            location = geolocator.geocode(location_name)
            if location:
                st.session_state.latitude = location.latitude
                st.session_state.longitude = location.longitude
    
    with col2:
        latitude = st.number_input("Vĩ độ", value=st.session_state.get('latitude', 10.762622))
        longitude = st.number_input("Kinh độ", value=st.session_state.get('longitude', 106.660172))
    
    # Analysis parameters
    col3, col4 = st.columns(2)
    with col3:
        analysis_mode = st.selectbox(
            "Chế độ phân tích",
            ["Tiêu chuẩn", "Mật độ dày đặc", "Ngoại ô"]
        )
    
    with col4:
        radius = st.slider("Bán kính phân tích (m)", 100, 2000, 1000, 1)
    
    # Map
    m = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Circle(
        location=[latitude, longitude],
        radius=radius,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.2
    ).add_to(m)
    
    folium_static(m)
    
    # Analysis button
    if st.button("Phân tích"):
        with st.spinner("Đang phân tích..."):
            # Tạo thanh tiến trình
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Bước 1: Lấy dữ liệu OSM
            status_text.text("Đang lấy dữ liệu từ OpenStreetMap...")
            G = ox.graph_from_point((latitude, longitude), dist=radius, network_type='all')
            progress_bar.progress(25)
            
            # Bước 2: Lấy thông tin tòa nhà
            status_text.text("Đang lấy thông tin tòa nhà...")
            buildings = ox.features_from_point((latitude, longitude), tags={'building': True}, dist=radius)
            progress_bar.progress(50)
            
            # Bước 3: Lấy thông tin khu vực xanh
            status_text.text("Đang lấy thông tin khu vực xanh...")
            green_areas = ox.features_from_point((latitude, longitude), tags={'leisure': ['park', 'garden']}, dist=radius)
            progress_bar.progress(75)
            
            # Bước 4: Phân tích và đề xuất
            status_text.text("Đang phân tích và đề xuất vị trí trồng cây...")
            suggestions = analyze_area(buildings, green_areas, G, analysis_mode, radius, latitude, longitude)
            progress_bar.progress(90)
            
            # Bước 5: Lưu kết quả vào database
            status_text.text("Đang lưu kết quả phân tích...")
            analysis_id = save_analysis(location_name, latitude, longitude, analysis_mode, radius, suggestions)
            progress_bar.progress(100)
            
            # Hoàn thành
            status_text.text("Phân tích hoàn tất!")
            
            # Hiển thị kết quả
            st.success(f"Phân tích hoàn tất! Đã tìm thấy {len(suggestions)} vị trí đề xuất.")
            
            # Hiển thị bảng kết quả
            df = pd.DataFrame(suggestions)
            st.dataframe(df)
            
            # Cập nhật bản đồ với các đề xuất
            for suggestion in suggestions:
                folium.Marker(
                    [suggestion['latitude'], suggestion['longitude']],
                    popup=f"{suggestion['tree_type']}<br>{suggestion['reason']}"
                ).add_to(m)
            
            folium_static(m)
            
            # Thêm dòng lưu ý
            st.markdown("---")
            st.markdown("""
            **Lưu ý:** Các thông tin đề xuất trên chỉ mang tính chất tham khảo. Việc quyết định trồng cây cần được xem xét kỹ lưỡng dựa trên:
            - Điều kiện thực tế của địa điểm
            - Khả năng chăm sóc và bảo trì
            - Quy hoạch tổng thể của khu vực
            - Các quy định và tiêu chuẩn hiện hành
            """)
    else:
        st.info("Vui lòng nhập thông tin và bấm nút Phân tích để bắt đầu.")
    
    # Thêm dòng copyright
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} - Nhóm 5 - Lớp 10_ĐH_THMT1")

elif page == "Lịch sử":
    st.title("Lịch sử phân tích")
    
    analyses = get_analysis_history()
    if analyses:
        for analysis in analyses:
            with st.expander(f"{analysis['location_name']} - {analysis['analysis_date'].strftime('%d/%m/%Y %H:%M')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Tọa độ:** {analysis['latitude']}, {analysis['longitude']}")
                    st.write(f"**Chế độ phân tích:** {analysis['analysis_mode']}")
                with col2:
                    try:
                        params = json.loads(analysis['analysis_parameters']) if analysis['analysis_parameters'] else {}
                        radius = params.get('radius', 1000)  # Giá trị mặc định là 1000m
                    except (json.JSONDecodeError, TypeError):
                        radius = 1000
                    st.write(f"**Bán kính:** {radius}m")
                    st.write(f"**Số điểm đề xuất:** {analysis['suggestion_count']}")
                
                # Lấy chi tiết các điểm đề xuất
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM tree_planting_suggestions 
                    WHERE analysis_id = %s 
                    ORDER BY priority_score DESC
                """, (analysis['id'],))
                suggestions = cursor.fetchall()
                cursor.close()
                conn.close()
                
                # Hiển thị bảng chi tiết các điểm đề xuất
                if suggestions:
                    st.subheader("Chi tiết các điểm đề xuất")
                    df = pd.DataFrame(suggestions)
                    # Chọn và đổi tên các cột cần hiển thị
                    display_df = df[['latitude', 'longitude', 'suggested_tree_type', 'reason', 
                                   'priority_score', 'estimated_space_sqm', 'min_distance_to_other_trees']]
                    display_df.columns = ['Vĩ độ', 'Kinh độ', 'Loại cây đề xuất', 'Lý do', 
                                        'Điểm ưu tiên', 'Diện tích (m²)', 'Khoảng cách tối thiểu (m)']
                    st.dataframe(display_df)
                
                # Show analysis map
                m = folium.Map(location=[analysis['latitude'], analysis['longitude']], zoom_start=15)
                folium.Circle(
                    location=[analysis['latitude'], analysis['longitude']],
                    radius=radius,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.2
                ).add_to(m)
                
                # Thêm các điểm đề xuất vào bản đồ
                for suggestion in suggestions:
                    folium.Marker(
                        [suggestion['latitude'], suggestion['longitude']],
                        popup=f"""
                            <b>{suggestion['suggested_tree_type']}</b><br>
                            {suggestion['reason']}<br>
                            Điểm ưu tiên: {suggestion['priority_score']:.2f}<br>
                            Diện tích: {suggestion['estimated_space_sqm']}m²<br>
                            Khoảng cách tối thiểu: {suggestion['min_distance_to_other_trees']}m
                        """
                    ).add_to(m)
                
                folium_static(m)
    else:
        st.info("Chưa có lịch sử phân tích nào.")
    
    # Thêm dòng copyright
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} - Nhóm 5 - Lớp 10_ĐH_THMT1")

else:  # Xem Vùng Đã Phủ Xanh
    st.title("Xem Vùng Đã Phủ Xanh")
    city_name = st.text_input("Nhập tên thành phố:", "Hồ Chí Minh, Việt Nam")
    if st.button("Hiển thị bản đồ"):
        try:
            boundary, green_areas = fetch_urban_data(city_name)
            m = folium.Map(location=[boundary.centroid.y[0], boundary.centroid.x[0]], zoom_start=12)
            folium.GeoJson(boundary, name="Ranh giới đô thị", style_function=lambda x: {"color": "blue"}).add_to(m)
            folium.GeoJson(green_areas, name="Vùng xanh", style_function=lambda x: {"color": "green"}).add_to(m)
            folium.LayerControl().add_to(m)
            folium_static(m)
        except Exception as e:
            st.error(f"Không thể tải dữ liệu cho thành phố này. Lỗi: {str(e)}")
    
    # Thêm dòng copyright
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} - Nhóm 5 - Lớp 10_ĐH_THMT1") 