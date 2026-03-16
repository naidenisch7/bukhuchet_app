from datetime import date as dt_date

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

import db

Builder.load_string("""
<WarrantyScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1
    MDFloatLayout:
        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Гарантия / Сервис"
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1
                left_action_items: [["menu", lambda x: app.open_drawer()]]

            MDBoxLayout:
                size_hint_y: None
                height: dp(38)
                md_bg_color: 0.12, 0.12, 0.14, 1
                padding: dp(8), dp(4)
                spacing: dp(6)
                id: filter_row

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    id: cases_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.15, 0.70, 0.65, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.add_case()
""")

STATUS_MAP = {
    "received":    ("📥 Принято",  [0.15, 0.70, 0.65, 1]),
    "in_progress": ("🔧 В работе", [0.95, 0.75, 0.15, 1]),
    "completed":   ("✅ Готово",    [0.30, 0.85, 0.50, 1]),
    "returned":    ("🏠 Выдано",   [0.50, 0.50, 0.50, 1]),
}

FILTER_LABELS = [
    ("all",         "Все"),
    ("received",    "Принято"),
    ("in_progress", "В работе"),
    ("completed",   "Готово"),
    ("returned",    "Выдано"),
]


def _fmt_money(val):
    s = f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}р."


class WarrantyScreen(MDScreen):
    status_filter = StringProperty("all")

    _dialog = None

    # ── lifecycle ───────────────────────────────────────────────
    def on_enter(self, *args):
        self._build_filter_chips()
        self.load_cases()

    def go_back(self):
        self.manager.current = "main_menu"

    # ── filter chips ────────────────────────────────────────────
    def set_filter(self, f):
        self.status_filter = f
        self._build_filter_chips()
        self.load_cases()

    def _build_filter_chips(self):
        row = self.ids.filter_row
        row.clear_widgets()
        for key, label in FILTER_LABELS:
            if key == self.status_filter:
                btn = MDRaisedButton(
                    text=label,
                    md_bg_color=(0.15, 0.70, 0.65, 1),
                    text_color=(1, 1, 1, 1),
                    font_size="11sp",
                    size_hint=(None, None),
                    height=dp(30),
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            else:
                btn = MDFlatButton(
                    text=label,
                    text_color=(0.6, 0.6, 0.6, 1),
                    font_size="11sp",
                    size_hint=(None, None),
                    height=dp(30),
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            row.add_widget(btn)

    # ── case list ───────────────────────────────────────────────
    def load_cases(self):
        container = self.ids.cases_list
        container.clear_widgets()
        status = None if self.status_filter == "all" else self.status_filter
        cases = db.get_warranty_cases(status=status)
        if not cases:
            container.add_widget(
                MDLabel(
                    text="Нет записей",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=dp(60),
                )
            )
            return
        for c in cases:
            container.add_widget(self._make_case_card(c))

    def _make_case_card(self, case):
        status_key = case.get("status", "received")
        status_label, status_color = STATUS_MAP.get(
            status_key, ("?", [0.5, 0.5, 0.5, 1])
        )

        buyer_name = ""
        if case.get("buyer_id"):
            try:
                buyer = db.get_buyer(case["buyer_id"])
                if buyer:
                    buyer_name = buyer.get("name", "")
            except Exception:
                pass

        problem_text = case.get("problem", "") or ""
        if len(problem_text) > 50:
            problem_text = problem_text[:50] + "…"

        card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(90),
            md_bg_color=(0.18, 0.18, 0.20, 1),
            radius=[dp(10)],
            padding=0,
            ripple_behavior=True,
            on_release=lambda x, cid=case["id"]: self._view_case(cid),
        )

        # colored left bar
        bar = MDBoxLayout(
            size_hint=(None, 1),
            width=dp(5),
            md_bg_color=status_color,
            radius=[dp(10), 0, 0, dp(10)],
        )
        card.add_widget(bar)

        # info area
        info = MDBoxLayout(
            orientation="vertical",
            padding=(dp(10), dp(8)),
            spacing=dp(2),
            size_hint=(1, 1),
        )

        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(22),
        )
        top_row.add_widget(
            MDLabel(
                text=case.get("device_name", ""),
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True,
                size_hint_x=0.7,
            )
        )
        top_row.add_widget(
            MDLabel(
                text=status_label,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=status_color,
                halign="right",
                size_hint_x=0.3,
            )
        )
        info.add_widget(top_row)

        if buyer_name:
            info.add_widget(
                MDLabel(
                    text=f"Клиент: {buyer_name}",
                    font_style="Caption",
                    theme_text_color="Custom",
                    text_color=(0.65, 0.65, 0.65, 1),
                    size_hint_y=None,
                    height=dp(18),
                )
            )

        info.add_widget(
            MDLabel(
                text=problem_text,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.55, 0.55, 1),
                size_hint_y=None,
                height=dp(18),
            )
        )

        cost = case.get("cost", 0) or 0
        if cost > 0:
            info.add_widget(
                MDLabel(
                    text=_fmt_money(cost),
                    font_style="Caption",
                    theme_text_color="Custom",
                    text_color=(0.15, 0.70, 0.65, 1),
                    halign="right",
                    size_hint_y=None,
                    height=dp(18),
                )
            )

        card.add_widget(info)
        return card

    # ── view / details dialog ───────────────────────────────────
    def _dismiss(self):
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None

    def _view_case(self, case_id):
        case = db.get_warranty_case(case_id)
        if not case:
            return

        status_key = case.get("status", "received")
        status_label, status_color = STATUS_MAP.get(
            status_key, ("?", [0.5, 0.5, 0.5, 1])
        )

        buyer_name = "—"
        if case.get("buyer_id"):
            try:
                buyer = db.get_buyer(case["buyer_id"])
                if buyer:
                    buyer_name = buyer.get("name", "")
            except Exception:
                pass

        imei_line = f"IMEI: {case['imei']}\n" if case.get("imei") else ""
        cost = case.get("cost", 0) or 0
        cost_line = f"Стоимость: {_fmt_money(cost)}\n" if cost > 0 else ""
        received = case.get("received_date", "")
        completed = case.get("completed_date", "")
        dates = f"Принято: {received}"
        if completed:
            dates += f"\nЗавершено: {completed}"

        detail_text = (
            f"[b]{case.get('device_name', '')}[/b]\n"
            f"{imei_line}"
            f"Клиент: {buyer_name}\n"
            f"{cost_line}"
            f"Статус: {status_label}\n"
            f"{dates}\n\n"
            f"Проблема:\n{case.get('problem', '—')}"
        )

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
        )
        lbl = MDLabel(
            text=detail_text,
            markup=True,
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
        )
        lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        content.add_widget(lbl)

        # action buttons
        actions_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            adaptive_height=True,
        )

        if status_key == "received":
            actions_box.add_widget(
                MDRaisedButton(
                    text="🔧 В работу",
                    md_bg_color=(0.95, 0.75, 0.15, 1),
                    text_color=(0, 0, 0, 1),
                    size_hint_x=1,
                    on_release=lambda x: self._change_status(case_id, "in_progress"),
                )
            )
        elif status_key == "in_progress":
            actions_box.add_widget(
                MDRaisedButton(
                    text="✅ Готово",
                    md_bg_color=(0.30, 0.85, 0.50, 1),
                    text_color=(0, 0, 0, 1),
                    size_hint_x=1,
                    on_release=lambda x: self._change_status(case_id, "completed"),
                )
            )
        elif status_key == "completed":
            actions_box.add_widget(
                MDRaisedButton(
                    text="🏠 Выдано клиенту",
                    md_bg_color=(0.50, 0.50, 0.50, 1),
                    text_color=(1, 1, 1, 1),
                    size_hint_x=1,
                    on_release=lambda x: self._change_status(case_id, "returned"),
                )
            )

        actions_box.add_widget(
            MDFlatButton(
                text="🗑 Удалить",
                text_color=(0.95, 0.30, 0.30, 1),
                size_hint_x=1,
                on_release=lambda x: self._delete_case(case_id),
            )
        )

        content.add_widget(actions_box)
        content.height = lbl.height + actions_box.height + dp(40)

        self._dismiss()
        self._dialog = MDDialog(
            title="Детали заявки",
            type="custom",
            content_cls=content,
            md_bg_color=(0.18, 0.18, 0.20, 1),
        )
        self._dialog.open()

    # ── status change ───────────────────────────────────────────
    def _change_status(self, case_id, new_status):
        kwargs = {"status": new_status}
        if new_status == "completed":
            kwargs["completed_date"] = str(dt_date.today())
        db.update_warranty_case(case_id, **kwargs)
        self._dismiss()
        self.load_cases()

    # ── delete ──────────────────────────────────────────────────
    def _delete_case(self, case_id):
        db.delete_warranty_case(case_id)
        self._dismiss()
        self.load_cases()

    # ── add case (two-step) ─────────────────────────────────────
    def add_case(self):
        self._selected_buyer_id = None
        buyers = db.get_buyers()

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
        )

        content.add_widget(
            MDRaisedButton(
                text="Без покупателя",
                md_bg_color=(0.30, 0.30, 0.32, 1),
                text_color=(1, 1, 1, 1),
                size_hint_x=1,
                on_release=lambda x: self._add_case_step2(None),
            )
        )

        for b in buyers:
            content.add_widget(
                MDFlatButton(
                    text=b.get("name", f"ID {b['id']}"),
                    text_color=(0.9, 0.9, 0.9, 1),
                    size_hint_x=1,
                    on_release=lambda x, bid=b["id"]: self._add_case_step2(bid),
                )
            )

        content.height = dp(44) * (len(buyers) + 1) + dp(16)

        self._dismiss()
        self._dialog = MDDialog(
            title="Выберите клиента",
            type="custom",
            content_cls=content,
            md_bg_color=(0.18, 0.18, 0.20, 1),
        )
        self._dialog.open()

    def _add_case_step2(self, buyer_id):
        self._selected_buyer_id = buyer_id
        self._dismiss()

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
            height=dp(300),
        )

        self._tf_device = MDTextField(
            hint_text="Название устройства",
            mode="fill",
            fill_color_normal=(0.14, 0.14, 0.16, 1),
            text_color_normal=(1, 1, 1, 1),
            hint_text_color_normal=(0.5, 0.5, 0.5, 1),
            line_color_normal=(0.15, 0.70, 0.65, 1),
            size_hint_y=None,
            height=dp(48),
        )
        self._tf_imei = MDTextField(
            hint_text="IMEI (необязательно)",
            mode="fill",
            fill_color_normal=(0.14, 0.14, 0.16, 1),
            text_color_normal=(1, 1, 1, 1),
            hint_text_color_normal=(0.5, 0.5, 0.5, 1),
            line_color_normal=(0.15, 0.70, 0.65, 1),
            size_hint_y=None,
            height=dp(48),
        )
        self._tf_problem = MDTextField(
            hint_text="Описание проблемы",
            mode="fill",
            multiline=True,
            fill_color_normal=(0.14, 0.14, 0.16, 1),
            text_color_normal=(1, 1, 1, 1),
            hint_text_color_normal=(0.5, 0.5, 0.5, 1),
            line_color_normal=(0.15, 0.70, 0.65, 1),
            size_hint_y=None,
            height=dp(72),
        )
        self._tf_cost = MDTextField(
            hint_text="Стоимость (0 если бесплатно)",
            mode="fill",
            input_filter="float",
            fill_color_normal=(0.14, 0.14, 0.16, 1),
            text_color_normal=(1, 1, 1, 1),
            hint_text_color_normal=(0.5, 0.5, 0.5, 1),
            line_color_normal=(0.15, 0.70, 0.65, 1),
            size_hint_y=None,
            height=dp(48),
        )

        save_btn = MDRaisedButton(
            text="Сохранить",
            md_bg_color=(0.15, 0.70, 0.65, 1),
            text_color=(1, 1, 1, 1),
            size_hint_x=1,
            on_release=lambda x: self._save_case(),
        )

        content.add_widget(self._tf_device)
        content.add_widget(self._tf_imei)
        content.add_widget(self._tf_problem)
        content.add_widget(self._tf_cost)
        content.add_widget(save_btn)

        self._dialog = MDDialog(
            title="Новая заявка",
            type="custom",
            content_cls=content,
            md_bg_color=(0.18, 0.18, 0.20, 1),
        )
        self._dialog.open()

    def _save_case(self):
        device = self._tf_device.text.strip()
        if not device:
            return
        imei = self._tf_imei.text.strip() or None
        problem = self._tf_problem.text.strip()
        try:
            cost = float(self._tf_cost.text.strip())
        except (ValueError, TypeError):
            cost = 0.0
        if cost < 0:
            cost = 0.0

        buyer_id = self._selected_buyer_id
        received_date = str(dt_date.today())

        db.add_warranty_case(buyer_id, device, imei, problem, cost, received_date)

        # deduct from buyer deposit / overflow to debt
        if buyer_id and cost > 0:
            try:
                buyer = db.get_buyer(buyer_id)
                if buyer:
                    deposit = buyer.get("deposit", 0) or 0
                    debt = buyer.get("debt", 0) or 0
                    if deposit >= cost:
                        deposit -= cost
                    else:
                        remaining = cost - deposit
                        deposit = 0
                        debt += remaining
                    db.update_buyer(buyer_id, deposit=deposit, debt=debt)
            except Exception:
                pass

        self._dismiss()
        self.load_cases()
