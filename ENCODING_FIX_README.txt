========================================
  ENCODING FIX FOR WINDOWS
========================================

VẤN ĐỀ:
--------
Windows console mặc định sử dụng cp1252 (Windows-1252)
encoding, không hỗ trợ Unicode đầy đủ.

Khi print text có ký tự đặc biệt như:
- Tiếng Việt: Đăng nhập, ă, ơ, ư
- Emoji: 🚀, ✅, ❌
- Unicode khác

→ Gây lỗi: UnicodeEncodeError


GIẢI PHÁP:
----------
File encoding_fix.py tự động:
1. Set console encoding thành UTF-8
2. Wrap stdout/stderr với UTF-8 encoding
3. Provide safe_print() và safe_str() functions


SỬ DỤNG:
--------
Chỉ cần import ở đầu file Python:

```python
import encoding_fix  # Must be first import

# Rest of your code...
```

File sẽ tự động fix encoding khi import.


FILES ĐÃ FIX:
-------------
✅ project/twitter.py
✅ automation_runner.py
✅ dashboard.py (không cần vì Streamlit tự handle)


TEST:
-----
Run: python encoding_fix.py

Nếu thấy:
✅ UTF-8 encoding is working!
Testing Unicode: Đăng nhập vào X

→ Encoding đã được fix thành công!


LƯU Ý:
-------
- encoding_fix.py phải được import TRƯỚC tất cả
- Nếu vẫn gặp lỗi, dùng safe_print() thay vì print()
- Nếu cần convert string, dùng safe_str(text)


TROUBLESHOOTING:
----------------
Q: Vẫn bị lỗi encoding?
A: Đảm bảo import encoding_fix đầu tiên

Q: Emoji không hiển thị?
A: Windows console cũ không hỗ trợ
   → Dùng Windows Terminal hoặc VSCode terminal

Q: Muốn disable encoding fix?
A: Comment dòng: import encoding_fix


========================================

