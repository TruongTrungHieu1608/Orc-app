import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import ImageGrab, Image, ImageTk
import pytesseract
from PIL import Image

class OCRMelamineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Mã Hóa Melamine")
        self.root.geometry("900x700")

        self.setup_ui()

    def setup_ui(self):
        # ===== Button dán ảnh từ clipboard =====
        self.btn_paste = ttk.Button(self.root, text="📋 Dán ảnh từ Clipboard", command=self.paste_image)
        self.btn_paste.pack(pady=10)

        # ===== Frame chứa Canvas + Scrollbar =====
        frame_canvas = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        frame_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Canvas có thể scroll
        self.canvas = tk.Canvas(frame_canvas, bg="#f8f8f8")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar dọc và ngang
        self.scrollbar_y = ttk.Scrollbar(frame_canvas, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(fill=tk.X)
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)

        # Frame chứa ảnh bên trong canvas (để auto scroll)
        self.image_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor="nw")

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        # ===== OCR button =====
        self.btn_ocr = ttk.Button(self.root, text="🔍 Nhận diện chữ", command=self.dummy_ocr)
        self.btn_ocr.pack(pady=10)

        # ===== Text box hiển thị kết quả OCR =====
        self.text_box = scrolledtext.ScrolledText(self.root, height=5, font=("Consolas", 12))
        self.text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=False)

        # ===== Nút sinh mã và kết quả =====
        self.btn_generate_code = ttk.Button(self.root, text="🧠 Sinh mã thành phẩm", command=self.dummy_generate_code)
        self.btn_generate_code.pack(pady=10)

        self.result_label = tk.Label(self.root, text="Mã thành phẩm: Chưa có", font=("Arial", 14, "bold"), fg="blue")
        self.result_label.pack(pady=10)

        # Bắt sự kiện thay đổi kích thước canvas để update scrollregion
        self.canvas.bind("<Configure>", self.update_scrollregion)

    def paste_image(self):
        img = ImageGrab.grabclipboard()
        if img:
            self.original_img = img
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_img)
            self.update_scrollregion()
        else:
            self.image_label.config(text="Không tìm thấy ảnh!", image="", bg="#f8f8f8")

    def update_scrollregion(self, event=None):
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def dummy_ocr(self):
        def real_ocr(self):
            if hasattr(self, 'original_img'):
                # Dùng pytesseract để OCR ảnh
                text = pytesseract.image_to_string(self.original_img)

                # Xoá trắng vùng kết quả và đưa vào lại
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, text.strip())

                # Nếu có Label hiển thị bên ngoài thì cũng update luôn:
                if hasattr(self, 'ocr_result_label'):
                    self.ocr_result_label.config(text=text.strip())
            else:
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, "❌ Chưa có ảnh để nhận diện.")

    def dummy_generate_code(self):
        self.result_label.config(text="Mã thành phẩm: XX18GCAXXXXXXLXTT")

# Khởi chạy app
if __name__ == "__main__":
    root = tk.Tk()
    app = OCRMelamineApp(root)
    root.mainloop()
