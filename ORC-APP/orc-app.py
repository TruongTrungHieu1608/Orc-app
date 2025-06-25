# Tích hợp OCR từ clipboard + sinh mã thành phẩm Melamine/Laminate
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk, ImageGrab
import pytesseract
import re
import pyperclip

# Cấu hình Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Bản đồ mã hóa chung
TYPE_MAP = {"MDF": "M", "DĂM": "D", "HDF": "H", "VENEER": "V", "ACRYLIC": "A", "PLYWOOD": "P"}
SUPPLIER_MAP = {"ML": "ML", "DA": "DA", "GC": "GC", "DW": "DW"}
PROPERTY_MAP = {"HMR": "H", "THUONG": "A", "CHONG CHAY": "C", "MMR": "M", "CA": "H"}
STANDARD_MAP = {"E0": "0", "E1": "1", "E2": "2", "CARP1": "3", "CARP2": "4"}
SIZE_MAP = {"4X8": "T", "6X8": "L", "4X9": "N"}
COVER_MAP = {"2M": "MM", "1M": "MX", "2L": "LL", "1L": "LX", "2A": "AA", "2V": "VV"}
FILM_MAP = {"T": "T", "G": "G", "SH": "S", "WN": "W", "VI": "V", "D9": "D", "NF": "N", "BS": "B", "SC": "1", "HG": "H", "RM": "R", "V1": "2", "V2": "3", "V3": "4", "V4": "5", "EV": "E", "PL": "P", "C": "C", "F1": "F1", "F2": "F2", "K": "K"}

# Biến toàn cục
current_image = None
image_on_canvas = None

def convert_thickness(thickness):
    try:
        num = float(thickness)
        if abs(num - 5.5) < 0.01:
            return "550"
        if num >= 6:
            return f"{int(num):03d}"
        return f"{int(num * 10):03d}"
    except:
        return "000"

def clean_color(c):
    c = re.sub(r"[^A-Z0-9]", "", c.upper())
    return c[:4].ljust(4, "X")

# Xử lý laminate
def extract_laminate_code(parts):
    code = ""
    code += next((v for k, v in TYPE_MAP.items() if k in parts), 'X')
    
    raw_th = next((p for p in parts if re.fullmatch(r"\d+", p)), '')
    code += convert_thickness(raw_th)
    
    code += next((SUPPLIER_MAP[p] for p in parts if p in SUPPLIER_MAP), 'XX')
    code += next((PROPERTY_MAP[k] for k in PROPERTY_MAP if k in parts), 'A')
    code += next((STANDARD_MAP[k] for k in STANDARD_MAP if k in parts), '1')
    code += next((SIZE_MAP[k] for k in SIZE_MAP if k in parts), 'T')

    # ======= Lớp phủ ========
    covers = [p for p in parts if p in COVER_MAP]
    if len(covers) >= 2:
        cover_code = 'LL'
    elif len(covers) == 1:
        cover_code = 'LX' if covers[0].startswith('1') else 'LL'
    else:
        cover_code = 'LL'
    code += cover_code

    # ======= Màu sắc ========
    colors = []
    for i, p in enumerate(parts):
        if p == 'LAMINATE':
            for j in range(i+1, len(parts)):
                if re.fullmatch(r"\d{1,4}", parts[j]):
                    colors.append(clean_color(parts[j]))
                    if len(colors) == 2:
                        break
    if not colors:
        code += '00000000'
    elif len(colors) == 1:
        code += colors[0] + 'XXXX' if cover_code == 'LX' else colors[0] + colors[0]
    else:
        code += colors[0] + colors[1]

    # ======= Bề mặt film ========
    films = [p for p in parts if p in FILM_MAP]
    if cover_code == 'LX':
        film_code = FILM_MAP[films[-1]] + 'X' if films else 'TX'
    else:
        if len(films) >= 2:
            film_code = FILM_MAP[films[0]] + FILM_MAP[films[1]]
        elif len(films) == 1:
            film_code = FILM_MAP[films[0]] * 2
        else:
            film_code = 'TT'
    code += film_code

    return code

# Hàm xử lý bề mặt Mine + Màu 
def extract_melamine_code(parts):
    code = ""

    # ======= Loại ván + độ dày ========
    code += next((v for k, v in TYPE_MAP.items() if k in parts), 'X')
    raw_th = next((p for p in parts if re.fullmatch(r"\d+(\.\d+)?", p)), '')
    code += convert_thickness(raw_th)

    # ======= NCC + thuộc tính + tiêu chuẩn + khổ ========
    code += next((SUPPLIER_MAP[p] for p in parts if p in SUPPLIER_MAP), 'XX')
    code += next((PROPERTY_MAP[k] for k in PROPERTY_MAP if k in parts), 'A')
    code += next((STANDARD_MAP[k] for k in STANDARD_MAP if k in parts), '1')
    code += next((SIZE_MAP[k] for k in SIZE_MAP if k in parts), 'T')

    # ======= Lớp phủ ========
    covers = [p for p in parts if p in COVER_MAP]
    if len(covers) >= 2:
        cover_code = 'MM'
    elif len(covers) == 1:
        cover_code = 'MX' if covers[0].startswith('1') else 'MM'
    else:
        cover_code = 'MM'
    code += cover_code

    # ======= Màu sắc (sau từ "MINE") ========
    colors = []
    for i, p in enumerate(parts):
        if p == 'MINE':
            for j in range(i + 1, len(parts)):
                if re.fullmatch(r"\d{1,4}", parts[j]):
                    colors.append(clean_color(parts[j]))
                    if len(colors) == 2:
                        break
    if not colors:
        code += '00000000'
    elif len(colors) == 1:
        code += colors[0] + 'XXXX' if cover_code == 'MX' else colors[0] + colors[0]
    else:
        code += colors[0] + colors[1]

    # ======= Bề mặt film ========
    films = [p for p in parts if p in FILM_MAP]
    if cover_code == 'MX':
        film_code = FILM_MAP[films[-1]] + 'X' if films else 'TX'
    else:
        if len(films) >= 2:
            film_code = FILM_MAP[films[0]] + FILM_MAP[films[1]]
        elif len(films) == 1:
            film_code = FILM_MAP[films[0]] * 2
        else:
            film_code = 'TT'
    code += film_code

    return code


# Lỗi hàm xử lý trường hợp 1 mặt Late 1 mặt Mine
def extract_mixed_code(parts):
    code = ""

    # ===== Loại ván + độ dày =====
    code += next((v for k, v in TYPE_MAP.items() if k in parts), 'X')
    raw_th = next((p for p in parts if re.fullmatch(r"\d+(\.\d+)?", p)), '')
    code += convert_thickness(raw_th)

    # Tạm gán NCC
    code += 'XX'

    # ===== Thuộc tính, tiêu chuẩn, size =====
    code += next((PROPERTY_MAP[k] for k in PROPERTY_MAP if k in parts), 'A')
    code += next((STANDARD_MAP[k] for k in STANDARD_MAP if k in parts), '1')
    code += next((SIZE_MAP[k] for k in SIZE_MAP if k in parts), 'T')

    # Lớp phủ hỗn hợp → sẽ là 'ML' hoặc 'LM' tùy mã màu
    cover_code = 'ML'  # placeholder
    code += cover_code

    # ===== Tìm mã màu melamine & laminate =====
    color_mine = '0000'
    color_late = '0000'
    for i, p in enumerate(parts):
        if p == 'MINE':
            for j in range(i+1, len(parts)):
                if re.fullmatch(r'\d{1,4}', parts[j]):
                    color_mine = clean_color(parts[j])
                    break
        if p == 'LAMINATE':
            for j in range(i+1, len(parts)):
                if re.fullmatch(r'\d{1,4}', parts[j]):
                    color_late = clean_color(parts[j])
                    break

    # ===== Chọn NCC dựa trên so sánh mã màu =====
    supplier_code = 'ML' if color_mine < color_late else 'LM'
    code = code[:4] + supplier_code + code[6:]  # gắn vào vị trí NCC
    code = code[:10] + supplier_code  # gắn lại cover_code (ML hoặc LM)

    # ===== Mã màu: MINE + 'X' + LAMINATE =====
    code += color_mine + color_late

    # ===== Film =====
    film_mine = next((FILM_MAP[parts[i+1]] for i, p in enumerate(parts) if p == 'MINE' and i+1 < len(parts) and parts[i+1] in FILM_MAP), 'T')
    film_late = next((FILM_MAP[parts[i+1]] for i, p in enumerate(parts) if p == 'LAMINATE' and i+1 < len(parts) and parts[i+1] in FILM_MAP), 'X')
    code += film_mine + film_late

    return code

def extract_code_from_text(text):
    txt = re.sub(r"[^A-Z0-9\. ]", " ", text.upper())
    parts = txt.split()

    for i in range(len(parts) - 1):
        if parts[i] == 'HMR' and parts[i + 1] == '1':
            parts[i + 1] = 'E1'

    product_name = ' '.join(parts)

    if 'LAMINATE' in parts and 'MINE' in parts:
        return extract_mixed_code(parts), product_name
    elif 'LAMINATE' in parts:
        return extract_laminate_code(parts), product_name
    elif 'MINE' in parts:
        return extract_melamine_code(parts), product_name
    else:
        return 'INVALID', product_name  # hoặc fallback khác tùy anh

def run_gui():
    def get_clipboard_image():
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                return img.convert('RGB')
        except:
            pass
        return None

    def paste_image():
        global current_image, image_on_canvas
        img = get_clipboard_image()
        if img is None:
            messagebox.showwarning('Lỗi', 'Không có ảnh trong clipboard!')
            return
        current_image = img
        canvas.config(scrollregion=(0,0,img.width,img.height))
        tk_img = ImageTk.PhotoImage(img)
        canvas.image = tk_img
        if image_on_canvas:
            canvas.delete(image_on_canvas)
        image_on_canvas = canvas.create_image(0,0,anchor='nw',image=tk_img)
        text_box.delete('1.0', tk.END)

    def do_ocr():
        global current_image
        if not current_image:
            messagebox.showinfo('Thông báo', 'Hãy dán ảnh trước khi nhận diện.')
            return
        text = pytesseract.image_to_string(current_image, lang='eng+vie')
        code, name = extract_code_from_text(text)
        result = f"Mã sản phẩm: {code}\nTên hàng hóa: {name}"
        text_box.delete('1.0', tk.END)
        text_box.insert(tk.END, result)
        pyperclip.copy(result)

    root = tk.Tk()
    root.title('📸 OCR & Sinh mã')
    root.geometry('700x800')
    root.resizable(True, True)

    tk.Label(root, text='📋 Ctrl+C ảnh → Dán → Nhận diện + Sinh mã', font=('Segoe UI',12)).pack(pady=10)
    tk.Button(root, text='📎 Dán từ clipboard', command=paste_image).pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    h_scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    canvas = tk.Canvas(frame, xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set, bg='white')
    h_scroll.config(command=canvas.xview)
    v_scroll.config(command=canvas.yview)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    #current_image = None
    #image_on_canvas = None

    tk.Button(root, text='🧠 Nhận diện + Sinh mã', command=do_ocr).pack(pady=10)
    tk.Label(root, text='📄 Kết quả (auto copy):', font=('Segoe UI',11,'bold'), fg='blue').pack()
    text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=15, font=('Consolas',10))
    text_box.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    run_gui()
