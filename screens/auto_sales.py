"""Экран авто-продаж — тёмная тема."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
import db
from parser import parse_full_message

Builder.load_string("""
#:import dp kivy.metrics.dp

<AutoSalesScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Авто-продажи"
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

                MDCard:
                    orientation: "vertical"
                    padding: dp(14)
                    size_hint_y: None
                    height: dp(56)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.18, 0.18, 0.20, 1

                    MDLabel:
                        text: "Вставьте текст с товарами:\\nПоставщик(Покупатель) + товары"
                        halign: "center"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1

                MDTextField:
                    id: text_input
                    hint_text: "Вставьте текст заказа..."
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: None
                    height: dp(200)

                MDFillRoundFlatButton:
                    text: "Распознать"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.18, 0.74, 0.42, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.parse_text()

                MDCard:
                    id: result_card
                    orientation: "vertical"
                    padding: dp(16)
                    size_hint_y: None
                    height: dp(10)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.18, 0.18, 0.20, 0

                    MDLabel:
                        id: result_label
                        text: ""
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                MDFillRoundFlatButton:
                    id: btn_save
                    text: "Сохранить"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.18, 0.74, 0.42, 1
                    text_color: 1, 1, 1, 1
                    opacity: 0
                    disabled: True
                    on_release: root.save_order()
""")


class AutoSalesScreen(MDScreen):
    parsed_order = None

    def on_enter(self):
        self.ids.text_input.text = ""
        self.ids.result_label.text = ""
        self.ids.result_card.elevation = 0
        self.ids.result_card.md_bg_color = [0.18, 0.18, 0.20, 0]
        self.ids.result_card.height = dp(10)
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True
        self.parsed_order = None

    def parse_text(self):
        text = self.ids.text_input.text.strip()
        if not text:
            return

        order = parse_full_message(text)
        if not order.items:
            self.ids.result_label.text = "Товары не распознаны"
            self.ids.result_card.elevation = 0
            self.ids.result_card.md_bg_color = [0.3, 0.15, 0.15, 1]
            self.ids.result_card.height = dp(60)
            return

        self.parsed_order = order
        lines = []
        lines.append(f"📦 Поставщик: {order.supplier or '—'}")
        lines.append(f"🛒 Покупатель: {order.buyer or '—'}")
        if order.manager_count > 1:
            lines.append(f"👥 Менеджеров: {order.manager_count}")
        lines.append(f"\nРаспознано {len(order.items)} товаров:\n")
        for i, it in enumerate(order.items, 1):
            lines.append(f"{i}. {it.product_name} × {it.quantity} | {it.purchase_price}→{it.sale_price}")
        lines.append(f"\nЗакупка: {order.total_purchase}")
        lines.append(f"Продажа: {order.total_sale}")
        lines.append(f"Прибыль: {order.total_profit}")
        if order.manager_count > 1:
            lines.append(f"👤 На менеджера: {order.profit_per_manager:.0f}")

        self.ids.result_label.text = "\n".join(lines)
        self.ids.result_card.elevation = 0
        self.ids.result_card.md_bg_color = [0.15, 0.25, 0.15, 1]
        self.ids.result_card.height = dp(max(200, len(order.items) * 28 + 150))
        self.ids.btn_save.opacity = 1
        self.ids.btn_save.disabled = False

    def save_order(self):
        if not self.parsed_order:
            return

        order = self.parsed_order
        supplier_id = buyer_id = None

        if order.supplier:
            sup = db.find_supplier_by_name(order.supplier)
            supplier_id = sup["id"] if sup else db.add_supplier(order.supplier)

        if order.buyer:
            buy = db.find_buyer_by_name(order.buyer)
            buyer_id = buy["id"] if buy else db.add_buyer(order.buyer)

        items = [
            {"product_name": it.product_name, "quantity": it.quantity,
             "purchase_price": it.purchase_price, "sale_price": it.sale_price}
            for it in order.items
        ]

        from datetime import date as dt_date
        today = dt_date.today().strftime("%Y-%m-%d")

        db.create_order(date=today, supplier_id=supplier_id, buyer_id=buyer_id,
                        items=items, doc_type="income")
        order_id, doc_num = db.create_order(
            date=today, supplier_id=supplier_id, buyer_id=buyer_id,
            items=items, doc_type="expense")

        self.ids.result_label.text += f"\n\n✅ Заказ {doc_num} сохранён!"
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True

    def go_back(self):
        self.manager.current = "main_menu"
