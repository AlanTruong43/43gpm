# 43GPM Profile Dashboard

Dashboard quản lý profiles cho phần mềm antidetect 43GPM và chạy các automation projects.

## 🚀 Tính năng

- ✅ Hiển thị danh sách profiles
- 🔍 Tìm kiếm và lọc profiles theo group
- ▶️ Mở/đóng profiles trực tiếp từ dashboard
- 🎯 Chạy automation projects với profile đã chọn
- 📊 Theo dõi trạng thái các profiles đang chạy
- 🎨 Giao diện web đẹp và dễ sử dụng

## 📋 Yêu cầu

- Python 3.8+
- 43GPM phải đang chạy (port 19995)
- ChromeDriver (để chạy Selenium automation)

## 🔧 Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Đảm bảo 43GPM đang chạy trên port 19995

## 🎮 Sử dụng

### Khởi động Dashboard

```bash
streamlit run dashboard.py
```

Dashboard sẽ mở tại: `http://localhost:8501`

### Quy trình làm việc

1. **Tab Profiles**: 
   - Xem danh sách profiles
   - Mở profile cần dùng
   - Kiểm tra thông tin profile

2. **Tab Run Project**:
   - Chọn project cần chạy (twitter.py, instagram.py, etc.)
   - Chọn profile đã mở
   - Click "Run Project"

3. **Tab Status**:
   - Theo dõi profiles đang chạy
   - Xem debug address
   - Đóng profiles khi hoàn thành

## 📁 Cấu trúc project

```
43gpm/
├── api/                        # API documentation
├── project/                    # Folder chứa automation projects
│   ├── twitter.py             # Example: Twitter automation
│   ├── instagram.py           # Your Instagram automation
│   └── linkedin.py            # Your LinkedIn automation
├── api_client.py              # 43GPM API client
├── dashboard.py               # Main dashboard app
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🔨 Tạo automation project mới

Tạo file mới trong folder `project/`, ví dụ `instagram.py`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def run(profile_data):
    """
    Main function - REQUIRED
    
    Args:
        profile_data: Dict with:
            - profile_id: Profile ID
            - profile_name: Profile name
            - remote_debugging_address: Debug address to connect
            - browser_location: Browser executable path
            - driver_path: ChromeDriver path
    """
    # Connect to opened profile
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", 
        profile_data['remote_debugging_address']
    )
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Your automation code here
    driver.get("https://instagram.com")
    time.sleep(2)
    
    # Do your automation tasks...
    
    # DON'T call driver.quit() - let dashboard handle it
    print("Automation completed!")
```

**Lưu ý quan trọng:**
- Function `run(profile_data)` là BẮT BUỘC
- KHÔNG gọi `driver.quit()` - để dashboard quản lý
- Profile browser đã được mở sẵn, chỉ cần connect vào

## 🎯 Ví dụ workflows

### Workflow 1: Run một profile
1. Mở dashboard
2. Vào tab "Profiles"
3. Chọn profile → Click "Open Profile"
4. Vào tab "Run Project"
5. Chọn project (twitter.py)
6. Chọn profile đang chạy
7. Click "Run Project"
8. Sau khi xong, vào tab "Status" → Close profile

### Workflow 2: Run nhiều profiles song song
1. Mở nhiều profiles từ tab "Profiles"
2. Tất cả profiles sẽ xuất hiện trong tab "Run Project"
3. Chọn từng profile và chạy project
4. Quản lý tất cả từ tab "Status"

## 🔐 API Reference

Dashboard sử dụng các API của 43GPM:

- `GET /api/v3/groups` - Lấy danh sách groups
- `GET /api/v3/profiles` - Lấy danh sách profiles
- `GET /api/v3/profiles/start/{id}` - Mở profile
- `GET /api/v3/profiles/close/{id}` - Đóng profile
- `GET /api/v3/profiles/{id}` - Lấy thông tin profile

Chi tiết xem trong folder `api/`

## 🐛 Troubleshooting

### Dashboard không kết nối được với 43GPM
- Kiểm tra 43GPM có đang chạy không
- Kiểm tra port 19995 có bị block không
- Thử truy cập: http://127.0.0.1:19995/api/v3/groups

### Profile không mở được
- Kiểm tra profile có tồn tại không
- Kiểm tra profile có đang được mở bởi process khác không
- Restart 43GPM và thử lại

### Selenium không connect được
- Kiểm tra ChromeDriver version phù hợp với Chrome
- Kiểm tra debug address có đúng không
- Kiểm tra profile đã mở chưa

## 📝 License

Free to use for personal projects.

## 👨‍💻 Support

Nếu có vấn đề, check lại:
1. 43GPM đang chạy
2. Dependencies đã cài đúng
3. Profile đã mở trước khi run project
4. Function `run(profile_data)` có trong project file

