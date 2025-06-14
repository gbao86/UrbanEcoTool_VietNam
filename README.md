# Urban Eco Tool - Công Cụ Đề Xuất Chọn Điểm Trồng Cây Xanh Đô Thị Việt Nam

## Giới thiệu
Urban Eco Tool là một ứng dụng web được phát triển bằng Streamlit, giúp đề xuất vị trí trồng cây xanh trong đô thị Việt Nam dựa trên các tiêu chuẩn TCVN và dữ liệu không gian địa lý. Ứng dụng sử dụng OpenStreetMap để phân tích không gian đô thị và đưa ra các đề xuất phù hợp cho việc trồng cây.

Dự án này được phát triển dựa trên ý tưởng từ source code mẫu về phân tích không gian xanh đô thị, nhưng đã được mở rộng và nâng cấp đáng kể với nhiều tính năng mới như:
- Phân tích theo tiêu chuẩn TCVN Việt Nam
- Đề xuất loại cây phù hợp cho từng vị trí
- Lưu trữ và quản lý lịch sử phân tích
- Tích hợp cơ sở dữ liệu MySQL
- Giao diện song ngữ Việt-Anh
- Xem vùng đã phủ xanh (tính năng được phát triển từ source code mẫu)

## Tính năng chính
- **Phân tích khu vực**: Phân tích không gian đô thị dựa trên vị trí được chọn
- **Đề xuất vị trí trồng cây**: Đưa ra các đề xuất cụ thể về vị trí và loại cây phù hợp
- **Xem lịch sử phân tích**: Lưu trữ và xem lại các phân tích đã thực hiện
- **Xem vùng đã phủ xanh**: Hiển thị bản đồ các khu vực xanh trong đô thị

## Yêu cầu hệ thống
- Python 3.7+
- MySQL Database
- Các thư viện Python (xem requirements.txt)

## Cài đặt

1. Clone repository:
```bash
git clone [repository-url]
cd UrbanEcoTool
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Tạo file .env với các thông tin cấu hình database:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=urban_eco_tool
```

4. Khởi tạo database:
```bash
python init_db.py
```

5. Chạy ứng dụng:
```bash
streamlit run app.py
```

## Cấu trúc dự án
```
UrbanEcoTool/
├── app.py                  # File chính của ứng dụng Streamlit
├── UrbanEcoTool.py         # Module chính của ứng dụng
├── UrbanEcoTool.ipynb      # Notebook phát triển và kiểm thử
├── requirements.txt        # Danh sách các thư viện cần thiết
├── database_setup.sql      # Script khởi tạo cơ sở dữ liệu
├── run.txt                # File cấu hình chạy ứng dụng
├── static/                # Thư mục chứa tài nguyên tĩnh
├── templates/             # Thư mục chứa template
├── cache/                 # Thư mục cache
├── instance/              # Thư mục chứa dữ liệu instance
└── .devcontainer/         # Cấu hình môi trường phát triển
```

## Công nghệ sử dụng
- **Streamlit**: Framework xây dựng giao diện web
- **OpenStreetMap (OSM)**: Nguồn dữ liệu bản đồ
- **MySQL**: Cơ sở dữ liệu
- **Folium**: Thư viện tạo bản đồ tương tác
- **GeoPandas**: Xử lý dữ liệu không gian địa lý

## Tiêu chuẩn áp dụng
Ứng dụng tuân thủ các tiêu chuẩn TCVN về mật độ cây xanh đô thị, bao gồm:
- Đô thị đặc biệt
- Đô thị loại 1-2
- Đô thị loại 3-4
- Đô thị loại 5

## Đóng góp
Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issue hoặc pull request để đóng góp.

## Giấy phép
This project is licensed under the MIT License - see the [MIT LICENSE](./LICENSE) file for details.

You’re free to use, modify, and distribute this software, but remember to keep the copyright notice intact. No warranties though — use at your own risk! 😎

## Liên hệ
Email: tiktokthu10@gmail.com

## Tham khảo
- Source code tham khảo: [UrbanEcoTool](https://github.com/Rahul-r13/UrbanEcoTool.git) - Một công cụ phân tích và tối ưu hóa không gian xanh đô thị sử dụng OpenStreetMap & GIS data.
