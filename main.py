import flet as ft
from datetime import datetime, timedelta
import os

def main(page: ft.Page):
    page.title = "Армійський Калькулятор"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.DARK
    page.background_color = "#3B4732" 
    
    # Адаптуємо розміри вікна (діє лише на ПК, на Android ігнорується)
    page.window_width = 450
    page.window_height = 750

    HL = {'01.01': 'Новий рік', '07.01': 'Різдво', '08.03': '8 Березня', '12.04': 'Великдень', '01.05': 'День праці', '09.05': 'День перемоги', '31.05': 'Трійця', '28.06': 'День Конституції', '24.08': 'День Незалежності', '06.12': 'День ЗСУ'}

    def do_calc(e):
        try:
            if not txt_dur.value or not txt_date.value: return
            dur = int(txt_dur.value)
            if "сімейними" in combo_type.value and dur > 10:
                dur = 10; txt_dur.value = "10"
            elif "заслуги" in combo_type.value and dur > 5:
                dur = 5; txt_dur.value = "5"
                
            sd = datetime.strptime(txt_date.value, "%d.%m.%Y")
            ed = sd + timedelta(days=dur - 1)
            applied = []
            
            if not chk_martial.value:
                curr_dt = sd
                while curr_dt <= ed:
                    key = curr_dt.strftime("%d.%m")
                    if key in HL:
                        applied.append(f"{curr_dt.strftime('%d.%m.%Y')} ({HL[key]})")
                        ed += timedelta(days=1)
                    curr_dt += timedelta(days=1)
            
            first_w = ed + timedelta(days=1)
            lbl_end.value = f"До (включно): {ed.strftime('%d.%m.%Y')}"
            lbl_last.value = f"Останній день в частині: {(sd - timedelta(days=1)).strftime('%d.%m.%Y')}"
            lbl_first.value = f"Повернення в частину: {first_w.strftime('%d.%m.%Y')}"
            
            res = f"Звання/ПІБ: {txt_pib.value or 'Не вказано'}\nВид: {combo_type.value}\nПеріод: {sd.strftime('%d.%m.%Y')} - {ed.strftime('%d.%m.%Y')} ({dur} дн.)\n"
            if chk_martial.value: res += "⚠️ Воєнний стан: свята скасовані.\n"
            elif applied: res += f"Подовжено на {len(applied)} дн. через свята.\n"
            res += "Вихідний день." if first_w.weekday() >= 5 else f"Початок служби: {first_w.strftime('%d.%m.%Y')}."
            lbl_res.value = res
            page.update()
        except Exception:
            lbl_res.value = f"Помилка введення дати! Формат: дд.мм.рррр"
            page.update()

    def add_to_log(e):
        do_calc(None)
        try:
            # Використовуємо безпечний шлях для Android (тимчасова папка додатку) або корінь для ПК
            log_dir = os.environ.get("HOME", ".")
            log_path = os.path.join(log_dir, "arm_vacation_log.txt")
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%d.%m %H:%M')}] {txt_pib.value or 'Боєць'} | {combo_type.value} | {txt_dur.value} дн.\n")
            
            snack = ft.SnackBar(ft.Text("Розрахунок успішно записано в лог!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception as ex:
            # Якщо запис у файл заблоковано, зберігаємо внутрішньо в пам'ять додатку
            page.client_storage.set(f"log_{datetime.now().timestamp()}", f"{txt_pib.value} | {txt_dur.value} дн.")
            snack = ft.SnackBar(ft.Text("Збережено в локальну пам'ять додатку!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    def close_app(e):
        # Безпечне закриття: на Windows закриє вікно, на Android просто згорне або очистить форму
        if page.platform in [ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX]:
            page.window_close()
        else:
            txt_pib.value = ""
            txt_dur.value = "30"
            do_calc(None)
            snack = ft.SnackBar(ft.Text("Форму очищено!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    txt_pib = ft.TextField(label="Звання / ПІБ", border_color="#C5C1AA", text_style=ft.TextStyle(weight="bold", size=16))
    combo_type = ft.Dropdown(label="Вид відпустки", value="Основна щорічна 🪖", options=[
        ft.dropdown.Option("Основна щорічна 🪖"), ft.dropdown.Option("За сімейними обставинами 🏠"),
        ft.dropdown.Option("Лікування / Реабілітація 🏥"), ft.dropdown.Option("У зв'язку з хворобою 🤒"),
        ft.dropdown.Option("Поранення / Контузія 💥"), ft.dropdown.Option("За особливі заслуги 🎖️")
    ], border_color="#C5C1AA")
    
    txt_date = ft.TextField(label="Дата початку (дд.мм.рррр)", value=datetime.now().strftime("%d.%m.%Y"), border_color="#C5C1AA", on_change=do_calc)
    txt_dur = ft.TextField(label="Тривалість (днів)", value="30", border_color="#C5C1AA", on_change=do_calc)
    chk_martial = ft.Checkbox(label="Воєнний стан (скасувати свята)", value=True, on_change=do_calc, label_style=ft.TextStyle(weight="bold"))
    
    lbl_last = ft.Text("Останній день в частині: --", size=14, weight="bold", color="#C5C1AA")
    lbl_end = ft.Text("До (включно): --", size=14, weight="bold", color="#C5C1AA")
    lbl_first = ft.Text("Повернення в частину: --", size=14, weight="bold", color="#C5C1AA")
    lbl_res = ft.Text("Введіть дані для тактичного розрахунку", size=14, color="#F5F5DC")
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("АРМІЙСЬКИЙ КАЛЬКУЛЯТОР ВІДПУСТОК", size=18, weight="bold", color="#FFFFFF", text_align="center"),
                txt_pib, combo_type, txt_date, txt_dur, chk_martial,
                ft.Divider(color="#C5C1AA"),
                lbl_last, lbl_end, lbl_first,
                ft.Container(content=lbl_res, bgcolor="#556B2F", padding=10, border_radius=5),
                ft.Row([
                    ft.ElevatedButton("Записати в Лог", on_click=add_to_log, bgcolor="#C5C1AA", color="#2F4F4F"),
                    ft.ElevatedButton("Очистити/Закрити", on_click=close_app, bgcolor="#768B6E", color="#FFFFFF")
                ], alignment="center")
            ], spacing=12),
            padding=15, bgcolor="#4D5D43", border_radius=10, margin=10
        )
    )
    do_calc(None)

if __name__ == "__main__":
    ft.app(target=main)
