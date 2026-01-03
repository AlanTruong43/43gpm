# 🚀 43GPM External Automation API

Hệ thống điều khiển trình duyệt 43GPM (GPM Login) thông qua API, cho phép tích hợp với các phần mềm bên thứ 3.

## 🛠 Yêu cầu hệ thống
- Python 3.11+
- Các thư viện cần thiết: `pip install fastapi uvicorn selenium requests pydantic`
- Đang chạy phần mềm GPM Login (mặc định tại cổng 19995).

## 📁 Cấu trúc thư mục chính
- `api_server.py`: Server chính (FastAPI) để nhận lệnh.
- `api_client.py`: Client kết nối với API của GPM Login.
- `project/`: Thư mục chứa các kịch bản tự động hóa (ví dụ: `twitter.py`).
- `encoding_fix.py`: Hỗ trợ hiển thị tiếng Việt trên màn hình console Windows.

## 🚀 Cách sử dụng

### 1. Khởi chạy Server
Mở terminal tại thư mục dự án và chạy:
```bash
python api_server.py
```
Server sẽ mặc định chạy tại: `http://127.0.0.1:8000`

### 2. Cách gọi API từ Phần mềm bên thứ 3 (GET Method)

Đây là cách đơn giản nhất để tích hợp. Bạn chỉ cần gọi URL sau:

**Cấu trúc:** `http://127.0.0.1:8000/execute/{tên_script}?profile_id={ID_PROFILE}`

**Ví dụ:**
`http://127.0.0.1:8000/execute/twitter?profile_id=7c089289-cf25-4ca7-bba6-300266979f00`

*   `twitter`: Là tên file `twitter.py` trong thư mục `project/`.
*   `profile_id`: Là ID cố định của profile trong GPM Login.

### 🧠 Luồng xử lý tự động
1. Server nhận được `profile_id`.
2. Server tự hỏi GPM xem profile đó đang chạy ở cổng (port) nào.
3. Server tự tìm đúng `gpmdriver.exe` để điều khiển trình duyệt đó.
4. Server thực thi kịch bản (ví dụ: quét tab, mở Twitter, kiểm tra login).

## 📝 Phát triển kịch bản mới
Để tạo kịch bản mới, hãy tạo một file `.py` trong thư mục `project/` và định nghĩa hàm `run(profile_data)` tương tự như file `twitter.py`.
