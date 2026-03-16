"""Главное меню — тёмная тема в стиле «Учёт Товаров»."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen

Builder.load_string("""
#:import dp kivy.metrics.dp

<DarkMenuCard@MDCard>:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(4)
    size_hint: None, None
    size: dp(180), dp(120)
    elevation: 0
    radius: [dp(8)]
    ripple_behavior: True
    md_bg_color: 0.18, 0.18, 0.20, 1
    icon_text: ""
    label_text: ""
    sub_text: ""

    Widget:
        size_hint_y: 0.1

    MDIcon:
        icon: root.icon_text
        halign: "center"
        font_size: "36sp"
        size_hint_y: 0.45
        theme_text_color: "Custom"
        text_color: 0.7, 0.7, 0.7, 1

    MDLabel:
        text: root.label_text
        halign: "center"
        font_style: "Body1"
        bold: True
        size_hint_y: 0.25
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1

    MDLabel:
        text: root.sub_text
        halign: "center"
        font_style: "Caption"
        size_hint_y: 0.2
        theme_text_color: "Custom"
        text_color: 0.3, 0.85, 0.5, 1

<SmallIconCard@MDCard>:
    orientation: "vertical"
    padding: dp(8)
    size_hint: None, None
    size: dp(85), dp(70)
    elevation: 0
    radius: [dp(8)]
    ripple_behavior: True
    md_bg_color: 0.18, 0.18, 0.20, 1
    icon_text: ""
    label_text: ""

    MDIcon:
        icon: root.icon_text
        halign: "center"
        font_size: "24sp"
        size_hint_y: 0.55
        theme_text_color: "Custom"
        text_color: 0.7, 0.7, 0.7, 1

    MDLabel:
        text: root.label_text
        halign: "center"
        font_style: "Caption"
        size_hint_y: 0.45
        theme_text_color: "Custom"
        text_color: 0.85, 0.85, 0.85, 1

<MainMenuScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDBoxLayout:
        orientation: "vertical"

        # Top bar
        MDTopAppBar:
            title: "Бухучет"
            elevation: 0
            md_bg_color: 0.10, 0.10, 0.12, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["menu", lambda x: app.open_drawer()]]

        # Accent strip
        MDBoxLayout:
            size_hint_y: None
            height: dp(32)
            md_bg_color: 0.18, 0.74, 0.42, 1
            padding: dp(12), 0

            MDLabel:
                text: "Учёт продаж электроники"
                halign: "center"
                font_style: "Caption"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

        # Main grid
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(10)
                padding: dp(14), dp(14)
                adaptive_height: True

                # Row 1
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(120)
                    pos_hint: {"center_x": 0.5}

                    DarkMenuCard:
                        icon_text: "package-variant-closed"
                        label_text: "Товары"
                        on_release: root.go_orders()

                    DarkMenuCard:
                        icon_text: "file-document-outline"
                        label_text: "Документы"
                        on_release: root.go_income()

                # Row 2
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(120)
                    pos_hint: {"center_x": 0.5}

                    DarkMenuCard:
                        icon_text: "chart-bar"
                        label_text: "Отчеты"
                        on_release: root.go_orders()

                    DarkMenuCard:
                        icon_text: "cash-multiple"
                        label_text: "Затраты"
                        on_release: root.go_expense()

                # Row 3
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(120)
                    pos_hint: {"center_x": 0.5}

                    DarkMenuCard:
                        icon_text: "arrow-down-bold-box-outline"
                        label_text: "новый Приход"
                        on_release: root.go_new_order_income()

                    DarkMenuCard:
                        icon_text: "arrow-up-bold-box-outline"
                        label_text: "новый Расход"
                        on_release: root.go_new_order_expense()

                # Row 4
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(120)
                    pos_hint: {"center_x": 0.5}

                    DarkMenuCard:
                        icon_text: "text-recognition"
                        label_text: "Авто-продажи"
                        on_release: root.go_auto_sales()

                    DarkMenuCard:
                        icon_text: "help-circle-outline"
                        label_text: "Нужна помощь?"

                # Bottom small icons row
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(70)
                    pos_hint: {"center_x": 0.5}

                    SmallIconCard:
                        icon_text: "truck-outline"
                        label_text: "Поставщ."
                        on_release: root.go_suppliers()

                    SmallIconCard:
                        icon_text: "account-cash-outline"
                        label_text: "Покупат."
                        on_release: root.go_buyers()

                    SmallIconCard:
                        icon_text: "cog-outline"
                        label_text: "Настр."

                    SmallIconCard:
                        icon_text: "information-outline"
                        label_text: "Справка"
""")


class MainMenuScreen(MDScreen):

    def go_buyers(self):
        self.manager.current = "buyers"

    def go_suppliers(self):
        self.manager.current = "suppliers"

    def go_new_order_income(self):
        scr = self.manager.get_screen("new_order")
        scr.preset_type = "income"
        self.manager.current = "new_order"

    def go_new_order_expense(self):
        scr = self.manager.get_screen("new_order")
        scr.preset_type = "expense"
        self.manager.current = "new_order"

    def go_auto_sales(self):
        self.manager.current = "auto_sales"

    def go_income(self):
        self.manager.current = "income"

    def go_expense(self):
        self.manager.current = "expense"

    def go_orders(self):
        self.manager.current = "orders"
