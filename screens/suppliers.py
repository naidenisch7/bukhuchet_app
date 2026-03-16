"""Экран поставщиков: список, детали, редактирование — тёмная тема."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<SuppliersScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Поставщики"
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
                    id: supplier_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.95, 0.55, 0.15, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.add_supplier()

<SupplierDetailScreen>:
    supplier_id: 0
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Поставщик"
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
                    padding: dp(20)
                    size_hint_y: None
                    height: dp(70)
                    elevation: 0
                    radius: [dp(12)]
                    md_bg_color: 0.95, 0.55, 0.15, 1

                    MDLabel:
                        id: sup_name
                        text: ""
                        font_style: "H5"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

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
                        id: sup_info
                        text: ""
                        font_style: "Body1"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

                MDFillRoundFlatButton:
                    text: "Редактировать"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.20, 0.60, 0.95, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.edit_supplier()

                MDFillRoundFlatButton:
                    text: "Удалить поставщика"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.75, 0.15, 0.15, 1
                    text_color: 1, 1, 1, 1
                    on_release: root.delete_supplier()

                MDLabel:
                    text: "Заказы поставщика"
                    font_style: "Subtitle1"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    size_hint_y: None
                    height: dp(36)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(6)
                    adaptive_height: True
                    id: orders_box

<SupplierEditScreen>:
    supplier_id: 0
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
                hint_text: "Имя поставщика"
                mode: "rectangle"
                icon_left: "truck"

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
                md_bg_color: 0.95, 0.55, 0.15, 1
                text_color: 1, 1, 1, 1
                on_release: root.save()
""")


class SuppliersScreen(MDScreen):
    dialog = None

    def on_enter(self):
        self.load_suppliers()

    def load_suppliers(self):
        box = self.ids.supplier_list
        box.clear_widgets()
        suppliers = db.get_suppliers()
        if not suppliers:
            box.add_widget(MDLabel(
                text="Нет поставщиков",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(80),
            ))
            return
        for s in suppliers:
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                size_hint_y=None,
                height=dp(78),
                elevation=0,
                radius=[dp(12)],
                ripple_behavior=True,
                md_bg_color=[0.18, 0.18, 0.20, 1],
                on_release=lambda x, sid=s["id"]: self.open_supplier(sid),
            )
            card.add_widget(MDLabel(
                text=s['name'],
                font_style="Subtitle1",
                bold=True,
                size_hint_y=0.5,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
            ))
            card.add_widget(MDLabel(
                text=f"Депозит: {s['deposit']:.0f}  |  Долг: {s['debt']:.0f}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=[0.6, 0.6, 0.6, 1],
                size_hint_y=0.5,
            ))
            box.add_widget(card)

    def open_supplier(self, supplier_id):
        scr = self.manager.get_screen("supplier_detail")
        scr.supplier_id = supplier_id
        self.manager.current = "supplier_detail"

    def add_supplier(self):
        if self.dialog:
            self.dialog.dismiss()
        content = MDTextField(hint_text="Имя поставщика", mode="rectangle")
        self.dialog = MDDialog(
            title="➕ Новый поставщик",
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
            db.add_supplier(name)
            self.dialog.dismiss()
            self.load_suppliers()

    def go_back(self):
        self.manager.current = "main_menu"


class SupplierDetailScreen(MDScreen):
    supplier_id = NumericProperty(0)

    def on_enter(self):
        self.load_data()

    def load_data(self):
        sup = db.get_supplier(self.supplier_id)
        if not sup:
            self.manager.current = "suppliers"
            return
        self.ids.sup_name.text = sup["name"]
        self.ids.sup_info.text = (
            f"Депозит: {sup['deposit']:.0f}      Долг: {sup['debt']:.0f}"
        )

    def edit_supplier(self):
        scr = self.manager.get_screen("supplier_edit")
        scr.supplier_id = self.supplier_id
        self.manager.current = "supplier_edit"

    def delete_supplier(self):
        db.delete_supplier(self.supplier_id)
        self.manager.current = "suppliers"

    def go_back(self):
        self.manager.current = "suppliers"


class SupplierEditScreen(MDScreen):
    supplier_id = NumericProperty(0)

    def on_enter(self):
        sup = db.get_supplier(self.supplier_id)
        if sup:
            self.ids.name_field.text = sup["name"]
            self.ids.deposit_field.text = str(sup["deposit"])
            self.ids.debt_field.text = str(sup["debt"])

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
            db.update_supplier(self.supplier_id, name=name, deposit=deposit, debt=debt)
        self.manager.current = "supplier_detail"

    def go_back(self):
        self.manager.current = "supplier_detail"
