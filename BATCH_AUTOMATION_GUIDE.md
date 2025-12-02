# 🚀 Batch Automation Runner Guide

## Tính năng mới - Clone & Nâng cấp GPM Automation

Dashboard giờ đã có **Batch Automation Runner** - tự động chạy project trên nhiều profiles cùng lúc!

---

## 🎯 TÍNH NĂNG CHÍNH:

### ✅ **Đã Có:**

1. **Multi-Profile Selection** - Chọn nhiều profiles cùng lúc
2. **Auto Open/Close** - Tự động mở và đóng profile
3. **Multi-Threading** - Chạy 1-10 profiles đồng thời
4. **Queue System** - Xử lý profiles theo thứ tự
5. **Individual Logs** - Log riêng cho từng profile
6. **Progress Tracking** - Theo dõi tiến độ real-time
7. **Auto Close on Error** - Tự động đóng profile khi lỗi
8. **Retry Mechanism** - Thử lại khi gặp lỗi
9. **Live Status** - Xem trạng thái từng profile
10. **Error Handling** - Xử lý lỗi tự động

---

## 🚀 CÁCH SỬ DỤNG:

### **Bước 1: Vào Tab "Batch Automation"**

```
Dashboard → Tab "🚀 Batch Automation"
```

### **Bước 2: Cấu hình Automation**

**⚙️ Automation Configuration:**

```
1. Select Project: Chọn project (twitter, instagram, etc.)
2. Number of Threads: Số profiles chạy đồng thời (1-10)
3. Auto Close on Error: ✅ Tự động đóng khi lỗi
4. Retry on Error: Số lần thử lại (0-5)
```

### **Bước 3: Chọn Profiles**

```
📋 Select Profiles:
- Chọn nhiều profiles từ dropdown
- Profiles sẽ chạy theo thứ tự đã chọn
- Có thể chọn tất cả hoặc một phần
```

### **Bước 4: Start Automation**

```
Click "▶️ Start Automation"
→ Automation sẽ tự động:
  1. Mở profile đầu tiên
  2. Chạy project
  3. Đóng profile khi xong
  4. Lặp lại với profile tiếp theo
```

### **Bước 5: Theo dõi Progress**

```
📊 Progress:
- Progress bar: Tiến độ tổng thể
- Metrics: Total, Pending, Running, Completed, Error
- Individual logs: Xem log chi tiết từng profile
```

---

## 📊 GIAO DIỆN:

### **1. Configuration Panel:**

```
⚙️ Automation Configuration
├─ 📁 Select Project: [twitter ▼]
├─ 🔢 Number of Threads: [═══●═══] 5
├─ ❌ Auto Close on Error: [✓]
└─ 🔄 Retry on Error: [0]
```

### **2. Profile Selection:**

```
📋 Select Profiles
[x] concu (ID: 7c089289...)
[x] Profile 1 (ID: abc12345...)
[x] Profile 2 (ID: def67890...)
✅ Selected 3 profile(s)
```

### **3. Control Buttons:**

```
[▶️ Start Automation] [⏹️ Stop] [🗑️ Clear Results] [🔄 Refresh]
```

### **4. Progress Display:**

```
📊 Progress
[████████████████░░░░] 80%

Total: 5   ⏳ Pending: 1   ▶️ Running: 0   ✅ Completed: 3   ❌ Error: 1
```

### **5. Individual Results:**

```
📑 Profile Results

✅ concu - COMPLETED
   Status: completed
   Started: 14:30:25
   Duration: 12.3s
   
   Logs:
   [14:30:25] ℹ️ Opening profile: concu
   [14:30:27] ✅ Profile opened successfully
   [14:30:27] ℹ️ Running project: twitter
   [14:30:37] ✅ Project completed successfully
   [14:30:37] ℹ️ Profile closed

❌ Profile1 - ERROR
   Status: error
   Message: Cannot open profile: Browser version not found
   Started: 14:30:40
   Duration: 3.1s
   
   Logs:
   [14:30:40] ℹ️ Opening profile: Profile1
   [14:30:43] ❌ Failed to open profile: ...
   [14:30:43] ℹ️ Profile closed due to error
```

---

## 🎮 CÁC TÌNH HUỐNG SỬ DỤNG:

### **Tình huống 1: Chạy Twitter automation trên 10 profiles**

```
1. Select Project: twitter
2. Number of Threads: 5 (chạy 5 profiles cùng lúc)
3. Select 10 profiles
4. Click Start
5. Đợi và theo dõi progress
6. Xem kết quả và logs
```

### **Tình huống 2: Test project mới trên nhiều profiles**

```
1. Select Project: new_project
2. Number of Threads: 2 (chạy ít để dễ debug)
3. Auto Close on Error: ✅
4. Retry on Error: 2
5. Select 5 profiles
6. Start và xem logs để debug
```

### **Tình huống 3: Chạy automation ban đêm**

```
1. Chọn tất cả profiles
2. Number of Threads: 10 (tối đa)
3. Retry on Error: 3
4. Start và để chạy
5. Sáng mai check kết quả
```

---

## ⚙️ ADVANCED SETTINGS:

### **Number of Threads:**

```
1 thread   = Chạy tuần tự, chậm nhưng ít tốn tài nguyên
5 threads  = Cân bằng (khuyến nghị)
10 threads = Nhanh nhất nhưng tốn RAM/CPU
```

### **Auto Close on Error:**

```
✅ Enabled  = Profile tự động đóng khi lỗi (khuyến nghị)
❌ Disabled = Profile giữ mở để debug
```

### **Retry on Error:**

```
0 = Không retry
1-2 = Retry cho lỗi tạm thời (network, timeout)
3-5 = Retry nhiều cho lỗi phức tạp
```

---

## 🐛 XỬ LÝ LỖI:

### **Lỗi: Cannot open profile**

```
Nguyên nhân:
- Browser version chưa download
- Profile đang mở ở nơi khác
- 43GPM không chạy

Giải pháp:
- Download browser version trong GPM
- Đóng profile đang mở
- Restart 43GPM
```

### **Lỗi: Project error**

```
Nguyên nhân:
- Lỗi trong code automation
- Timeout
- Element không tìm thấy

Giải pháp:
- Check logs chi tiết của profile
- Fix code trong project file
- Tăng timeout
- Enable retry
```

### **Lỗi: Thread timeout**

```
Nguyên nhân:
- Project chạy quá lâu
- Deadlock

Giải pháp:
- Click Stop để dừng
- Giảm số threads
- Optimize code project
```

---

## 💡 TIPS & TRICKS:

### **1. Tối ưu Performance:**

```
- Chạy 5 threads với profiles có proxy tốt
- Giảm xuống 2-3 threads nếu PC yếu
- Đóng app khác khi chạy nhiều profiles
```

### **2. Debug Hiệu quả:**

```
- Chạy 1 profile trước để test
- Enable Auto Close on Error
- Xem logs chi tiết
- Test lại sau khi fix
```

### **3. Automation Ban đêm:**

```
- Chọn tất cả profiles
- Set max threads
- Enable retry 2-3 lần
- Để chạy qua đêm
```

### **4. Organize Profiles:**

```
- Đặt tên profiles có ý nghĩa
- Group profiles theo mục đích
- Chọn đúng group khi chạy
```

---

## 🔄 SO SÁNH VỚI GPM AUTOMATION:

| Tính năng | GPM Auto | Dashboard Runner |
|-----------|----------|------------------|
| Multi-profile | ✅ | ✅ |
| Multi-threading | ✅ | ✅ |
| Auto open/close | ✅ | ✅ |
| Individual logs | ❌ | ✅ Better |
| Real-time progress | ⚠️ Basic | ✅ Advanced |
| Retry mechanism | ✅ | ✅ |
| Error handling | ✅ | ✅ Better |
| UI/UX | ⚠️ OK | ✅ Modern |
| Custom projects | ❌ | ✅ Flexible |
| Live status | ❌ | ✅ |

---

## 📈 ROADMAP - TÍNH NĂNG SẼ THÊM:

- [ ] **Excel Import** - Import profiles từ Excel
- [ ] **Schedule** - Lên lịch chạy automation
- [ ] **Email Report** - Gửi báo cáo qua email
- [ ] **Webhook** - Gửi thông báo qua webhook
- [ ] **Profile Filtering** - Filter profiles theo tiêu chí
- [ ] **Save Configuration** - Lưu config để tái sử dụng
- [ ] **Export Logs** - Export logs ra file
- [ ] **Statistics** - Thống kê chi tiết
- [ ] **Proxy Rotation** - Tự động đổi proxy khi lỗi
- [ ] **Parallel Projects** - Chạy nhiều projects khác nhau

---

## 🎉 KẾT LUẬN:

Dashboard giờ đã có đầy đủ tính năng **Batch Automation** giống GPM, thậm chí tốt hơn!

**Điểm mạnh:**
- ✅ Logs chi tiết cho từng profile
- ✅ Real-time progress tracking
- ✅ Modern UI/UX
- ✅ Flexible với custom projects
- ✅ Better error handling

**Next steps:**
1. Test với project twitter
2. Tạo thêm projects khác
3. Optimize performance
4. Thêm features mới

Happy Automating! 🚀

