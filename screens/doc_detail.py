"""Детальный просмотр документа — как в «Учёт Товаров»."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel, MDIcon
from datetime import date as dt_date
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<DocDetailScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: toolbar
            title: "Документ"
            elevation: 0
            md_bg_color: 0.10, 0.10, 0.12, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["delete", lambda x: root.ask_delete()]]

        # Header fields
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            padding: dp(16), dp(8)
            spacing: dp(4)
            md_bg_color: 0.12, 0.12, 0.14, 1

            # Date + DocNumber + Status icon row
            MDBoxLayout:
                size_hint_y: None
                height: dp(56)
                spacing: dp(12)

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: 0.4

                    MDLabel:
                        text: "Дата документа"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.5, 1
                        size_hint_y: 0.4

                    MDLabel:
                        id: doc_date
                        text: ""
                        font_style: "Body1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: 0.6

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: 0.4

                    MDLabel:
                        text: "Номер документа"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.5, 1
                        size_hint_y: 0.4

                    MDLabel:
                        id: doc_number
                        text: ""
                        font_style: "Body1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: 0.6

                MDIcon:
                    id: status_icon
                    icon: "card-account-details"
                    font_size: "36sp"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.74, 0.42, 1
                    size_hint_x: 0.2

            # Party label + name
            MDLabel:
                id: party_label
                text: "Поставщик"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1
                size_hint_y: None
                height: dp(18)

            MDBoxLayout:
                size_hint_y: None
                height: dp(32)

                MDLabel:
                    id: party_name
                    text: ""
                    font_style: "Subtitle1"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

            # Примечание
            MDLabel:
                text: "Примечание"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1
                size_hint_y: None
                height: dp(18)

            MDBoxLayout:
                size_hint_y: None
                height: dp(28)
                MDLabel:
                    id: note_text
                    text: ""
                    font_style: "Body2"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1

        # Separator
        MDBoxLayout:
            size_hint_y: None
            height: dp(1)
            md_bg_color: 0.25, 0.25, 0.27, 1

        # Items list
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                id: items_box

        # Bottom status bar
        MDBoxLayout:
            size_hint_y: None
            height: dp(40)
            md_bg_color: 0.10, 0.10, 0.12, 1
            padding: dp(16), 0
            spacing: dp(8)

            MDLabel:
                id: bottom_items
                text: ""
                font_style: "Body2"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_x: 0.15

            # Vertical divider
            MDBoxLayout:
                size_hint: None, 0.5
                width: dp(1)
                pos_hint: {"center_y": 0.5}
                md_bg_color: 0.4, 0.4, 0.4, 1

            MDLabel:
                id: bottom_qty
                text: ""
                font_style: "Body2"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_x: 0.15

            # Vertical divider
            MDBoxLayout:
                size_hint: None, 0.5
                width: dp(1)
                pos_hint: {"center_y": 0.5}
                md_bg_color: 0.4, 0.4, 0.4, 1

            MDLabel:
                id: bottom_total
                text: ""
                font_style: "Body2"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
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


class DocDetailScreen(MDScreen):
    order_id = NumericProperty(0)
    doc_mode = StringProperty("confirmed")  # "confirmed" or "open"
    open_sale_ids = ListProperty([])
    open_items_data = ListProperty([])
    return_screen = StringProperty("income")

    def on_enter(self):
        self.load_detail()

    def load_detail(self):
        box = self.ids.items_box
        box.clear_widgets()

        if self.doc_mode == "confirmed":
            self._load_confirmed(box)
        elif self.doc_mode == "open":
            self._load_open(box)

    def _load_confirmed(self, box):
        order = None
        orders = db.get_orders_by_type("income") + db.get_orders_by_type("expense")
        for o in orders:
            if o["id"] == self.order_id:
                order = o
                break
        if not order:
            box.add_widget(MDLabel(text="Документ не найден", halign="center",
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(80)))
            self.ids.bottom_items.text = ""
            self.ids.bottom_qty.text = ""
            self.ids.bottom_total.text = ""
            return

        doc_type = order.get("doc_type", "income")
        is_income = doc_type == "income"
        doc_num = order.get("doc_number") or f"#{order['id']}"

        # Title
        prefix = "Приход" if is_income else "Расход"
        self.ids.toolbar.title = f"{prefix} №{doc_num}"

        # Header fields
        self.ids.doc_date.text = _fmt_date_short(order["date"])
        self.ids.doc_number.text = doc_num
        self.ids.status_icon.icon = "card-account-details"
        self.ids.status_icon.text_color = [0.18, 0.74, 0.42, 1]

        if is_income and order.get("supplier_id"):
            sup = db.get_supplier(order["supplier_id"])
            self.ids.party_label.text = "Поставщик"
            self.ids.party_name.text = sup["name"] if sup else "—"
        elif not is_income and order.get("buyer_id"):
            buyer = db.get_buyer(order["buyer_id"])
            self.ids.party_label.text = "Покупатель"
            self.ids.party_name.text = buyer["name"] if buyer else "—"
        else:
            self.ids.party_label.text = "Контрагент"
            self.ids.party_name.text = "—"

        self.ids.note_text.text = ""

        # Items
        items = db.get_order_items(self.order_id)
        if not items:
            box.add_widget(MDLabel(text="Нет позиций", halign="center",
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(60)))
            self.ids.bottom_items.text = "0"
            self.ids.bottom_qty.text = "0"
            self.ids.bottom_total.text = "0р."
            return

        total_purchase = 0
        total_qty = 0
        created = order.get("created_at", "")
        time_str = created[:16].replace("T", " ") if created and len(created) > 10 else ""

        for it in items:
            qty = it["quantity"]
            pp = it["purchase_price"]
            sp = it.get("sale_price", 0) or 0
            subtotal_p = pp * qty
            subtotal_s = sp * qty
            total_purchase += subtotal_p
            total_qty += qty

            # Item row matching reference: image placeholder | name+price | qty
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(80),
                padding=[dp(8), dp(6)], spacing=dp(8),
            )
            # Separator line on top
            row.canvas_before = None

            # Image placeholder
            img_box = MDCard(
                size_hint=(None, None), size=(dp(48), dp(48)),
                radius=[dp(6)], elevation=0,
                md_bg_color=[0.20, 0.28, 0.22, 1],
                pos_hint={"center_y": 0.5},
            )
            img_box.add_widget(MDIcon(
                icon="image-outline", font_size="24sp",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.4, 0.6, 0.4, 1],
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            ))
            row.add_widget(img_box)

            # Name + prices
            info = MDBoxLayout(
                orientation="vertical", spacing=dp(2),
            )
            # Product name (bold)
            name_text = f"{it['product_name']} — {int(pp)}"
            info.add_widget(MDLabel(
                text=name_text, font_style="Body1", bold=True,
                theme_text_color="Custom", text_color=[1, 1, 1, 1],
                size_hint_y=0.45,
            ))
            # Price line: purchase / total
            price_text = f"{_fmt_money(pp)} / {_fmt_money(subtotal_p)}"
            info.add_widget(MDLabel(
                text=price_text, font_style="Caption",
                theme_text_color="Custom", text_color=[0.6, 0.6, 0.6, 1],
                size_hint_y=0.25,
            ))
            # Time
            info.add_widget(MDLabel(
                text=time_str, font_style="Caption",
                theme_text_color="Custom", text_color=[0.4, 0.4, 0.4, 1],
                size_hint_y=0.2,
            ))
            row.add_widget(info)

            # Quantity on right
            row.add_widget(MDLabel(
                text=str(qty), font_style="H6", bold=True,
                halign="right",
                theme_text_color="Custom", text_color=[1, 1, 1, 1],
                size_hint_x=None, width=dp(36),
            ))

            box.add_widget(row)

            # Separator
            sep = MDBoxLayout(
                size_hint_y=None, height=dp(1),
                md_bg_color=[0.22, 0.22, 0.24, 1],
            )
            box.add_widget(sep)

        # Bottom bar
        self.ids.bottom_items.text = str(len(items))
        self.ids.bottom_qty.text = str(total_qty)
        self.ids.bottom_total.text = _fmt_money(total_purchase)

    def _load_open(self, box):
        items = self.open_items_data
        if not items:
            box.add_widget(MDLabel(text="Нет позиций", halign="center",
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(60)))
            self.ids.bottom_items.text = "0"
            self.ids.bottom_qty.text = "0"
            self.ids.bottom_total.text = "0р."
            return

        self.ids.toolbar.title = "Открытая продажа"
        buyer_name = items[0].get("buyer_name", "—")
        sup_name = items[0].get("supplier_name", "—")

        today = dt_date.today().strftime("%d.%m.%Y")
        self.ids.doc_date.text = today
        self.ids.doc_number.text = "—"
        self.ids.status_icon.icon = "timer-sand"
        self.ids.status_icon.text_color = [0.85, 0.20, 0.20, 1]
        self.ids.party_label.text = "Покупатель / Поставщик"
        self.ids.party_name.text = f"{buyer_name} / {sup_name}"
        self.ids.note_text.text = "Ожидает подтверждения"

        total = 0
        total_qty = 0
        for it in items:
            qty = it["quantity"]
            pp = it["purchase_price"]
            subtotal = pp * qty
            total += subtotal
            total_qty += qty

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(72),
                padding=[dp(8), dp(6)], spacing=dp(8),
            )
            img_box = MDCard(
                size_hint=(None, None), size=(dp(48), dp(48)),
                radius=[dp(6)], elevation=0,
                md_bg_color=[0.20, 0.28, 0.22, 1],
                pos_hint={"center_y": 0.5},
            )
            img_box.add_widget(MDIcon(
                icon="image-outline", font_size="24sp", halign="center",
                theme_text_color="Custom", text_color=[0.4, 0.6, 0.4, 1],
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            ))
            row.add_widget(img_box)

            info = MDBoxLayout(orientation="vertical", spacing=dp(2))
            info.add_widget(MDLabel(
                text=f"{it['product_name']} — {int(pp)}",
                font_style="Body1", bold=True,
                theme_text_color="Custom", text_color=[1, 1, 1, 1],
                size_hint_y=0.5,
            ))
            info.add_widget(MDLabel(
                text=f"{_fmt_money(pp)} / {_fmt_money(subtotal)}",
                font_style="Caption",
                theme_text_color="Custom", text_color=[0.6, 0.6, 0.6, 1],
                size_hint_y=0.3,
            ))
            row.add_widget(info)

            row.add_widget(MDLabel(
                text=str(qty), font_style="H6", bold=True, halign="right",
                theme_text_color="Custom", text_color=[1, 1, 1, 1],
                size_hint_x=None, width=dp(36),
            ))
            box.add_widget(row)
            box.add_widget(MDBoxLayout(
                size_hint_y=None, height=dp(1),
                md_bg_color=[0.22, 0.22, 0.24, 1],
            ))

        # Action buttons
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        box.add_widget(Widget(size_hint_y=None, height=dp(12)))

        # Withdrawals section
        if self.open_sale_ids:
            sale_id = self.open_sale_ids[0]
            withdrawals = db.get_withdrawals(sale_id)
            if withdrawals:
                box.add_widget(MDLabel(
                    text="  💸 Снятия:", font_style="Subtitle2", bold=True,
                    theme_text_color="Custom", text_color=[0.95, 0.55, 0.15, 1],
                    size_hint_y=None, height=dp(28),
                ))
                for w in withdrawals:
                    st = "✅" if w["status"] == "done" else "⏳"
                    w_row = MDBoxLayout(
                        orientation="horizontal", size_hint_y=None, height=dp(36),
                        padding=[dp(16), 0], spacing=dp(8),
                    )
                    w_row.add_widget(MDLabel(
                        text=f"  {st} {_fmt_money(w['amount'])}",
                        font_style="Body2",
                        theme_text_color="Custom",
                        text_color=[1, 1, 1, 1] if w["status"] == "done" else [0.7, 0.7, 0.7, 1],
                    ))
                    if w["status"] == "pending":
                        proc_btn = MDFlatButton(
                            text="Провести", font_size="12sp",
                            theme_text_color="Custom", text_color=[0.30, 0.85, 0.50, 1],
                            size_hint_x=None, width=dp(80),
                            on_release=lambda x, wid=w["id"]: self._process_withdrawal(wid),
                        )
                        w_row.add_widget(proc_btn)
                    del_btn = MDFlatButton(
                        text="✕", font_size="14sp",
                        theme_text_color="Custom", text_color=[0.85, 0.20, 0.20, 1],
                        size_hint_x=None, width=dp(40),
                        on_release=lambda x, wid=w["id"]: self._delete_withdrawal(wid),
                    )
                    w_row.add_widget(del_btn)
                    box.add_widget(w_row)
                box.add_widget(Widget(size_hint_y=None, height=dp(8)))

        btn_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(48),
            padding=[dp(16), 0], spacing=dp(12),
        )
        btn_row.add_widget(MDRaisedButton(
            text="Подтвердить",
            md_bg_color=[0.18, 0.74, 0.42, 1], text_color=[1, 1, 1, 1],
            size_hint_x=0.33,
            on_release=lambda x: self._confirm(),
        ))
        btn_row.add_widget(MDRaisedButton(
            text="💸 Снять",
            md_bg_color=[0.95, 0.55, 0.15, 1], text_color=[1, 1, 1, 1],
            size_hint_x=0.33,
            on_release=lambda x: self._add_withdrawal(),
        ))
        btn_row.add_widget(MDFlatButton(
            text="Отменить",
            theme_text_color="Custom", text_color=[0.85, 0.20, 0.20, 1],
            size_hint_x=0.33,
            on_release=lambda x: self._cancel(),
        ))
        box.add_widget(btn_row)

        self.ids.bottom_items.text = str(len(items))
        self.ids.bottom_qty.text = str(total_qty)
        self.ids.bottom_total.text = _fmt_money(total)

    # ── Снятия из открытых продаж ──
    def _add_withdrawal(self):
        if not self.open_sale_ids:
            return
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        self._w_field = MDTextField(hint_text="Сумма снятия", input_filter="float")
        self._w_dlg = MDDialog(
            title="💸 Снятие средств",
            type="custom",
            content_cls=self._w_field,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self._w_dlg.dismiss()),
                MDRaisedButton(
                    text="Снять",
                    md_bg_color=[0.95, 0.55, 0.15, 1],
                    text_color=[1, 1, 1, 1],
                    on_release=lambda x: self._save_withdrawal(),
                ),
            ],
        )
        self._w_dlg.open()

    def _save_withdrawal(self):
        try:
            amount = float(self._w_field.text.replace(",", ".").replace(" ", ""))
        except (ValueError, AttributeError):
            return
        if amount <= 0:
            return
        self._w_dlg.dismiss()
        sale_id = self.open_sale_ids[0]
        db.add_withdrawal(sale_id, amount)
        self.load_detail()

    def _process_withdrawal(self, withdrawal_id):
        items = self.open_items_data
        buyer_id = items[0].get("buyer_id") if items else None
        if buyer_id:
            db.process_withdrawal(withdrawal_id, buyer_id)
        self.load_detail()

    def _delete_withdrawal(self, withdrawal_id):
        db.delete_withdrawal(withdrawal_id)
        self.load_detail()

    def _confirm(self):
        items = self.open_items_data
        if not items:
            return
        buyer_id = items[0].get("buyer_id")
        sup_name = (items[0].get("supplier_name") or "").strip()
        supplier_id = None
        if sup_name:
            for s in db.get_suppliers():
                if s["name"].strip().lower() == sup_name.lower():
                    supplier_id = s["id"]
                    break
        order_items = [{
            "product_name": it["product_name"],
            "quantity": it["quantity"],
            "purchase_price": it["purchase_price"],
            "sale_price": it.get("sale_price", 0),
        } for it in items]
        today = dt_date.today().strftime("%Y-%m-%d")
        db.create_order(date=today, supplier_id=supplier_id, buyer_id=buyer_id,
                        items=order_items, doc_type="expense")
        for sid in self.open_sale_ids:
            db.close_open_sale(sid)
        self.go_back()

    def _cancel(self):
        for sid in self.open_sale_ids:
            db.delete_open_sale(sid)
        self.go_back()

    # ── Удаление документа ──
    def ask_delete(self):
        if self.doc_mode == "open":
            return
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        self._del_dlg = MDDialog(
            title="Удалить документ?",
            text="Это действие нельзя отменить.",
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self._del_dlg.dismiss()),
                MDRaisedButton(
                    text="Удалить",
                    md_bg_color=[0.85, 0.20, 0.20, 1],
                    text_color=[1, 1, 1, 1],
                    on_release=lambda x: self._do_delete(),
                ),
            ],
        )
        self._del_dlg.open()

    def _do_delete(self):
        self._del_dlg.dismiss()
        if self.order_id:
            db.delete_order(self.order_id)
        self.go_back()

    def go_back(self):
        self.manager.current = self.return_screen
