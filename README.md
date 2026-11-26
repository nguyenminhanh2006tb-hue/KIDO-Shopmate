# Mẫu chatbot chăm sóc khách hàng (Streamlit + Gemini API)

Mẫu này biến prompt RODES và sổ tay chính sách của nhóm thành một trang chat công khai, miễn phí, trông như một ứng dụng nhắn tin: thanh tiêu đề có ảnh đại diện và tên doanh nghiệp, bóng chat hai bên, giờ gửi, gợi ý trả lời nhanh và nhãn nguồn “Mục …” dưới mỗi câu trả lời. Dùng được cho mọi loại doanh nghiệp. Nhóm **không cần viết code**: chỉ thay hai tệp văn bản, sửa phần cài đặt và dán khóa API của mình.

```
Khách mở link  →  Ứng dụng trên Streamlit (giữ khóa API)  →  Gemini API
```

Khóa API nằm trên máy chủ của Streamlit, khách không bao giờ nhìn thấy.

## Nhóm cần chuẩn bị

- Tài khoản Google (từ 18 tuổi trở lên).
- Tài khoản GitHub miễn phí: github.com.
- Prompt RODES và sổ tay chính sách của cửa hàng nhóm (đã kiểm thử ở bước 6).

## Các tệp trong mẫu

| Tệp | Nhóm làm gì |
| --- | --- |
| `prompt.md` | Thay bằng prompt RODES của nhóm (phần R, O, D, E) |
| `so-tay.md` | Thay bằng sổ tay chính sách của cửa hàng nhóm (định dạng Markdown) |
| `app.py` | Chỉ sửa phần **CÀI ĐẶT** ở đầu tệp |
| `logo.png` (tùy chọn) | Tải lên logo vuông của doanh nghiệp; không có thì ảnh đại diện là chữ cái đầu |
| `.streamlit/config.toml` | Giữ nguyên (phông chữ và giao diện chung) |
| `requirements.txt` | Giữ nguyên |
| `.streamlit/secrets.toml.example` | Mẫu dòng khóa API để sao chép, không sửa |
| `.gitignore` | Giữ nguyên |

## Bước 1. Lấy khóa Gemini API (5 phút)

1. Vào **aistudio.google.com/apikey** và đăng nhập bằng tài khoản Google.
2. Bấm **Create API key**, làm theo hộp thoại.
3. Sao chép khóa và cất ở nơi an toàn (ví dụ trình quản lý mật khẩu).

> Không dán khóa vào `app.py`, `prompt.md`, nhóm chat hay bất kỳ tệp nào trên GitHub. Ai có khóa là dùng được hạn mức của bạn.

## Bước 2. Tạo kho mã (repository) của nhóm (10 phút)

1. Mở link kho mẫu giảng viên gửi.
2. Bấm **Use this template → Create a new repository** (hoặc **Fork**). Đặt tên, ví dụ `chatbot-nhom-3`.
3. Trong kho mới, mở `prompt.md` → biểu tượng bút chì → xóa nội dung cũ → dán prompt của nhóm → **Commit changes**.
4. Làm tương tự với `so-tay.md`.
   - Nếu sổ tay đang ở Google Docs: **Tệp → Tải xuống → Markdown (.md)**, mở tệp bằng Notepad rồi sao chép toàn bộ.
   - Cuối prompt nhóm nên có câu: “Chỉ dùng thông tin trong SỔ TAY CHÍNH SÁCH KHÁCH HÀNG ở cuối hướng dẫn này.” Ứng dụng tự ghép sổ tay vào sau prompt với đúng tiêu đề đó.
5. Mở `app.py`, chỉ sửa khung **CÀI ĐẶT**:

| Dòng | Ý nghĩa | Ví dụ cho một quán ăn |
| --- | --- | --- |
| `TEN_CONG_TY` | Tên doanh nghiệp trên thanh tiêu đề | `"Bếp Nhà Mây"` |
| `TEN_BOT` | Tên trợ lý | `"Mây"` |
| `TRANG_THAI` | Dòng nhỏ dưới tên | `"Trợ lý AI · trả lời trong vài giây"` |
| `LOI_CHAO` | Tin nhắn đầu tiên khách thấy | `"Chào bạn, mình là Mây. Mình giải đáp về thực đơn, đặt bàn và giao món."` |
| `CAU_HOI_GOI_Y` | 2–4 câu hỏi khách bấm để hỏi nhanh | `["Quán mở cửa mấy giờ?", "Đặt bàn thế nào?"]` |
| `GOI_Y_O_NHAP` | Chữ mờ trong ô nhắn tin | `"Nhắn tin"` |
| `HOTLINE` | Số gọi trên thanh tiêu đề và trong câu trả lời lỗi | `"1900 1234"` |
| `MAU_CHU_DAO` | Màu thương hiệu, mã hex (tra trên htmlcolorcodes.com) | `"#C2410C"` |
| `LOGO` | Tên tệp logo trong kho mã | `"logo.png"` |

Giữ nguyên dấu ngoặc kép, dấu phẩy và dấu ngoặc vuông. Không sửa các dòng khác. Chữ trên bóng chat tự chuyển trắng hoặc đen theo màu bạn chọn.

6. Tùy chọn: thêm logo. Trong kho mã, bấm **Add file → Upload files**, tải lên ảnh vuông tên `logo.png` (hoặc đổi dòng `LOGO` cho đúng tên tệp).

> Lời chào, gợi ý và hotline nằm trong `app.py`; còn cách bot trả lời nằm trong `prompt.md`. Nhớ sửa cả hai cho cùng một doanh nghiệp.

## Bước 3. Đưa lên Streamlit Community Cloud (10 phút)

1. Vào **share.streamlit.io**, đăng nhập bằng GitHub và cho phép truy cập kho mã.
2. Bấm **Create app** → chọn kho của nhóm, nhánh `main`, tệp chính `app.py`.
3. Đặt địa chỉ web dễ nhớ, ví dụ `chatbot-nhom-3`.
4. Mở **Advanced settings**, dán vào ô **Secrets** (thay bằng khóa thật của nhóm):

```toml
GEMINI_API_KEY = "dan-khoa-api-cua-ban-vao-day"
```

5. Bấm **Save**, rồi **Deploy**. Lần đầu mất vài phút để cài đặt.
6. Nhóm nhận được đường link dạng `https://chatbot-nhom-3.streamlit.app`, mở được trên điện thoại và máy tính.

Đổi khóa sau này: trang ứng dụng → **⋮ → Settings → Secrets**, sửa rồi **Save**.

## Bước 4. Kiểm thử trên link thật

Chạy lại 10 ca mẫu ở bước 6 trên trang web và chấm bằng rubric 0–2. Kết quả có thể khác khi thử bằng Gemini skill, vì model và cách nạp tài liệu khác nhau. Chỉ gửi link cho người khác khi đạt từ 8/10 ca.

## Khi gặp lỗi

| Hiện tượng | Cách xử lý |
| --- | --- |
| Trang báo “Chưa có khóa API” | Chưa dán khóa vào Secrets, hoặc sai tên. Tên phải đúng là `GEMINI_API_KEY` |
| Bot trả lời “Khóa API không hợp lệ” | Khóa bị dán thiếu ký tự hoặc đã bị xóa. Tạo khóa mới ở AI Studio và dán lại vào Secrets |
| Bot luôn trả lời “Hệ thống đang bận” | Mở **Manage app** ở góc dưới phải → xem dòng `Gemini API error`. Thường do hết hạn mức miễn phí hoặc model đã đổi tên |
| Lỗi do model đã đổi tên hoặc ngừng | Thêm dòng `GEMINI_MODEL = "tên-model-mới"` vào Secrets (xem tên ở trang giá của Google AI Studio) |
| Trang lỗi ngay khi mở, báo thiếu tệp | Kiểm tra `prompt.md` và `so-tay.md` vẫn đúng tên, nằm cùng thư mục với `app.py` |
| Trang lỗi ngay khi mở, báo `SyntaxError` | Phần CÀI ĐẶT thiếu dấu ngoặc kép, dấu phẩy hoặc ngoặc vuông. So lại với bảng ở bước 2 |
| Màu không đổi | `MAU_CHU_DAO` phải là mã hex 6 chữ số có dấu `#`, ví dụ `"#C2410C"` |
| Không có nhãn “Mục …” dưới câu trả lời | Nhãn chỉ hiện khi câu trả lời kết thúc bằng `(Mục …)`. Giữ yêu cầu ghi mục trong `prompt.md` |
| Bot trả lời sai chính sách | Sửa `so-tay.md` hoặc phần D trong `prompt.md` theo bảng chẩn đoán ở bước 6, rồi Commit. Ứng dụng tự cập nhật |

## Giới hạn cần ghi trong báo cáo

- **Đây là bản demo cho lớp học, không dùng cho khách thật.** Ở gói miễn phí, theo điều khoản của Google, người kiểm duyệt có thể đọc nội dung gửi vào API và nội dung được dùng để cải thiện sản phẩm của Google. Không nhập tên, số điện thoại, mã đơn hay thông tin thật.
- **Hạn mức miễn phí có giới hạn** và tính theo dự án; xem tại aistudio.google.com/rate-limit. Mỗi lượt truy cập bị giới hạn 40 tin nhắn để tránh dùng hết hạn mức.
- **Không có nhân viên thật phía sau.** Bot chỉ có thể hướng khách tới hotline.
- **Không dành cho người dưới 18 tuổi**, theo điều khoản Gemini API.
- Muốn chạy thật: chuyển sang gói trả phí của Gemini API hoặc dùng nền tảng chatbot chăm sóc khách hàng thương mại.

## Tùy chọn: chạy thử trên máy trước khi đưa lên

Cần Python 3.10 trở lên.

```bash
pip install -r requirements.txt
```

Tạo tệp `.streamlit/secrets.toml` (không đưa lên GitHub, đã có trong `.gitignore`) chứa dòng `GEMINI_API_KEY = "..."`, rồi chạy:

```bash
streamlit run app.py
```
