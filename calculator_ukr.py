import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from tkcalendar import DateEntry

HL = {
    '01.01': 'Новий рік', '07.01': 'Різдво', '08.03': '8 Березня',
    '12.04': 'Великдень', '01.05': 'День праці', '09.05': 'День перемоги',
    '31.05': 'Трійця', '28.06': 'День Конституції', '24.08': 'День Незалежності',
    '14.10': 'День захисників', '06.12': 'День ЗСУ'
}

grid_data = []

def calculate_vacation(*args):
    try:
        sd = entry_start.get_date()
        dur = int(entry_duration.get().strip() or 0)
        v_type = combo_type.get()
        
        # Військові ліміти згідно із законодавством
        if "сімейними" in v_type and dur > 10:
            dur = 10; entry_duration.delete(0, tk.END); entry_duration.insert(0, "10")
        elif "заслуги" in v_type and dur > 5:
            dur = 5; entry_duration.delete(0, tk.END); entry_duration.insert(0, "5")
            
        s_dt = datetime.combine(sd, datetime.min.time())
        ed = s_dt + timedelta(days=dur - 1)
        applied = []
        
        if not var_martial.get():
            curr_dt = s_dt
            while curr_dt <= ed:
                if curr_dt.strftime('%d.%m') in HL:
                    applied.append(f"{curr_dt.strftime('%d.%m.%Y')} ({HL[curr_dt.strftime('%d.%m')]})")
                    ed += timedelta(days=1)
                curr_dt += timedelta(days=1)
                
        update_entry(entry_end, ed.strftime("%d.%m.%Y"))
        update_entry(entry_last_work, (s_dt - timedelta(days=1)).strftime("%d.%m.%Y"))
        first_w = ed + timedelta(days=1)
        update_entry(entry_first_work, first_w.strftime("%d.%m.%Y"))
        
        msg = f'Військовослужбовець: {entry_pib.get().strip() or "Не вказано"}\nВид відпустки: {v_type}\nПеріод: {s_dt.strftime("%d.%m.%Y")} - {ed.strftime("%d.%m.%Y")} ({dur} дн.)\n'
        if var_martial.get():
            msg += '⚠️ Воєнний стан: святкові дні НЕ подовжують термін відпустки.\n'
        elif applied:
            msg += f'Подовжено на {len(applied)} дн. через свята:\n' + '\n'.join(applied) + '\n'
        msg += 'Вихідний день.' if first_w.weekday() >= 5 else f'Повернення в частину: {first_w.strftime("%d.%m.%Y")}.'
        
        text_memo.config(state=tk.NORMAL); text_memo.delete('1.0', tk.END); text_memo.insert(tk.END, msg); text_memo.config(state=tk.DISABLED)
    except:
        pass

def update_entry(w, t):
    w.config(state=tk.NORMAL); w.delete(0, tk.END); w.insert(0, t); w.config(state=tk.DISABLED)
def show_grid_window():
    pib_text = entry_pib.get().strip() or 'Військовослужбовець'
    date_range = f"{entry_start.get()}-{entry_end.get()}"
    row_entry = (pib_text, combo_type.get(), entry_duration.get(), date_range)
    grid_data.append(row_entry)
    
    # АВТО-ЛОГГЕР: Запис історії розрахунку у файл логу на диск поруч з EXE
    try:
        with open("log.txt", "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
            log_file.write(f"[{timestamp}] {pib_text} | {combo_type.get()} | {entry_duration.get()} дн. | {date_range}\n")
    except:
        pass
        
    win = tk.Toplevel(root); win.title("Журнал відпусток підрозділу"); win.geometry("520x200"); win.resizable(False, False)
    tree = ttk.Treeview(win, columns=("ПІБ", "Тип", "Дні", "Період"), show="headings", height=6)
    tree.heading("ПІБ", text="Звання / ПІБ"); tree.heading("Тип", text="Вид відпустки"); tree.heading("Дні", text="Дні"); tree.heading("Період", text="Період")
    tree.column("ПІБ", width=150); tree.column("Тип", width=130); tree.column("Дні", width=40); tree.column("Період", width=185); tree.pack(fill="both", expand=True)
    for row in grid_data: tree.insert("", "end", values=row)

def export_report():
    with open('Звіт_Відпусток.txt', 'w', encoding='utf-8') as f:
        f.write("=== ОФІЦІЙНИЙ HD ЗВІТ АРМІЙСЬКОЇ ВІДПУСТКИ ===\n\n")
        f.write(text_memo.get("1.0", tk.END))
    messagebox.showinfo('ОК', 'Рапорт-звіт збережено в файл Звіт_Відпусток.txt')

def val_dur(P): return P == "" or (P.isdigit() and len(P) <= 2)
def val_date(P):
    if P == '' or len(P) > 10 or any(not (c.isdigit() or c == '.') for c in P): return P == ''
    pts = P.split('.'); return not (len(pts) > 3 or (len(pts) >= 1 and pts and (len(pts) > 2 or int(pts) > 31)) or (len(pts) >= 2 and pts and (len(pts) > 2 or int(pts) > 12)) or (len(pts) == 3 and pts and len(pts) > 4))

ds = {
    'Олива 🪖': {'bg': '#556B2F', 'fg': '#FFFFFF', 'lbl': '#556B2F', 'fr_bg': '#C5C1AA', 'fr_fg': '#2F4F4F', 'mem': '#F5F5DC', 'btn': '#D2D7D3', 'm': 'o', 'cal_head': '#3B4732'},
    'Класичний Білий': {'bg': '#E9ECEF', 'fg': '#212529', 'lbl': '#E9ECEF', 'fr_bg': '#FFFFFF', 'fr_fg': '#212529', 'mem': '#F1F3F5', 'btn': '#DEE2E6', 'm': 'n', 'cal_head': '#0A192F'},
    'Глибокий Темний': {'bg': '#121212', 'fg': '#FFFFFF', 'lbl': '#1E1E1E', 'fr_bg': '#1E1E1E', 'fr_fg': '#00FFCC', 'mem': '#2D2D2D', 'btn': '#333333', 'm': 'n', 'cal_head': '#1E1E1E'},
    'Текстура: Піксель': {'bg': '#4D5D43', 'fg': '#E4EAD8', 'lbl': '#3B4732', 'fr_bg': '#627459', 'fr_fg': '#1E2416', 'mem': '#2B3326', 'btn': '#768B6E', 'm': 'p', 'cal_head': '#3B4732'},
    'Текстура: АКМ': {'bg': '#2B261D', 'fg': '#FFD700', 'lbl': '#1C1914', 'fr_bg': '#3D362D', 'fr_fg': '#FFFFFF', 'mem': '#14120E', 'btn': '#4F473B', 'm': 'a', 'cal_head': '#1C1914'},
    'Батюшка у рясі': {'bg': '#0B0C10', 'fg': '#FFD700', 'lbl': '#1F2833', 'fr_bg': '#151B26', 'fr_fg': '#FFD700', 'mem': '#000000', 'btn': '#24303C', 'm': 'b', 'cal_head': '#1F2833'},
    'ЛГБТ Веселка': {'bg': '#FF0000', 'fg': '#FFFFFF', 'lbl': '#FF7F00', 'fr_bg': '#FFED00', 'fr_fg': '#4B0082', 'mem': '#FFFFFF', 'btn': '#00FF00', 'm': 'pr', 'cal_head': '#FF7F00'}
}

def apply_design(n):
    s = ds[n]; root.configure(bg=s['bg']); lbl_info.configure(bg=s['lbl'], fg=s['fg']); frame_group.configure(bg=s['fr_bg'], fg=s['fr_fg'], bd=2)
    for w in frame_group.winfo_children():
        if isinstance(w, tk.Label) or isinstance(w, tk.Checkbutton): w.configure(bg=s['fr_bg'], fg=s['fr_fg'])
    if s['m'] == 'o': frame_group.configure(text=' 🪖 [АРМІЙСЬКА СЕКТОРНА ВІДПУСТКА: ОЛИВА] 🪖 '); lbl_info.configure(text='🪖 Військовий хронограф підрозділу | Базовий захисний стиль Олива 🪖')
    elif s['m'] == 'b': frame_group.configure(text=' ✙ [ТЕКСТУРА: ЗОЛОТІ ХРЕСТИ] ✙ '); lbl_info.configure(text='✙ Духовенство: Контрастний чорно-золотий стиль для військових капеланів ✙')
    elif s['m'] == 'p': frame_group.configure(text=' ▒▒ [РЕАЛІСТИЧНИЙ ПІКСЕЛЬ ЗСУ ММ-14] ▒▒ '); lbl_info.configure(text='▒▒ Оперативний штаб розрахунку | Цифровий армійський піксель ЗСУ ▒▒')
    elif s['m'] == 'a': frame_group.configure(text=' ⚔️ [ТЕКСТУРА: СТАЛЬ АКМ] ⚔️ '); lbl_info.configure(text='⚔️ Тактичний сектор підрахунку часу | Сталеве покриття АКМ ⚔️')
    elif s['m'] == 'pr': frame_group.configure(text=' 🌈 [ФОТО-ТЕМАТИКА: ВЕСЕЛКОВИЙ ПРАПОР] 🌈 '); lbl_info.configure(text='🏳️\u200d🌈 Яскравий і висококонтрастний дизайн інтерфейсу ЛГБТ+ 🏳️\u200d🌈')
    else: frame_group.configure(text=' Параметри відпустки '); lbl_info.configure(text='Розрахувати відпустку можна за будь-яким із представлених параметрів.')
    text_memo.configure(bg=s['mem'], fg='#000000' if s['mem'] in ['#FFFFFF', '#F5F5DC', '#FFF8DC'] else s['fr_fg']); frame_buttons.configure(bg=s['bg'])
    for b in [btn_close, btn_about, btn_style, btn_add, btn_exp]: b.configure(bg=s['btn'], fg='#212529' if s['btn'] in ['#E9ECEF', '#D4D0C8', '#DEE2E6', '#D2D7D3'] else s['fg'])
    entry_start.configure(background=s['cal_head'], headersbackground=s['cal_head'], foreground='white', headersforeground='white')
root = tk.Tk(); root.title('HD Армійський Калькулятор Відпусток'); root.geometry('490x485'); root.resizable(False, False)
v_dur = (root.register(val_dur), '%P'); v_date = (root.register(val_date), '%P'); var_martial = tk.BooleanVar(value=True)

lbl_info = tk.Label(root, text='', wraplength=460, justify='left', font=('Arial', 10, 'bold')); lbl_info.pack(pady=5, padx=15)
frame_group = tk.LabelFrame(root, text='', font=('Arial', 10, 'bold'), padx=10, pady=5); frame_group.pack(fill='x', padx=15, pady=2)

tk.Label(frame_group, text='Звання / ПІБ:', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5)
entry_pib = tk.Entry(frame_group, width=22, font=('Arial', 10, 'bold')); entry_pib.grid(row=0, column=1, pady=3, padx=5, sticky='w')

tk.Label(frame_group, text='Вид відпустки:', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5)
combo_type = ttk.Combobox(frame_group, values=['Основна щорічна 🪖', 'За сімейними обставинами 🏠', 'Лікування / Реабілітація 🏥', 'У зв\'язку з хворобою 🤒', 'Поранення / Контузія 💥', 'За особливі заслуги 🎖️'], width=22, state='readonly', font=('Arial', 9, 'bold'))
combo_type.current(0); combo_type.grid(row=1, column=1, pady=3, padx=5, sticky='w'); combo_type.bind('<<ComboboxSelected>>', calculate_vacation)

tk.Label(frame_group, text='З (включно):', font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5)
entry_start = DateEntry(frame_group, width=16, borderwidth=2, date_pattern='dd.mm.yyyy', locale='uk_UA', validate='key', validatecommand=v_date, font=('Arial', 10, 'bold'))
entry_start.grid(row=2, column=1, pady=3, padx=5, sticky='w'); entry_start.bind("<<DateEntrySelected>>", calculate_vacation); entry_start.bind('<KeyRelease>', calculate_vacation)

tk.Label(frame_group, text='Тривалість (днів):', font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5)
entry_duration = tk.Entry(frame_group, width=6, validate='key', validatecommand=v_dur, font=('Arial', 10, 'bold')); entry_duration.insert(0, '30'); entry_duration.grid(row=3, column=1, pady=3, padx=5, sticky='w'); entry_duration.bind('<KeyRelease>', calculate_vacation)

check_martial = tk.Checkbutton(frame_group, text='Воєнний стан (скасувати свята)', variable=var_martial, font=('Arial', 10, 'bold'), command=calculate_vacation); check_martial.grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=3)

tk.Label(frame_group, text='Останній день в частині:', font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', padx=5)
entry_last_work = tk.Entry(frame_group, width=16, state=tk.DISABLED, font=('Arial', 10, 'bold'), disabledforeground='#212529'); entry_last_work.grid(row=5, column=1, pady=3, padx=5, sticky='w')
tk.Label(frame_group, text='До (включно):', font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', padx=5)
entry_end = tk.Entry(frame_group, width=16, state=tk.DISABLED, font=('Arial', 10, 'bold'), disabledforeground='#212529'); entry_end.grid(row=6, column=1, pady=3, padx=5, sticky='w')
tk.Label(frame_group, text='Повернення в частину:', font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky='w', padx=5)
entry_first_work = tk.Entry(frame_group, width=16, state=tk.DISABLED, font=('Arial', 10, 'bold'), disabledforeground='#212529'); entry_first_work.grid(row=7, column=1, pady=3, padx=5, sticky='w')

text_memo = tk.Text(root, height=4, width=62, font=('Arial', 10, 'bold'), state=tk.DISABLED); text_memo.pack(pady=5, padx=15)

frame_buttons = tk.Frame(root); frame_buttons.pack(side='bottom', fill='x', pady=5, padx=15)
btn_close = tk.Button(frame_buttons, text='Закрити', command=root.quit, width=8, font=('Arial', 10, 'bold')); btn_close.pack(side='left', padx=1)
btn_style = tk.Menubutton(frame_buttons, text='Дизайн...', width=9, font=('Arial', 10, 'bold'), relief='raised')
menu_styles = tk.Menu(btn_style, tearoff=0); btn_style['menu'] = menu_styles
for name in ds.keys(): menu_styles.add_command(label=name, command=lambda n=name: apply_design(n))
btn_style.pack(side='left', padx=1)

btn_add = tk.Button(frame_buttons, text='+ Графік', command=show_grid_window, width=8, font=('Arial', 10, 'bold')); btn_add.pack(side='left', padx=1)
btn_exp = tk.Button(frame_buttons, text='Рапорт', command=export_report, width=8, font=('Arial', 10, 'bold')); btn_exp.pack(side='left', padx=1)
btn_about = tk.Button(frame_buttons, text='Про утиліту', width=11, font=('Arial', 10, 'bold'), command=lambda: messagebox.showinfo('Калькулятор', 'Військовий Комплекс')); btn_about.pack(side='right', padx=1)

apply_design('Олива 🪖'); calculate_vacation(); root.mainloop()
