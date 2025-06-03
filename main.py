import tkinter as tk
from tkinter import messagebox
from encryption import encrypt, decrypt
from crack import analyze_frequency, suggest_key
from dictionary_helper import load_dictionary, extract_suggestions

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("单表代换工具")
        self.geometry("600x500")
        self.frames = {}

        for F in (StartPage, EncryptPage, CrackPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="请选择功能模块：", font=("Helvetica", 16)).pack(pady=40)
        tk.Button(self, text="密钥加解密", width=20,
                  command=lambda: controller.show_frame("EncryptPage")).pack(pady=10)
        tk.Button(self, text="无密钥破译", width=20,
                  command=lambda: controller.show_frame("CrackPage")).pack(pady=10)

class EncryptPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="输入明文或密文：").pack()
        self.input_text = tk.Text(self, height=6)
        self.input_text.pack(fill="x", padx=10)

        tk.Label(self, text="请输入26字母密钥：").pack()
        self.key_entry = tk.Entry(self)
        self.key_entry.pack(fill="x", padx=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="加密", command=self.encrypt).pack(side="left", padx=10)
        tk.Button(button_frame, text="解密", command=self.decrypt).pack(side="left", padx=10)

        tk.Label(self, text="输出结果：").pack()
        self.output_text = tk.Text(self, height=6)
        self.output_text.pack(fill="x", padx=10)

        tk.Button(self, text="返回主页", command=lambda: controller.show_frame("StartPage")).pack(pady=5)

    def encrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip().upper()
        if len(key) != 26 or not key.isalpha():
            messagebox.showerror("密钥错误", "密钥必须是26个字母！")
            return
        result = encrypt(text, key)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

    def decrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip().upper()
        if len(key) != 26 or not key.isalpha():
            messagebox.showerror("密钥错误", "密钥必须是26个字母！")
            return
        result = decrypt(text, key)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

class CrackPage(tk.Frame):
    def __init__(self, parent, controller):
        self.grouped_suggestions = {}
        super().__init__(parent)
        self.controller = controller

        # 加载英文词典
        self.dictionary = load_dictionary("resources/words_dictionary.json")

        # 当前破译映射
        self.current_mapping = {chr(i): None for i in range(65, 91)}  # A-Z

        # 字母替换表 UI（26个Entry）
        self.mapping_entries = {}
        tk.Label(self, text="密文字母：").pack()
        letter_frame = tk.Frame(self)
        letter_frame.pack()

        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            col = tk.Frame(letter_frame)
            col.pack(side="left", padx=1)

            tk.Label(col, text=letter).pack()
            entry = tk.Entry(col, width=2, justify="center")
            entry.insert(0, "")
            entry.bind("<KeyRelease>", lambda e, l=letter: self.update_mapping_from_entry(l))
            entry.pack()
            self.mapping_entries[letter] = entry

        # 输入密文
        tk.Label(self, text="请输入密文（无密钥）：").pack()
        self.input_text = tk.Text(self, height=6)
        self.input_text.pack(fill="x", padx=10)

        # 自动建议按钮
        tk.Button(self, text="自动频率建议", command=self.auto_suggest).pack(pady=5)

        # 输出区
        tk.Label(self, text="当前破译结果：").pack()
        self.output_text = tk.Text(self, height=6)
        self.output_text.pack(fill="x", padx=10)

        # 破译建议区域
        tk.Label(self, text="系统建议：").pack()
        self.suggestion_text = tk.Text(self, height=5, bg="#f0f0f0", fg="blue")
        self.suggestion_text.pack(fill="x", padx=10)
        self.suggestion_text.config(state="disabled")

        # 添加推荐词数量调整控件
        tk.Label(self, text="建议数量：").pack()
        self.suggestion_count = tk.IntVar(value=3)
        spin = tk.Spinbox(self, from_=1, to=10, textvariable=self.suggestion_count, width=5)
        spin.pack()

        # 更稳定地监听建议数量的变更
        self.suggestion_count.trace_add("write", lambda *args: self.update_partial_output())



        # 返回主页
        tk.Button(self, text="返回主页", command=lambda: controller.show_frame("StartPage")).pack(pady=10)

    def auto_suggest(self):
        text = self.input_text.get("1.0", tk.END).strip()
        freq = analyze_frequency(text)
        suggestion = suggest_key(freq)

        top3 = list(suggestion.items())[:5]
        freq_suggestions = [f"{ciph} → {plain}" for ciph, plain in top3]

        self.grouped_suggestions["频率建议"] = freq_suggestions
        self.show_suggestions(self.grouped_suggestions)






    def show_suggestions(self, grouped_suggestions: dict):
        self.suggestion_text.config(state="normal")
        self.suggestion_text.delete("1.0", tk.END)

        if not grouped_suggestions:
            self.suggestion_text.insert(tk.END, "暂无建议")
        else:
            # 手动排序显示顺序：词典 → 频率 → 其他
            priority = ["词典建议", "频率建议"]
            shown = set()

            for key in priority:
                if key in grouped_suggestions:
                    self.suggestion_text.insert(tk.END, f"【{key}】\n")
                    for line in grouped_suggestions[key]:
                        self.suggestion_text.insert(tk.END, f"  - {line}\n")
                    self.suggestion_text.insert(tk.END, "\n")
                    shown.add(key)
        self.suggestion_text.config(state="disabled")

        
    def update_mapping_from_entry(self, cipher_letter):
        val = self.mapping_entries[cipher_letter].get().strip().upper()
        if len(val) == 1 and val.isalpha():
            self.current_mapping[cipher_letter] = val
        elif val == "":
            self.current_mapping[cipher_letter] = None
        self.update_partial_output()

    def update_partial_output(self):
        text = self.input_text.get("1.0", tk.END).strip()
        result = self.get_partial_decryption(text)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

        # 生成建议
        # 获取用户选择的推荐词数量
        max_matches = self.suggestion_count.get()
        dictionary_suggestions = extract_suggestions(result, self.dictionary, max_matches)


        # 更新共享建议字典
        self.grouped_suggestions["词典建议"] = dictionary_suggestions

        # 合并显示所有建议
        self.show_suggestions(self.grouped_suggestions)




    def get_partial_decryption(self, text):
        text = text.upper()
        result = ""
        for char in text:
            if char.isalpha() and self.current_mapping[char]:
                result += self.current_mapping[char]
            elif char.isalpha():
                result += "_"
            else:
                result += char
        return result
   

if __name__ == "__main__":
    app = App()
    app.mainloop()

