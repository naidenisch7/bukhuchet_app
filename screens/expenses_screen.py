"""Экран затрат: Зарплата / Такси / Другое — CRUD + фильтрация по датам."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from datetime import date as dt_date, timedelta
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<ExpensesScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Затраты"
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1
                left_action_items: [["arrow-left", lambda x: root.go_back()]]

            # Date filter chips
            MDBoxLayout:
                size_hint_y: None
                height: dp(38)
                md_bg_color: 0.12, 0.12, 0.14, 1
                padding: dp(8), dp(4)
                spacing: dp(6)
                id: filter_row

            # Total card
            MDCard:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(50)
                elevation: 0
                radius: [0]
                md_bg_color: 0.15, 0.15, 0.17, 1
                padding: dp(16), dp(8)

                MDLabel:
                    id: total_label
                    text: "Итого: 0р."
                    font_style: "H6"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.95, 0.55, 0.15, 1

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(8)
                    spacing: dp(6)
                    id: expense_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.95, 0.55, 0.15, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.add_expense()
""")


def _fmt_money(val):
    s = f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}р."


def _fmt_date_short(date_str):
    try:
        d = dt_date.fromisoformat(date_str)
        return d.strftime("%d.%m.%Y")
    except Exception:
        return date_str


CAT_ICONS = {
    "Зарплата": ("cash", [0.18, 0.74, 0.42, 1]),
    "Такси": ("car", [0.95, 0.75, 0.15, 1]),
    "Другое": ("dots-horizontal-circle-outline", [0.60, 0.60, 0.60, 1]),
}


class ExpensesScreen(MDScreen):
    date_filter = StringProperty("today")

    def on_enter(self):
        self._build_filter_chips()
        self.load_expenses()

    def go_back(self):
        self.manager.current = "main_menu"

    # ── filter chips ───────────────────────────────────────
    def set_filter(self, f):
        self.date_filter = f
        self._build_filter_chips()
        self.load_expenses()

    def _build_filter_chips(self):
        row = self.ids.filter_row
        row.clear_widgets()
        filters = [("today", "Сегодня"), ("week", "Неделя"), ("month", "Месяц"), ("all", "Все")]
        for key, label in filters:
            active = self.date_filter == key
            if active:
                btn = MDRaisedButton(
                    text=label, font_size="12sp",
                    md_bg_color=[0.95, 0.55, 0.15, 1],
                    text_color=[1, 1, 1, 1],
                    size_hint_x=1,
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            else:
                btn = MDFlatButton(
                    text=label, font_size="12sp",
                    theme_text_color="Custom",
                    text_color=[0.6, 0.6, 0.6, 1],
                    size_hint_x=1,
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            row.add_widget(btn)

    def _get_date_range(self):
        today = dt_date.today()
        if self.date_filter == "today":
            s = today.strftime("%Y-%m-%d")
            return s, s
        elif self.date_filter == "week":
            return (today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.date_filter == "month":
            return today.replace(day=1).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        return None, None

    # ── loader ─────────────────────────────────────────────
    def load_expenses(self):
        box = self.ids.expense_list
        box.clear_widgets()

        d_from, d_to = self._get_date_range()
        if d_from:
            expenses = db.get_expenses_by_period(d_from, d_to)
        else:
            expenses = db.get_expenses()

        total = sum(e["amount"] for e in expenses)
        self.ids.total_label.text = f"Итого: {_fmt_money(total)}"

        # Group by date
        by_date = {}
        for e in expenses:
            by_date.setdefault(e["date"], []).append(e)

        for date_str, items in by_date.items():
            # Date header
            box.add_widget(MDLabel(
                text=_fmt_date_short(date_str),
                font_style="Caption", bold=True,
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(28),
                padding=[dp(8), 0],
            ))
            day_total = sum(it["amount"] for it in items)
            box.add_widget(MDLabel(
                text=f"За день: {_fmt_money(day_total)}",
                font_style="Caption",
                theme_text_color="Custom", text_color=[0.95, 0.55, 0.15, 1],
                size_hint_y=None, height=dp(20),
                padding=[dp(8), 0],
            ))

            for e in items:
                box.add_widget(self._make_expense_card(e))

        if not expenses:
            box.add_widget(MDLabel(
                text="Нет затрат за выбранный период",
                halign="center",
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(60),
            ))

        box.add_widget(Widget(size_hint_y=None, height=dp(80)))

    def _make_expense_card(self, expense):
        from kivymd.uix.label import MDIcon
        cat = expense["category"]
        icon_name, icon_color = CAT_ICONS.get(cat, ("dots-horizontal", [0.6, 0.6, 0.6, 1]))

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None, height=dp(72),
            elevation=0, radius=[dp(12)],
            md_bg_color=[0.18, 0.18, 0.20, 1],
            padding=[dp(12), dp(8)],
        )

        # Left: icon + info
        left = MDBoxLayout(orientation="horizontal", size_hint_x=0.7, spacing=dp(8))
        left.add_widget(MDIcon(
            icon=icon_name, font_size="28sp",
            theme_text_color="Custom", text_color=icon_color,
            size_hint_x=None, width=dp(36),
            pos_hint={"center_y": 0.5},
        ))
        info = MDBoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(MDLabel(
            text=cat, font_style="Subtitle1", bold=True,
            theme_text_color="Custom", text_color=[1, 1, 1, 1],
            size_hint_y=0.5,
        ))
        desc = expense.get("description") or ""
        info.add_widget(MDLabel(
            text=desc if desc else "—",
            font_style="Caption",
            theme_text_color="Custom", text_color=[0.6, 0.6, 0.6, 1],
            size_hint_y=0.5,
        ))
        left.add_widget(info)
        card.add_widget(left)

        # Right: amount + delete
        right = MDBoxLayout(orientation="horizontal", size_hint_x=0.3, spacing=dp(4))
        right.add_widget(MDLabel(
            text=_fmt_money(expense["amount"]),
            halign="right", font_style="Subtitle2", bold=True,
            theme_text_color="Custom", text_color=[0.95, 0.55, 0.15, 1],
            size_hint_x=0.7,
        ))
        right.add_widget(MDIconButton(
            icon="delete-outline",
            theme_text_color="Custom", text_color=[0.7, 0.3, 0.3, 1],
            on_release=lambda x, eid=expense["id"]: self._delete_expense(eid),
        ))
        card.add_widget(right)
        return card

    def _delete_expense(self, expense_id):
        db.delete_expense(expense_id)
        self.load_expenses()

    # ── add expense dialog (2-step) ────────────────────────
    def add_expense(self):
        """Step 1: select category."""
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(12),
            size_hint_y=None, height=dp(180), padding=[dp(8), dp(8)],
        )
        for cat in db.EXPENSE_CATEGORIES:
            icon_name, icon_color = CAT_ICONS.get(cat, ("dots-horizontal", [0.6, 0.6, 0.6, 1]))
            btn = MDRaisedButton(
                text=f"  {cat}",
                icon=icon_name,
                md_bg_color=[0.25, 0.25, 0.27, 1],
                text_color=[1, 1, 1, 1],
                size_hint_x=1,
                on_release=lambda x, c=cat: self._select_category(c),
            )
            content.add_widget(btn)

        self._cat_dialog = MDDialog(
            title="Выберите категорию",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self._cat_dialog.dismiss()),
            ],
        )
        self._cat_dialog.open()

    def _select_category(self, category):
        """Step 2: enter amount + description."""
        self._cat_dialog.dismiss()
        self._selected_cat = category

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(12),
            size_hint_y=None, height=dp(140), padding=[dp(8), dp(8)],
        )
        hint = "Имя и сумма (Иван 50000)" if category == "Зарплата" else "Сумма"
        self._amount_field = MDTextField(
            hint_text=hint,
            mode="rectangle",
        )
        self._desc_field = MDTextField(
            hint_text="Описание (необязательно)",
            mode="rectangle",
        )
        content.add_widget(self._amount_field)
        content.add_widget(self._desc_field)

        self._amount_dialog = MDDialog(
            title=f"Затрата: {category}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self._amount_dialog.dismiss()),
                MDRaisedButton(
                    text="Сохранить",
                    md_bg_color=[0.95, 0.55, 0.15, 1],
                    on_release=lambda x: self._save_expense(),
                ),
            ],
        )
        self._amount_dialog.open()

    def _save_expense(self):
        raw = (self._amount_field.text or "").strip()
        desc = (self._desc_field.text or "").strip()
        cat = self._selected_cat

        # Parse amount: for Зарплата support "Name Amount" format
        amount = 0
        if cat == "Зарплата" and " " in raw:
            parts = raw.rsplit(" ", 1)
            try:
                amount = float(parts[1].replace(",", "."))
                if not desc:
                    desc = parts[0]
            except ValueError:
                pass
        if amount == 0:
            try:
                amount = float(raw.replace(",", "."))
            except ValueError:
                return

        if amount <= 0:
            return

        today = dt_date.today().strftime("%Y-%m-%d")
        db.add_expense(today, cat, amount, desc)
        self._amount_dialog.dismiss()
        self.load_expenses()
