import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import csv
from datetime import datetime

DATA_FILE = "devices.json"
EXPORT_FILE = "devices_export.csv"

STATUSES = ["Работает", "В ремонте", "Списано"]
CRITICALITY = ["Критично", "Некритично"]

DEMO_DATA = [
    {"name":"PC-01","type":"Компьютер","cabinet":"Кабинет 101","status":"В ремонте","critical":"Критично","reason":"Не включается, возможна проблема с БП","responsible":"Иванов А.А.","date":"10.12.2025"},
    {"name":"PC-02","type":"Компьютер","cabinet":"Кабинет 101","status":"Работает","critical":"Некритично","reason":"Плановая проверка","responsible":"Иванов А.А.","date":"05.12.2025"},
    {"name":"Projector-01","type":"Проектор","cabinet":"Кабинет 102","status":"В ремонте","critical":"Критично","reason":"Не работает лампа","responsible":"Петрова О.В.","date":"11.12.2025"},
    {"name":"Printer-01","type":"Принтер","cabinet":"Учительская","status":"Работает","critical":"Некритично","reason":"Замена картриджа","responsible":"Секретарь","date":"01.12.2025"},
    {"name":"Laptop-01","type":"Ноутбук","cabinet":"Кабинет 203","status":"Списано","critical":"Некритично","reason":"Физическое повреждение матрицы","responsible":"Администрация","date":"20.11.2025"},
    {"name":"Router-01","type":"Маршрутизатор","cabinet":"Кабинет 204","status":"В ремонте","critical":"Критично","reason":"Нет подключения к сети","responsible":"Инженер ИКТ","date":"12.12.2025"},
    {"name":"PC-05","type":"Компьютер","cabinet":"Кабинет 205","status":"Работает","critical":"Некритично","reason":"Без неисправностей","responsible":"Учитель математики","date":"02.12.2025"},
    {"name":"InteractiveBoard-01","type":"Интерактивная доска","cabinet":"Кабинет 301","status":"В ремонте","critical":"Критично","reason":"Не реагирует на касания","responsible":"Инженер ИКТ","date":"09.12.2025"},
    {"name":"PC-07","type":"Компьютер","cabinet":"Кабинет 302","status":"Работает","critical":"Некритично","reason":"Обновление ПО","responsible":"Учитель информатики","date":"06.12.2025"},
    {"name":"Printer-03","type":"Принтер","cabinet":"Кабинет директора","status":"В ремонте","critical":"Критично","reason":"Застревание бумаги","responsible":"Администрация","date":"08.12.2025"},
    {"name":"PC-10","type":"Компьютер","cabinet":"Кабинет 303","status":"Работает","critical":"Некритично","reason":"Без замечаний","responsible":"Учитель физики","date":"04.12.2025"},
    {"name":"Server-01","type":"Сервер","cabinet":"Серверная","status":"В ремонте","critical":"Критично","reason":"Перегрев оборудования","responsible":"Системный администратор","date":"12.12.2025"},
    {"name":"Camera-01","type":"Камера видеонаблюдения","cabinet":"Коридор 2 этаж","status":"Работает","critical":"Некритично","reason":"Проверка соединения","responsible":"Охрана","date":"03.12.2025"},
    {"name":"PC-12","type":"Компьютер","cabinet":"Кабинет 401","status":"В ремонте","critical":"Некритично","reason":"Медленная работа","responsible":"Учитель истории","date":"07.12.2025"},
    {"name":"Projector-03","type":"Проектор","cabinet":"Актовый зал","status":"Работает","critical":"Некритично","reason":"Без неисправностей","responsible":"Завхоз","date":"01.12.2025"},
    {"name":"PC-14","type":"Компьютер","cabinet":"Кабинет 402","status":"Списано","critical":"Некритично","reason":"Устаревшее оборудование","responsible":"Администрация","date":"15.11.2025"},
    {"name":"WiFi-AP-02","type":"Точка доступа","cabinet":"Библиотека","status":"В ремонте","critical":"Критично","reason":"Нет сигнала","responsible":"Инженер ИКТ","date":"12.12.2025"},
    {"name":"PC-16","type":"Компьютер","cabinet":"Кабинет 403","status":"Работает","critical":"Некритично","reason":"Без замечаний","responsible":"Учитель биологии","date":"05.12.2025"}
]

class TechAccountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Журнал учёта техники школы")
        self.root.geometry("1180x600")
        self.root.resizable(False, False)

        self.load_data()
        self.create_ui()
        self.update_table()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(DEMO_DATA, f, ensure_ascii=False, indent=4)
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self.devices = json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.devices, f, ensure_ascii=False, indent=4)

    def create_ui(self):
        ttk.Label(self.root, text="Журнал учёта неисправностей", font=("Segoe UI", 14, "bold")).pack(pady=10)

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=15)

        ttk.Label(top, text="Кабинет").pack(side="left")
        self.search_entry = ttk.Entry(top, width=16)
        self.search_entry.pack(side="left", padx=5)

        self.status_filter = ttk.Combobox(top, values=["Все"] + STATUSES, width=14, state="readonly")
        self.status_filter.set("Все")
        self.status_filter.pack(side="left", padx=5)

        self.crit_filter = ttk.Combobox(top, values=["Все"] + CRITICALITY, width=14, state="readonly")
        self.crit_filter.set("Все")
        self.crit_filter.pack(side="left", padx=5)

        ttk.Button(top, text="Фильтр", command=self.search).pack(side="left", padx=5)
        ttk.Button(top, text="Сброс", command=self.reset_search).pack(side="left")
        ttk.Button(top, text="Выгрузить в Excel", command=self.export_excel).pack(side="right")

        columns = ("num","name","type","cabinet","status","critical","reason","responsible","date")
        headers = ["№","Название","Тип","Кабинет","Статус","Критичность","Причина","Ответственный","Дата"]
        widths = [40,120,120,140,110,110,200,140,90]

        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=18)
        for c,h,w in zip(columns,headers,widths):
            self.tree.heading(c,text=h)
            self.tree.column(c,width=w,anchor="center")
        self.tree.pack(padx=15, pady=10)

        self.tree.tag_configure("ok", background="#e2f0d9")
        self.tree.tag_configure("repair", background="#fff2cc")
        self.tree.tag_configure("critical", background="#ffd6d6")
        self.tree.tag_configure("removed", background="#eeeeee")

        btns = ttk.Frame(self.root)
        btns.pack(pady=5)

        ttk.Button(btns, text="Добавить", command=self.add).pack(side="left", padx=5)
        ttk.Button(btns, text="Редактировать", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btns, text="Удалить", command=self.delete).pack(side="left", padx=5)

    def update_table(self, data=None):
        self.tree.delete(*self.tree.get_children())
        data = data if data else self.devices
        for i,d in enumerate(data, start=1):
            tag = "ok"
            if d["status"] == "В ремонте":
                tag = "repair"
            if d["status"] == "Списано":
                tag = "removed"
            if d["critical"] == "Критично":
                tag = "critical"

            self.tree.insert("", "end", values=(
                i, d["name"], d["type"], d["cabinet"], d["status"],
                d["critical"], d["reason"], d["responsible"], d["date"]
            ), tags=(tag,))

    def search(self):
        cab = self.search_entry.get().lower()
        st = self.status_filter.get()
        cr = self.crit_filter.get()
        res = []
        for d in self.devices:
            if cab and cab not in d["cabinet"].lower(): continue
            if st != "Все" and d["status"] != st: continue
            if cr != "Все" and d["critical"] != cr: continue
            res.append(d)
        self.update_table(res)

    def reset_search(self):
        self.search_entry.delete(0, tk.END)
        self.status_filter.set("Все")
        self.crit_filter.set("Все")
        self.update_table()

    def export_excel(self):
        with open(EXPORT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["№","Название","Тип","Кабинет","Статус","Критичность","Причина","Ответственный","Дата"])
            for i,d in enumerate(self.devices, start=1):
                writer.writerow([
                    i,
                    d["name"],
                    d["type"],
                    d["cabinet"],
                    d["status"],
                    d["critical"],
                    d["reason"],
                    d["responsible"],
                    d["date"]
                ])
        messagebox.showinfo("Готово", "Файл сохранён корректно для Excel")

    def add(self): DeviceWindow(self)
    def edit(self):
        if not self.tree.selection(): return
        DeviceWindow(self, self.tree.index(self.tree.selection()[0]))
    def delete(self):
        if not self.tree.selection(): return
        del self.devices[self.tree.index(self.tree.selection()[0])]
        self.save_data()
        self.update_table()

class DeviceWindow:
    def __init__(self, app, idx=None):
        self.app = app
        self.idx = idx
        self.win = tk.Toplevel()
        self.win.title("Запись")
        self.win.geometry("460x420")
        self.inputs = {}

        fields = [
            ("Название","name"),("Тип","type"),("Кабинет","cabinet"),
            ("Статус","status"),("Критичность","critical"),
            ("Причина","reason"),("Ответственный","responsible")
        ]

        for i,(t,k) in enumerate(fields):
            ttk.Label(self.win,text=t).grid(row=i,column=0,padx=10,pady=6,sticky="w")
            if k=="status":
                w=ttk.Combobox(self.win,values=STATUSES,state="readonly")
            elif k=="critical":
                w=ttk.Combobox(self.win,values=CRITICALITY,state="readonly")
            else:
                w=ttk.Entry(self.win,width=35)
            w.grid(row=i,column=1)
            self.inputs[k]=w

        if idx is not None:
            d=self.app.devices[idx]
            for k,v in self.inputs.items():
                v.set(d[k]) if hasattr(v,"set") else v.insert(0,d[k])

        ttk.Button(self.win,text="Сохранить",command=self.save).grid(row=8,columnspan=2,pady=20)

    def save(self):
        d={k:v.get() for k,v in self.inputs.items()}
        if "" in d.values(): return
        d["date"]=datetime.now().strftime("%d.%m.%Y")
        if self.idx is None: self.app.devices.append(d)
        else: self.app.devices[self.idx]=d
        self.app.save_data()
        self.app.update_table()
        self.win.destroy()

if __name__ == "__main__":
    root=tk.Tk()
    TechAccountingApp(root)
    root.mainloop()
