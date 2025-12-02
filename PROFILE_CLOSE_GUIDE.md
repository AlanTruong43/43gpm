# Profile Auto-Close Guide

## 🎯 Tính năng tự động đóng profile

Dashboard automation runner giờ **TỰ ĐỘNG ĐÓNG PROFILE** sau khi hoàn thành hoặc gặp lỗi.

---

## ✅ CƠ CHẾ HOẠT ĐỘNG:

### **1. Khi Project Hoàn Thành:**
```
1. Run automation project
2. Project execute thành công
3. Log: "Project completed successfully"
4. Log: "Closing profile..."
5. Call API close profile
6. Check kết quả:
   ✅ Success → "Profile closed successfully"
   ❌ Failed → Retry 1 lần
   ❌ Fail retry → "Failed to close (manual close required)"
```

### **2. Khi Gặp Lỗi (nếu Auto Close on Error = ✅):**
```
1. Project gặp lỗi
2. Log error details
3. Log: "Closing profile due to error..."
4. Call API close profile
5. Check kết quả tương tự như trên
```

### **3. Retry Mechanism:**
```
Nếu close profile failed:
- Wait 1 second
- Log: "Retrying close..."
- Try close again
- Nếu vẫn fail → Log warning
```

---

## 🔧 CẤU HÌNH:

### **Auto Close on Error:**

```
⚙️ Automation Configuration
[✓] Auto Close on Error  ← Check để bật
```

**Enabled (✓):**
- Profile tự động đóng khi gặp lỗi
- Tiết kiệm RAM
- Tránh profiles bị treo
- **Khuyến nghị cho production**

**Disabled (❌):**
- Profile giữ mở khi lỗi
- Dễ debug
- Có thể inspect browser manually
- **Khuyến nghị khi development**

---

## 📊 LOGS MẪU:

### **Success Case:**
```
[01:15:30] ℹ️ Opening profile: concu
[01:15:32] ✅ Profile opened successfully
[01:15:32] ℹ️ Running project: twitter
[01:15:45] ✅ Project completed successfully
[01:15:45] ℹ️ Closing profile...
[01:15:46] ✅ Profile closed successfully
```

### **Error Case (Auto Close Enabled):**
```
[01:20:10] ℹ️ Opening profile: test_profile
[01:20:12] ✅ Profile opened successfully
[01:20:12] ℹ️ Running project: twitter
[01:20:15] ❌ Error: Element not found
[01:20:15] ⚠️ Closing profile due to error...
[01:20:16] ✅ Profile closed due to error
```

### **Close Failed Case:**
```
[01:25:30] ℹ️ Closing profile...
[01:25:31] ⚠️ Failed to close profile: Profile not found
[01:25:31] ℹ️ Retrying close...
[01:25:32] ⚠️ Failed to close profile (manual close required)
```

---

## 🛠️ TROUBLESHOOTING:

### **Profile không đóng?**

**Kiểm tra:**
1. Xem logs chi tiết trong dashboard
2. Check xem có message "Failed to close"
3. Profile có đang bị stuck không

**Giải pháp:**
```bash
# Option 1: Đóng thủ công trong dashboard
Dashboard → Tab "Status" → Click "Close"

# Option 2: Đóng thủ công trong 43GPM
Mở 43GPM → Click profile → Close

# Option 3: Đóng tất cả profiles
python check_open_profiles.py --close-all
```

### **Nhiều profiles bị mở không đóng?**

**Check open profiles:**
```bash
python check_open_profiles.py
```

Output:
```
CHECKING OPEN PROFILES
==========================================
Total profiles: 10

[CLOSED] profile1
[OPEN]   profile2 (ID: abc123...)
[CLOSED] profile3
[OPEN]   profile4 (ID: def456...)

==========================================
Summary: 2 profile(s) currently OPEN
==========================================
```

**Close all:**
```bash
python check_open_profiles.py --close-all
```

---

## 💡 BEST PRACTICES:

### **Development (Testing Projects):**
```
✅ Auto Close on Error: ❌ Disabled
✅ Threads: 1-2
✅ Manual inspection when error
✅ Close manually when done
```

### **Production (Running Automation):**
```
✅ Auto Close on Error: ✅ Enabled
✅ Threads: 5-10
✅ Retry on Error: 2-3
✅ Let system handle closing
```

### **Batch Testing:**
```
✅ Auto Close on Error: ✅ Enabled
✅ Select nhiều profiles
✅ Run và check logs
✅ System auto close all
```

---

## 🔍 DEBUG CLOSE ISSUES:

### **Nếu profile không đóng được:**

1. **Check logs:**
```
Dashboard → Profile Results → Expand profile → Check logs
```

2. **Manual close:**
```python
from api_client import GPMClient

client = GPMClient()
result = client.close_profile("PROFILE_ID")
print(result)
```

3. **Check GPM:**
```
- Mở 43GPM
- Xem profile list
- Profile có icon đang chạy không?
- Click close manually
```

---

## ⚙️ TECHNICAL DETAILS:

### **Close Profile Flow:**

```python
# In automation_runner.py

# 1. After project completes
self.log_message(profile_id, "Closing profile...", "info")
close_result = self.client.close_profile(profile_id)

# 2. Check result
if close_result.get("success"):
    self.log_message(profile_id, "Profile closed successfully", "success")
else:
    # 3. Retry
    error_msg = close_result.get("message")
    self.log_message(profile_id, f"Failed: {error_msg}", "warning")
    
    time.sleep(1)
    close_result2 = self.client.close_profile(profile_id)
    
    if close_result2.get("success"):
        self.log_message(profile_id, "Closed on retry", "success")
    else:
        self.log_message(profile_id, "Manual close required", "error")
```

### **API Response:**

```json
{
  "success": true,
  "message": "Đóng thành công"
}
```

Or error:
```json
{
  "success": false,
  "message": "Profile không tồn tại"
}
```

---

## 📈 STATISTICS:

Dashboard tracks:
- ✅ Profiles closed successfully
- ⚠️ Profiles failed to close
- ℹ️ Retry attempts
- ❌ Manual close required

Check in logs for each profile.

---

## 🎉 SUMMARY:

**Tính năng Auto Close:**
- ✅ Tự động đóng sau khi hoàn thành
- ✅ Tự động đóng khi lỗi (optional)
- ✅ Retry mechanism
- ✅ Detailed logging
- ✅ Manual fallback

**Best Practice:**
- Development: Disable auto close
- Production: Enable auto close
- Monitor logs
- Use check_open_profiles.py tool

Happy Automating! 🚀

