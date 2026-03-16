"""Экран создания нового заказа — тёмная тема."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.label import MDLabel
import db
from parser import parse_product_lines
from datetime import date as dt_date

Builder.load_string("""
#:import dp kivy.metrics.dp

<NewOrderScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Новый заказ"
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
                id: content_box

                MDLabel:
                    id: step_label
                    text: "Шаг 1: Выберите тип документа"
                    font_style: "H6"
                    halign: "center"
                    bold: True
                    size_hint_y: None
                    height: dp(44)
                    theme_text_color: "Custom"
                    text_color: 0.3, 0.85, 0.5, 1

                MDFillRoundFlatButton:
                    id: btn_income
                    text: "Приходный"
                    pos_hint: {"center_x": 0.5}
                    size_hint_x: 0.8
                    md_bg_color: 0.95, 0.55, 0.15, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.select_type("income")

                MDFillRoundFlatButton:
                    id: btn_expense
                    text: "Расходный"
                    pos_hint: {"center_x": 0.5}
                    size_hint_x: 0.8
                    md_bg_color: 0.20, 0.60, 0.95, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.select_type("expense")

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(4)
                    adaptive_height: True
                    id: entity_list

                MDTextField:
                    id: items_input
                    hint_text: "Вставьте список товаров"
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: None
                    height: dp(200)
                    opacity: 0

                MDFillRoundFlatButton:
                    id: btn_parse
                    text: "Распознать товары"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.18, 0.74, 0.42, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.parse_items()
                    opacity: 0

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
                    text: "Сохранить заказ"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.18, 0.74, 0.42, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.save_order()
                    opacity: 0
""")


class NewOrderScreen(MDScreen):
    step = NumericProperty(1)
    doc_type = StringProperty("income")
    supplier_id = NumericProperty(0)
    buyer_id = NumericProperty(0)
    parsed_items = ListProperty([])
    preset_type = StringProperty("")

    def on_enter(self):
        self.supplier_id = 0
        self.buyer_id = 0
        self.parsed_items = []
        if self.preset_type:
            self.doc_type = self.preset_type
            self.preset_type = ""
            self.step = 2
        else:
            self.step = 1
        self._update_ui()

    def _update_ui(self):
        step = self.step
        self.ids.btn_income.opacity = 1 if step == 1 else 0
        self.ids.btn_income.disabled = step != 1
        self.ids.btn_expense.opacity = 1 if step == 1 else 0
        self.ids.btn_expense.disabled = step != 1
        self.ids.entity_list.clear_widgets()
        self.ids.items_input.opacity = 0
        self.ids.items_input.disabled = True
        self.ids.btn_parse.opacity = 0
        self.ids.btn_parse.disabled = True
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True
        self.ids.result_label.text = ""
        self.ids.result_card.elevation = 0
        self.ids.result_card.md_bg_color = [1, 1, 1, 0]

        if step == 1:
            self.ids.step_label.text = "Шаг 1: Выберите тип документа"
        elif step == 2:
            self.ids.step_label.text = "Шаг 2: Выберите поставщика"
            self._show_entities(db.get_suppliers(), "supplier")
        elif step == 3:
            self.ids.step_label.text = "Шаг 3: Выберите покупателя"
            self._show_entities(db.get_buyers(), "buyer")
        elif step == 4:
            self.ids.step_label.text = "Шаг 4: Вставьте товары"
            self.ids.items_input.opacity = 1
            self.ids.items_input.disabled = False
            self.ids.items_input.text = ""
            self.ids.btn_parse.opacity = 1
            self.ids.btn_parse.disabled = False
        elif step == 5:
            self.ids.step_label.text = "✅ Проверьте и сохраните"
            self.ids.btn_save.opacity = 1
            self.ids.btn_save.disabled = False

    def _show_entities(self, entities, etype):
        box = self.ids.entity_list
        for e in entities:
            card = MDCard(
                orientation="vertical",
                padding=dp(14),
                size_hint_y=None,
                height=dp(56),
                elevation=0,
                radius=[dp(12)],
                ripple_behavior=True,
                md_bg_color=[0.18, 0.18, 0.20, 1],
                on_release=lambda x, eid=e["id"]: (
                    self._select_supplier(eid) if etype == "supplier"
                    else self._select_buyer(eid)
                ),
            )
            card.add_widget(MDLabel(
                text=e['name'],
                font_style="Subtitle1",
                valign="center",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
            ))
            box.add_widget(card)

    def select_type(self, doc_type):
        self.doc_type = doc_type
        self.step = 2
        self._update_ui()

    def _select_supplier(self, sid):
        self.supplier_id = sid
        self.step = 3
        self._update_ui()

    def _select_buyer(self, bid):
        self.buyer_id = bid
        self.step = 4
        self._update_ui()

    def parse_items(self):
        text = self.ids.items_input.text.strip()
        if not text:
            return
        items = parse_product_lines(text)
        if not items:
            self.ids.result_label.text = "Товары не распознаны"
            self.ids.result_card.elevation = 0
            self.ids.result_card.md_bg_color = [0.3, 0.15, 0.15, 1]
            self.ids.result_card.height = dp(60)
            return
        self.parsed_items = [
            {"product_name": it.product_name, "quantity": it.quantity,
             "purchase_price": it.purchase_price, "sale_price": it.sale_price}
            for it in items
        ]
        lines = [f"Распознано {len(items)} товаров:\n"]
        total_p = total_s = 0
        for i, it in enumerate(items, 1):
            lines.append(f"{i}. {it.product_name} × {it.quantity} | {it.purchase_price}→{it.sale_price}")
            total_p += it.purchase_total
            total_s += it.sale_total
        lines.append(f"\nЗакупка: {total_p}")
        lines.append(f"Продажа: {total_s}")
        lines.append(f"Прибыль: {total_s - total_p}")
        self.ids.result_label.text = "\n".join(lines)
        self.ids.result_card.elevation = 0
        self.ids.result_card.md_bg_color = [0.15, 0.25, 0.15, 1]
        self.ids.result_card.height = dp(max(200, len(items) * 28 + 120))
        self.step = 5
        self.ids.step_label.text = "✅ Проверьте и сохраните"
        self.ids.btn_save.opacity = 1
        self.ids.btn_save.disabled = False

    def save_order(self):
        if not self.parsed_items:
            return
        today = dt_date.today().strftime("%Y-%m-%d")
        order_id, doc_num = db.create_order(
            date=today, supplier_id=self.supplier_id,
            buyer_id=self.buyer_id, items=self.parsed_items,
            doc_type=self.doc_type,
        )
        self.ids.result_label.text += f"\n\n✅ Заказ {doc_num} сохранён!"
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True

    def go_back(self):
        if self.step > 1:
            self.step -= 1
            self._update_ui()
        else:
            self.manager.current = "main_menu"
