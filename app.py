"""Chatbot chăm sóc khách hàng dạng ứng dụng nhắn tin: Streamlit + Gemini API.

Sinh viên chỉ sửa phần CÀI ĐẶT bên dưới, thay nội dung prompt.md và so-tay.md,
rồi dán khóa API vào mục Secrets của Streamlit.
"""

import base64
import html
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
from google import genai

# ============================ CÀI ĐẶT (sinh viên sửa ở đây) ============================
TEN_CONG_TY = "StrideFit"
TEN_BOT = "Stridey"
TRANG_THAI = "Trợ lý AI · trả lời trong vài giây"
LOI_CHAO = "Chào bạn, mình là Stridey, trợ lý AI của StrideFit. Mình giải đáp về đặt hàng, giao hàng, đổi trả và bảo hành."
CAU_HOI_GOI_Y = [
    "Mình có bao lâu để trả hàng?",
    "Phí giao hàng bao nhiêu?",
    "Đổi size có mất phí không?",
]
GOI_Y_O_NHAP = "Nhắn tin"
HOTLINE = "1900 0000"
MAU_CHU_DAO = "#0F6E5C"  # màu thương hiệu, mã hex; chữ trên bóng chat tự đổi trắng/đen cho dễ đọc
LOGO = "logo.png"  # tệp ảnh vuông cùng thư mục; nếu không có, ảnh đại diện là chữ cái đầu của công ty
# =====================================================================================

MODEL_MAC_DINH = "gemini-4-hydrogen"  # model trong hướng dẫn nhanh của Google, có gói miễn phí
SO_TIN_TOI_DA = 40  # giới hạn mỗi lượt truy cập, tránh một người dùng hết hạn mức miễn phí
GIO_VN = timezone(timedelta(hours=7))  # máy chủ Streamlit chạy giờ UTC
THU_MUC = Path(__file__).parent

st.set_page_config(page_title=f"{TEN_BOT} · {TEN_CONG_TY}", page_icon="💬", layout="centered")


def mau_chu_tren(mau_nen):
    """Trả về chữ trắng hoặc gần đen, bên nào tương phản hơn với màu nền."""
    r, g, b = (int(mau_nen.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    sang = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    l = 0.2126 * sang[0] + 0.7152 * sang[1] + 0.0722 * sang[2]
    return "#ffffff" if (1.05 / (l + 0.05)) >= ((l + 0.05) / 0.05) else "#111214"


assert mau_chu_tren("#0F6E5C") == "#ffffff" and mau_chu_tren("#F5C542") == "#111214"

if not re.fullmatch(r"#[0-9A-Fa-f]{6}", MAU_CHU_DAO):  # mã màu gõ sai thì dùng màu mặc định
    MAU_CHU_DAO = "#0F6E5C"
CO_LOGO = bool(LOGO) and (THU_MUC / LOGO).is_file()
CHU_DAI_DIEN = html.escape(TEN_CONG_TY.strip()[:1].upper() or "?")
MAU_CHU = mau_chu_tren(MAU_CHU_DAO)

st.markdown(f"""
<style>
:root {{
  --nhan: {MAU_CHU_DAO}; --chu-tren-nhan: {MAU_CHU};
  --nen: #f4f4f5; --the: #ffffff; --bong-bot: #ececee; --duong: rgba(17,18,20,.08);
  --chu: #17181a; --chu-phu: #55575d; --chu-mo: #74767c;
  --cong: cubic-bezier(.22,1,.36,1);
}}
.stApp {{ background: var(--nen); }}
header[data-testid="stHeader"] {{ display: none; }}
.block-container {{ padding: 0 16px 24px; max-width: 760px; }}

/* Thanh tiêu đề cuộc trò chuyện */
.dau-chat {{ position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 12px;
  margin: 0 -16px 8px; padding: 12px 16px; background: var(--the); border-bottom: 1px solid var(--duong); }}
.dai-dien {{ width: 40px; height: 40px; border-radius: 50%; flex: none; display: grid; place-items: center;
  background: var(--nhan); color: var(--chu-tren-nhan); font-weight: 600; font-size: 17px; overflow: hidden; }}
.dai-dien img {{ width: 100%; height: 100%; object-fit: cover; }}
.dau-chat .chu {{ min-width: 0; }}
.dau-chat .ten, .dau-chat .trang-thai {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.dau-chat .ten {{ font-size: 16px; font-weight: 600; color: var(--chu); line-height: 20px; }}
.dau-chat .trang-thai {{ font-size: 13px; color: var(--chu-mo); line-height: 18px; display: flex; align-items: center; gap: 6px; }}
.dau-chat .cham {{ width: 8px; height: 8px; border-radius: 50%; background: #16a34a; }}
.dau-chat .trang-thai {{ display: block; }}
.dau-chat .cham {{ display: inline-block; margin-right: 6px; vertical-align: 1px; }}
.dau-chat .goi {{ margin-left: auto; flex: none; white-space: nowrap; font-size: 13px; color: var(--chu-phu); text-decoration: none;
  padding: 6px 12px; border: 1px solid var(--duong); border-radius: 8px; transition: background-color .15s var(--cong); }}
.dau-chat .goi:hover {{ background: var(--nen); }}
.ngay {{ text-align: center; font-size: 12px; color: var(--chu-mo); margin: 8px 0 12px; }}

/* Bóng chat: dựa trên st.chat_message của Streamlit 1.67 */
[data-testid="stChatMessage"] {{ background: transparent !important; padding: 2px 0; gap: 8px; align-items: flex-end; }}
[data-testid="stChatMessageContent"] {{ max-width: 78%; flex: 0 1 auto; margin: 0 !important; padding: 8px 14px; border-radius: 18px;
  background: var(--bong-bot); color: var(--chu); }}
[data-testid="stChatMessageContent"] p {{ font-size: 15px; line-height: 22px; margin: 0 0 6px; }}
[data-testid="stChatMessageContent"] p:last-child {{ margin-bottom: 0; }}
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{ flex-direction: row-reverse; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
  background: var(--nhan); color: var(--chu-tren-nhan); }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] * {{
  color: var(--chu-tren-nhan); }}
[data-testid="stChatMessageAvatarUser"] {{ display: none; }}
[data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarCustom"] {{
  width: 28px; height: 28px; min-width: 28px; border-radius: 50%; background: var(--nhan); color: var(--chu-tren-nhan); }}
[data-testid="stChatMessageAvatarCustom"] img {{ border-radius: 50%; }}
.meta {{ display: flex; align-items: center; gap: 6px; margin-top: 4px; font-size: 12px; line-height: 16px; color: var(--chu-mo); }}
.nguon {{ font-size: 12px; padding: 1px 8px; border-radius: 6px; background: var(--the);
  border: 1px solid var(--duong); color: var(--chu-phu); font-variant-numeric: tabular-nums; }}
.dang-go {{ display: inline-flex; gap: 4px; padding: 6px 2px; }}
.dang-go span {{ width: 6px; height: 6px; border-radius: 50%; background: var(--chu-mo); opacity: .4;
  animation: go 1.2s var(--cong) infinite; }}
.dang-go span:nth-child(2) {{ animation-delay: .15s; }} .dang-go span:nth-child(3) {{ animation-delay: .3s; }}
@keyframes go {{ 0%, 60%, 100% {{ opacity: .4; transform: none; }} 30% {{ opacity: 1; transform: translateY(-2px); }} }}

/* Gợi ý trả lời nhanh */
.st-key-goi-y {{ padding-left: 36px; gap: 8px; }}
.st-key-goi-y button {{ border-radius: 18px; min-height: 36px; padding: 6px 14px; background: var(--the);
  border: 1px solid var(--nhan); color: var(--chu); font-size: 14px;
  transition: background-color .15s var(--cong), transform .15s var(--cong); }}
.st-key-goi-y button:hover {{ background: color-mix(in srgb, var(--nhan) 10%, var(--the)); border-color: var(--nhan); color: var(--chu); }}
.st-key-goi-y button:active {{ transform: scale(.98); }}
.st-key-goi-y button p {{ font-size: 14px; }}

/* Ô nhắn tin */
[data-testid="stBottom"] > div {{ background: var(--nen); }}
[data-testid="stChatInput"] > div {{ border-radius: 22px; background: var(--the); border: 1px solid var(--duong); }}
[data-testid="stChatInput"]:focus-within > div {{ border-color: var(--nhan); }}
[data-testid="stChatInputSubmitButton"] {{ background: var(--nhan) !important; color: var(--chu-tren-nhan) !important; border-radius: 50%; }}
.chu-thich {{ text-align: center; font-size: 12px; line-height: 16px; color: var(--chu-mo); margin-top: 16px; }}
</style>
""", unsafe_allow_html=True)


def doc_bi_mat(ten, mac_dinh=None):
    try:
        return st.secrets.get(ten, mac_dinh)
    except FileNotFoundError:  # chạy trên máy mà chưa có .streamlit/secrets.toml
        return mac_dinh


KHOA_API = doc_bi_mat("GEMINI_API_KEY")
MODEL = doc_bi_mat("GEMINI_MODEL", MODEL_MAC_DINH)

if CO_LOGO:
    kieu = "svg+xml" if LOGO.lower().endswith(".svg") else "jpeg" if LOGO.lower().endswith((".jpg", ".jpeg")) else "png"
    du_lieu = base64.b64encode((THU_MUC / LOGO).read_bytes()).decode()
    dai_dien_html = f'<div class="dai-dien"><img src="data:image/{kieu};base64,{du_lieu}" alt=""></div>'
else:
    dai_dien_html = f'<div class="dai-dien">{CHU_DAI_DIEN}</div>'
st.markdown(f"""
<div class="dau-chat">
  {dai_dien_html}
  <div class="chu">
    <div class="ten">{html.escape(TEN_BOT)} · {html.escape(TEN_CONG_TY)}</div>
    <div class="trang-thai"><span class="cham"></span>{html.escape(TRANG_THAI)}</div>
  </div>
  <a class="goi" href="tel:{html.escape(HOTLINE.replace(' ', ''))}">Gọi {html.escape(HOTLINE)}</a>
</div>
""", unsafe_allow_html=True)

if not KHOA_API:
    st.error("Chưa có khóa API. Vào **Settings → Secrets** của ứng dụng trên Streamlit "
             "và dán dòng: `GEMINI_API_KEY = \"khóa-của-bạn\"` rồi bấm **Save**.")
    st.stop()


@st.cache_resource
def tao_client(khoa):
    return genai.Client(api_key=khoa)


@st.cache_data
def tao_huong_dan():
    prompt = (THU_MUC / "prompt.md").read_text(encoding="utf-8")
    so_tay = (THU_MUC / "so-tay.md").read_text(encoding="utf-8")
    return f"{prompt}\n\nSỔ TAY CHÍNH SÁCH KHÁCH HÀNG\n\n{so_tay}"


client = tao_client(KHOA_API)
HUONG_DAN = tao_huong_dan()
ANH_BOT = str(THU_MUC / LOGO) if CO_LOGO else ":material/support_agent:"
TRICH_MUC = re.compile(r"\s*\((Mục[^()]*)\)\s*$")


def bay_gio():
    return datetime.now(GIO_VN).strftime("%H:%M")


def hien_tin(vai, noi_dung, gio):
    nguon = ""
    if vai == "assistant" and (m := TRICH_MUC.search(noi_dung)):
        noi_dung, nguon = noi_dung[:m.start()], f'<span class="nguon">{html.escape(m.group(1))}</span>'
    with st.chat_message(vai, avatar=ANH_BOT if vai == "assistant" else None):
        st.markdown(noi_dung)
    canh = "flex-end" if vai == "user" else "flex-start; padding-left:36px"
    st.markdown(f'<div class="meta" style="justify-content:{canh}">{nguon}<span>{gio}</span></div>',
                unsafe_allow_html=True)


if "tin_nhan" not in st.session_state:
    st.session_state.tin_nhan = [{"vai": "assistant", "noi_dung": LOI_CHAO, "gio": bay_gio()}]
    st.session_state.ma_luot_truoc = None

st.markdown('<div class="ngay">Hôm nay</div>', unsafe_allow_html=True)
for tin in st.session_state.tin_nhan:
    hien_tin(tin["vai"], tin["noi_dung"], tin["gio"])

cau_hoi = None
if len(st.session_state.tin_nhan) == 1 and CAU_HOI_GOI_Y:
    with st.container(key="goi-y", horizontal=True):
        for i, goi_y in enumerate(CAU_HOI_GOI_Y):
            if st.button(goi_y, key=f"goi-y-{i}"):
                cau_hoi = goi_y

if len(st.session_state.tin_nhan) >= SO_TIN_TOI_DA:
    st.info(f"Cuộc trò chuyện đã dài. Bạn tải lại trang để bắt đầu lại hoặc gọi {HOTLINE} nhé.")
    st.stop()

cau_hoi = st.chat_input(GOI_Y_O_NHAP, max_chars=500) or cau_hoi

if cau_hoi:
    st.session_state.tin_nhan.append({"vai": "user", "noi_dung": cau_hoi, "gio": bay_gio()})
    hien_tin("user", cau_hoi, bay_gio())

    yeu_cau = {"model": MODEL, "system_instruction": HUONG_DAN, "input": cau_hoi}
    if st.session_state.ma_luot_truoc:
        yeu_cau["previous_interaction_id"] = st.session_state.ma_luot_truoc

    dang_go = st.empty()
    with dang_go.container():
        with st.chat_message("assistant", avatar=ANH_BOT):
            st.markdown('<div class="dang-go"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
    try:
        ket_qua = client.interactions.create(**yeu_cau)
        tra_loi = ket_qua.output_text
        st.session_state.ma_luot_truoc = ket_qua.id
    except Exception as loi:
        print("Gemini API error:", ascii(loi))  # xem trong Manage app → logs; ascii() để không lỗi trên Windows
        if "API_KEY_INVALID" in str(loi):
            tra_loi = "Khóa API không hợp lệ. Chủ ứng dụng hãy kiểm tra lại GEMINI_API_KEY trong Secrets."
        else:
            tra_loi = f"Hệ thống đang bận. Bạn thử lại sau hoặc gọi hotline {HOTLINE} nhé."
    st.session_state.tin_nhan.append({"vai": "assistant", "noi_dung": tra_loi, "gio": bay_gio()})
    st.rerun()

st.markdown('<div class="chu-thich">Bạn đang nhắn với trợ lý AI. Bản demo cho lớp học: '
            'không gửi số thẻ, mật khẩu, mã OTP hay thông tin cá nhân thật.</div>', unsafe_allow_html=True)
