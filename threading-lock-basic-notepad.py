import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import random
import string
import time

class NotepadApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.text_areas = []
        self.current_text = ""  # เก็บข้อความปัจจุบันของหน้าต่างปัจจุบัน
        self.mutex = threading.Lock()  # Mutex lock
        self.bot_running = False  # สถานะการทำงานของ Bot

        self.style = ttk.Style()
        self.style.configure('TButton', padding=(10, 5), font='Helvetica 12')

        open_button = ttk.Button(self.root, text="Open", command=self.open_file)
        open_button.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        save_button = ttk.Button(self.root, text="Save", command=self.save_file)
        save_button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        create_button = ttk.Button(self.root, text="Create Window", command=self.create_window)
        create_button.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        reset_button = ttk.Button(self.root, text="Reset", command=self.reset_text)
        reset_button.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        toggle_bot_button = ttk.Button(self.root, text="Toggle Bot", command=self.toggle_bot)
        toggle_bot_button.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)

    def create_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Text Editor")

        text_area = tk.Text(new_window)
        text_area.pack(fill="both", expand=True)

        # ใส่ข้อมูลใหม่ในหน้าต่างปัจจุบัน
        text_area.insert(tk.END, self.current_text)

        self.text_areas.append({"text_area": text_area, "window": new_window})

        text_area.bind("<KeyRelease>", self.update_text)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_closed(new_window))

    def update_text(self, event):
        updated_text = event.widget.get("1.0", "end-1c")
        with self.mutex:
            for area in self.text_areas:
                if area["text_area"] != event.widget:
                    area["text_area"].delete("1.0", "end")
                    area["text_area"].insert("1.0", updated_text)
            self.current_text = updated_text  # อัปเดตข้อมูลปัจจุบันในหน้าต่างปัจจุบัน

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                with self.mutex:
                    for area in self.text_areas:
                        area["text_area"].delete("1.0", tk.END)
                        area["text_area"].insert(tk.END, content)
                    self.current_text = content  # อัปเดตข้อมูลปัจจุบันในหน้าต่างปัจจุบัน
                # เมื่อเปิดไฟล์เสร็จสิ้น ให้สร้างหน้าต่างใหม่ทันที
                self.create_window()

    def save_file(self):
        text_to_save = self.text_areas[0]["text_area"].get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_to_save)

    def reset_text(self):
        self.current_text = ""  # รีเซ็ตข้อความปัจจุบันในหน้าต่างปัจจุบัน
        with self.mutex:
            for area in self.text_areas:
                area["text_area"].delete("1.0", tk.END)

    def toggle_bot(self):
        self.bot_running = not self.bot_running
        if self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()

    def start_bot(self):
        self.bot_thread = threading.Thread(target=self.bot_task)
        self.bot_thread.daemon = True
        self.bot_thread.start()

    def stop_bot(self):
        pass  # ไม่ต้องทำอะไรเพิ่มเนื่องจากเราให้ bot_thread เป็น daemon thread

    def bot_task(self):
        while self.bot_running:
            random_char = random.choice(string.ascii_letters)
            with self.mutex:
                for area in self.text_areas:
                    area["text_area"].insert(tk.END, random_char)
                    self.current_text = area["text_area"].get("1.0", tk.END)  # อัปเดตข้อมูลปัจจุบัน

            time.sleep(4)  # ปรับเวลาการทำงาน Bot

    def on_window_closed(self, window):
        self.text_areas = [area for area in self.text_areas if area["window"] != window]
        window.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NotepadApp()
    app.run()
