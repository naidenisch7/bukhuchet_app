"""Экран покупателей: список, детали, редактирование, наценки — тёмная тема."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<BuyersScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Покупатели"
                left_action_items: [["arrow-left", lambda x: root.go_back()]]
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: dp(12)
                    spacing: dp(8)
                    adaptive_height: True
                    id: buyer_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.18, 0.74, 0.42, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.add_buyer()

<BuyerDetailScreen>:
    buyer_id: 0
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Покупатель"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 0
            md_bg_color: 0.10, 0.10, 0.12, 1
            specific_text_color: 1, 1, 1, 1

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(12)
                adaptive_height: True

                # Name header card
                MDCard:
                    orientation: "vertical"
                    padding: dp(20)
                    size_hint_y: None
                    height: dp(70)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.18, 0.74, 0.42, 1

                    MDLabel:
                        id: buyer_name
                        text: ""
                        font_style: "H5"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

                # Balance card
                MDCard:
                    orientation: "vertical"
                    padding: dp(16)
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(90)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.18, 0.18, 0.20, 1

                    MDLabel:
                        text: "Баланс"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        size_hint_y: None
                        height: dp(24)

                    MDLabel:
                        id: buyer_info
                        text: ""
                        font_style: "Body1"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                MDFillRoundFlatButton:
                    text: "Редактировать"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.20, 0.60, 0.95, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.edit_buyer()

                MDFillRoundFlatButton:
                    text: "Наценки по категориям"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.0, 0.74, 0.65, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.go_markups()

                # Снять с карты
                MDFillRoundFlatButton:
                    text: "Снять с карты (погасить долг)"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.95, 0.55, 0.15, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.withdraw_from_card()

                # Deposit management
                MDFillRoundFlatButton:
                    text: "Пополнить депозит"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.18, 0.74, 0.42, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.add_deposit()

                MDFillRoundFlatButton:
                    text: "История депозита"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.25, 0.25, 0.27, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.show_deposit_history()

                # Stats card
                MDCard:
                    orientation: "vertical"
                    padding: dp(16)
                    size_hint_y: None
                    height: dp(56)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.18, 0.18, 0.20, 1

                    MDLabel:
                        id: orders_info
                        text: ""
                        font_style: "Body1"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

                MDFillRoundFlatButton:
                    text: "Удалить покупателя"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.75, 0.15, 0.15, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.delete_buyer()

<BuyerEditScreen>:
    buyer_id: 0
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Редактирование"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 0
            md_bg_color: 0.10, 0.10, 0.12, 1
            specific_text_color: 1, 1, 1, 1

        MDCard:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint: 0.92, None
            height: dp(300)
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            elevation: 0
            radius: [dp(12)]
            md_bg_color: 0.18, 0.18, 0.20, 1

            MDTextField:
                id: name_field
                hint_text: "Имя покупателя"
                mode: "rectangle"
                icon_left: "account"

            MDTextField:
                id: deposit_field
                hint_text: "Депозит"
                mode: "rectangle"
                input_filter: "float"
                icon_left: "cash"

            MDTextField:
                id: debt_field
                hint_text: "Долг"
                mode: "rectangle"
                input_filter: "float"
                icon_left: "cash-minus"

            MDFillRoundFlatButton:
                text: "Сохранить"
                pos_hint: {"center_x": 0.5}
                md_bg_color: 0.18, 0.74, 0.42, 1
                text_color: 1, 1, 1, 1
                on_release: root.save()

<MarkupScreen>:
    buyer_id: 0
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Наценки"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 0
            md_bg_color: 0.10, 0.10, 0.12, 1
            specific_text_color: 1, 1, 1, 1

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(10)
                adaptive_height: True
                id: markup_list
""")


class BuyersScreen(MDScreen):
    dialog = None

    def on_enter(self):
        self.load_buyers()

    def load_buyers(self):
        box = self.ids.buyer_list
        box.clear_widgets()
        buyers = db.get_buyers()
        if not buyers:
            box.add_widget(MDLabel(
                text="Нет покупателей",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(80),
            ))
            return
        for b in buyers:
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                size_hint_y=None,
                height=dp(78),
                elevation=0,
                radius=[dp(12)],
                ripple_behavior=True,
                md_bg_color=[0.18, 0.18, 0.20, 1],
                on_release=lambda x, bid=b["id"]: self.open_buyer(bid),
            )
            card.add_widget(MDLabel(
                text=b['name'],
                font_style="Subtitle1",
                bold=True,
                size_hint_y=0.5,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
            ))
            card.add_widget(MDLabel(
                text=f"Депозит: {b['deposit']:.0f}  |  Долг: {b['debt']:.0f}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=[0.6, 0.6, 0.6, 1],
                size_hint_y=0.5,
            ))
            box.add_widget(card)

    def open_buyer(self, buyer_id):
        scr = self.manager.get_screen("buyer_detail")
        scr.buyer_id = buyer_id
        self.manager.current = "buyer_detail"

    def add_buyer(self):
        if self.dialog:
            self.dialog.dismiss()
        content = MDTextField(hint_text="Имя покупателя", mode="rectangle")
        self.dialog = MDDialog(
            title="➕ Новый покупатель",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Создать", on_release=lambda x: self._do_add(content.text)),
            ],
        )
        self.dialog.open()

    def _do_add(self, name):
        name = name.strip()
        if name:
            db.add_buyer(name)
            self.dialog.dismiss()
            self.load_buyers()

    def go_back(self):
        self.manager.current = "main_menu"


class BuyerDetailScreen(MDScreen):
    buyer_id = NumericProperty(0)

    def on_enter(self):
        self.load_data()

    def load_data(self):
        buyer = db.get_buyer(self.buyer_id)
        if not buyer:
            self.manager.current = "buyers"
            return
        self.ids.buyer_name.text = buyer["name"]
        self.ids.buyer_info.text = (
            f"Депозит: {buyer['deposit']:.0f}      Долг: {buyer['debt']:.0f}"
        )
        orders = db.get_orders_by_buyer(self.buyer_id)
        if orders:
            total = sum(o["total_sale"] for o in orders)
            self.ids.orders_info.text = f"Заказов: {len(orders)} | Продажи: {total:.0f}"
        else:
            self.ids.orders_info.text = "Заказов пока нет"

    def edit_buyer(self):
        scr = self.manager.get_screen("buyer_edit")
        scr.buyer_id = self.buyer_id
        self.manager.current = "buyer_edit"

    def go_markups(self):
        scr = self.manager.get_screen("markup")
        scr.buyer_id = self.buyer_id
        self.manager.current = "markup"

    def withdraw_from_card(self):
        """Снять с карты — ввод суммы, уменьшение долга."""
        if hasattr(self, '_wd_dialog') and self._wd_dialog:
            self._wd_dialog.dismiss()

        buyer = db.get_buyer(self.buyer_id)
        if not buyer:
            return

        self._wd_field = MDTextField(
            hint_text=f"Сумма (долг: {buyer['debt']:.0f})",
            mode="rectangle",
            input_filter="float",
        )
        self._wd_dialog = MDDialog(
            title="Снять с карты",
            type="custom",
            content_cls=self._wd_field,
            buttons=[
                MDFlatButton(text="Отмена",
                    on_release=lambda x: self._wd_dialog.dismiss()),
                MDRaisedButton(text="Снять",
                    md_bg_color=[0.95, 0.55, 0.15, 1],
                    on_release=lambda x: self._do_withdraw()),
            ],
        )
        self._wd_dialog.open()

    def _do_withdraw(self):
        try:
            amount = float(self._wd_field.text or 0)
        except ValueError:
            amount = 0
        if amount <= 0:
            return

        buyer = db.get_buyer(self.buyer_id)
        if not buyer:
            return

        new_debt = max(0, buyer["debt"] - amount)
        db.update_buyer(self.buyer_id, debt=new_debt)
        self._wd_dialog.dismiss()
        self.load_data()

    def delete_buyer(self):
        db.delete_buyer(self.buyer_id)
        self.manager.current = "buyers"

    # ── deposit management ─────────────────────────────────
    def add_deposit(self):
        """Dialog to add deposit payment."""
        buyer = db.get_buyer(self.buyer_id)
        if not buyer:
            return

        self._dep_field = MDTextField(
            hint_text=f"Сумма (текущий депозит: {buyer['deposit']:.0f})",
            mode="rectangle",
            input_filter="float",
        )
        self._dep_note = MDTextField(
            hint_text="Примечание (необязательно)",
            mode="rectangle",
        )
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(12),
            size_hint_y=None, height=dp(120),
        )
        content.add_widget(self._dep_field)
        content.add_widget(self._dep_note)

        self._dep_dialog = MDDialog(
            title="Пополнить депозит",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена",
                    on_release=lambda x: self._dep_dialog.dismiss()),
                MDRaisedButton(text="Пополнить",
                    md_bg_color=[0.18, 0.74, 0.42, 1],
                    on_release=lambda x: self._do_add_deposit()),
            ],
        )
        self._dep_dialog.open()

    def _do_add_deposit(self):
        try:
            amount = float(self._dep_field.text or 0)
        except ValueError:
            amount = 0
        if amount <= 0:
            return

        from datetime import date as dt_date
        note = (self._dep_note.text or "").strip()
        today = dt_date.today().strftime("%Y-%m-%d")
        db.add_deposit_payment(self.buyer_id, amount, today, note)
        self._dep_dialog.dismiss()
        self.load_data()

    def show_deposit_history(self):
        """Show deposit payment history dialog."""
        payments = db.get_deposit_payments_by_buyer(self.buyer_id)

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint_y=None, padding=[dp(4), dp(4)],
        )
        if not payments:
            content.height = dp(50)
            content.add_widget(MDLabel(
                text="Нет операций",
                halign="center",
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
            ))
        else:
            content.height = min(dp(60) * len(payments), dp(400))
            from kivy.uix.scrollview import ScrollView
            scroll = ScrollView()
            inner = MDBoxLayout(
                orientation="vertical", spacing=dp(6),
                adaptive_height=True,
            )
            for p in payments:
                amt = p["amount"]
                color = [0.18, 0.74, 0.42, 1] if amt >= 0 else [0.85, 0.20, 0.20, 1]
                sign = "+" if amt >= 0 else ""
                note = p.get("note") or ""
                date_str = (p.get("date") or "")[:10]

                row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None, height=dp(48),
                    padding=[dp(8), dp(4)],
                )
                left = MDBoxLayout(orientation="vertical", size_hint_x=0.6)
                left.add_widget(MDLabel(
                    text=f"{sign}{amt:.0f}р.",
                    font_style="Subtitle1", bold=True,
                    theme_text_color="Custom", text_color=color,
                ))
                left.add_widget(MDLabel(
                    text=note if note else "—",
                    font_style="Caption",
                    theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                ))
                row.add_widget(left)

                right = MDBoxLayout(orientation="horizontal", size_hint_x=0.4)
                right.add_widget(MDLabel(
                    text=date_str,
                    halign="right", font_style="Caption",
                    theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                ))
                right.add_widget(MDIconButton(
                    icon="delete-outline",
                    theme_text_color="Custom", text_color=[0.7, 0.3, 0.3, 1],
                    on_release=lambda x, pid=p["id"], a=amt:
                        self._delete_deposit(pid, a),
                ))
                row.add_widget(right)
                inner.add_widget(row)
            scroll.add_widget(inner)
            content.add_widget(scroll)

        self._hist_dialog = MDDialog(
            title="История депозита",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Закрыть",
                    on_release=lambda x: self._hist_dialog.dismiss()),
            ],
        )
        self._hist_dialog.open()

    def _delete_deposit(self, payment_id, amount):
        db.delete_deposit_payment(payment_id, self.buyer_id, amount)
        self._hist_dialog.dismiss()
        self.load_data()
        self.show_deposit_history()

    def go_back(self):
        self.manager.current = "buyers"


class BuyerEditScreen(MDScreen):
    buyer_id = NumericProperty(0)

    def on_enter(self):
        buyer = db.get_buyer(self.buyer_id)
        if buyer:
            self.ids.name_field.text = buyer["name"]
            self.ids.deposit_field.text = str(buyer["deposit"])
            self.ids.debt_field.text = str(buyer["debt"])

    def save(self):
        name = self.ids.name_field.text.strip()
        try:
            deposit = float(self.ids.deposit_field.text or 0)
        except ValueError:
            deposit = 0
        try:
            debt = float(self.ids.debt_field.text or 0)
        except ValueError:
            debt = 0
        if name:
            db.update_buyer(self.buyer_id, name=name, deposit=deposit, debt=debt)
        self.manager.current = "buyer_detail"

    def go_back(self):
        self.manager.current = "buyer_detail"


class MarkupScreen(MDScreen):
    buyer_id = NumericProperty(0)

    def on_enter(self):
        self.load_markups()

    def load_markups(self):
        box = self.ids.markup_list
        box.clear_widgets()
        db.ensure_default_markups(self.buyer_id)
        markups = db.get_markups(self.buyer_id)

        # Icons for categories
        cat_icons = {
            "Аксессуары": "headphones",
            "Телефоны": "cellphone",
            "Apple Watch": "watch",
            "Макбук": "laptop",
        }

        for m in markups:
            icon = cat_icons.get(m["category_name"], "package-variant")
            card = MDCard(
                orientation="horizontal",
                padding=dp(12),
                size_hint_y=None,
                height=dp(68),
                elevation=0,
                radius=[dp(12)],
                md_bg_color=[0.18, 0.18, 0.20, 1],
            )
            from kivymd.uix.label import MDIcon
            icon_box = MDBoxLayout(orientation="horizontal", size_hint_x=0.5, padding=[0, dp(8)])
            icon_box.add_widget(MDIcon(
                icon=icon, font_size="24sp",
                theme_text_color="Custom", text_color=[0.7,0.7,0.7,1],
                size_hint_x=0.3,
            ))
            icon_box.add_widget(MDLabel(
                text=m['category_name'],
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=[1,1,1,1],
                valign="center",
            ))
            card.add_widget(icon_box)
            tf = MDTextField(
                text=str(int(m["markup_amount"])),
                hint_text="₽",
                mode="rectangle",
                input_filter="int",
                size_hint_x=0.3,
            )
            tf.category_name = m["category_name"]
            card.add_widget(tf)
            card.add_widget(MDIconButton(
                icon="content-save",
                theme_text_color="Custom",
                text_color=[0.0, 0.74, 0.65, 1],
                on_release=lambda x, t=tf: self._save_markup(t),
            ))
            box.add_widget(card)

    def _save_markup(self, tf):
        try:
            amount = int(tf.text or 0)
        except ValueError:
            amount = 0
        db.set_markup(self.buyer_id, tf.category_name, amount)

    def go_back(self):
        self.manager.current = "buyer_detail"
