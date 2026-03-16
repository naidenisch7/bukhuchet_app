"""
Бухучет — мобильное приложение для учёта продаж электроники.
Тёмная тема в стиле «Учёт Товаров».
"""
import os
import sys

os.environ["KIVY_LOG_LEVEL"] = "warning"

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp
from kivymd.app import MDApp

import db

if sys.platform != "android":
    Window.size = (420, 760)

# ──── Navigation Drawer layout ────
Builder.load_string("""
#:import dp kivy.metrics.dp

<DrawerItem@MDBoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(48)
    padding: dp(16), 0
    spacing: dp(16)
    icon_name: ""
    label_text: ""
    active: False

    canvas.before:
        Color:
            rgba: (0.18, 0.74, 0.42, 0.15) if root.active else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

    MDIcon:
        icon: root.icon_name
        halign: "center"
        font_size: "22sp"
        size_hint: None, 1
        width: dp(28)
        theme_text_color: "Custom"
        text_color: (0.3, 0.85, 0.5, 1) if root.active else (0.6, 0.6, 0.6, 1)

    MDLabel:
        text: root.label_text
        font_style: "Body1"
        theme_text_color: "Custom"
        text_color: (1, 1, 1, 1) if root.active else (0.85, 0.85, 0.85, 1)
        valign: "center"

<DrawerSeparator@MDBoxLayout>:
    size_hint_y: None
    height: dp(1)
    md_bg_color: 0.25, 0.25, 0.27, 1

<ContentNavigationDrawer>:
    orientation: "vertical"
    md_bg_color: 0.12, 0.12, 0.14, 1
    padding: 0

    # Header
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(64)
        padding: dp(16), dp(12)
        spacing: dp(12)

        MDIcon:
            icon: "package-variant-closed"
            font_size: "36sp"
            size_hint: None, 1
            width: dp(40)
            theme_text_color: "Custom"
            text_color: 0.3, 0.85, 0.5, 1

        MDBoxLayout:
            orientation: "vertical"

            MDLabel:
                text: "Бухучет"
                font_style: "H6"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

            MDLabel:
                text: "v1.0"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1

    # Green accent
    MDBoxLayout:
        size_hint_y: None
        height: dp(36)
        md_bg_color: 0.18, 0.74, 0.42, 1
        padding: dp(16), 0

        MDLabel:
            text: "Учёт продаж"
            font_style: "Body2"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            valign: "center"

        MDIcon:
            icon: "menu-down"
            halign: "right"
            font_size: "24sp"
            size_hint: None, 1
            width: dp(28)
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

    ScrollView:
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: dp(8), dp(8)
            spacing: dp(2)

            DrawerItem:
                icon_name: "home-outline"
                label_text: "Главное меню"
                active: True
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("main_menu")

            DrawerItem:
                icon_name: "package-variant-closed"
                label_text: "Товары"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("orders")

            DrawerItem:
                icon_name: "file-document-outline"
                label_text: "Документы"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("income")

            DrawerItem:
                icon_name: "cash-multiple"
                label_text: "Затраты"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("expenses_list")

            DrawerItem:
                icon_name: "chart-bar"
                label_text: "Отчеты"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("reports")

            DrawerItem:
                icon_name: "undo-variant"
                label_text: "Возвраты"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("returns")

            DrawerItem:
                icon_name: "wrench-outline"
                label_text: "Гарантия"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("warranty")

            DrawerSeparator:

            DrawerItem:
                icon_name: "truck-outline"
                label_text: "Поставщики"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("suppliers")

            DrawerItem:
                icon_name: "account-cash-outline"
                label_text: "Покупатели"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("buyers")

            DrawerSeparator:

            DrawerItem:
                icon_name: "cog-outline"
                label_text: "Настройки"

            DrawerSeparator:

            DrawerItem:
                icon_name: "text-recognition"
                label_text: "Авто-продажи"
                on_touch_up: if self.collide_point(*args[1].pos): app.nav_to("auto_sales")

            DrawerItem:
                icon_name: "help-circle-outline"
                label_text: "Нужна помощь?"

            DrawerItem:
                icon_name: "information-outline"
                label_text: "Справка"

            DrawerItem:
                icon_name: "star-outline"
                label_text: "Что нового"

    # Footer
    MDBoxLayout:
        size_hint_y: None
        height: dp(1)
        md_bg_color: 0.25, 0.25, 0.27, 1

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(48)
        padding: dp(16), 0
        md_bg_color: 0.10, 0.10, 0.12, 1

        MDLabel:
            text: "Бухучет Электроника"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            valign: "center"

        MDIconButton:
            icon: "logout"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
""")

# Цвета тёмной темы
DARK_BG = [0.12, 0.12, 0.14, 1]
DARK_CARD = [0.18, 0.18, 0.20, 1]
DARK_BAR = [0.10, 0.10, 0.12, 1]
ACCENT_GREEN = [0.18, 0.74, 0.42, 1]
ACCENT_ORANGE = [0.95, 0.55, 0.15, 1]
ACCENT_BLUE = [0.20, 0.60, 0.95, 1]


from kivymd.uix.boxlayout import MDBoxLayout

class ContentNavigationDrawer(MDBoxLayout):
    pass


class BukhuchetApp(MDApp):
    title = "Бухучет"

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = "M3"

        db.init_db()

        from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer

        # Root layout
        nav_layout = MDNavigationLayout()

        # ScreenManager
        self.sm = ScreenManager(transition=SlideTransition())

        from screens.main_menu import MainMenuScreen
        from screens.buyers import BuyersScreen, BuyerDetailScreen, BuyerEditScreen, MarkupScreen
        from screens.suppliers import SuppliersScreen, SupplierDetailScreen, SupplierEditScreen
        from screens.new_order import NewOrderScreen
        from screens.auto_sales import AutoSalesScreen
        from screens.income import IncomeScreen
        from screens.expense import ExpenseScreen
        from screens.orders import OrdersScreen
        from screens.doc_detail import DocDetailScreen
        from screens.expenses_screen import ExpensesScreen as ExpensesListScreen
        from screens.reports_screen import ReportsScreen
        from screens.returns_screen import ReturnsScreen
        from screens.warranty_screen import WarrantyScreen

        self.sm.add_widget(MainMenuScreen(name="main_menu"))
        self.sm.add_widget(BuyersScreen(name="buyers"))
        self.sm.add_widget(BuyerDetailScreen(name="buyer_detail"))
        self.sm.add_widget(BuyerEditScreen(name="buyer_edit"))
        self.sm.add_widget(MarkupScreen(name="markup"))
        self.sm.add_widget(SuppliersScreen(name="suppliers"))
        self.sm.add_widget(SupplierDetailScreen(name="supplier_detail"))
        self.sm.add_widget(SupplierEditScreen(name="supplier_edit"))
        self.sm.add_widget(NewOrderScreen(name="new_order"))
        self.sm.add_widget(AutoSalesScreen(name="auto_sales"))
        self.sm.add_widget(IncomeScreen(name="income"))
        self.sm.add_widget(ExpenseScreen(name="expense"))
        self.sm.add_widget(OrdersScreen(name="orders"))
        self.sm.add_widget(DocDetailScreen(name="doc_detail"))
        self.sm.add_widget(ExpensesListScreen(name="expenses_list"))
        self.sm.add_widget(ReportsScreen(name="reports"))
        self.sm.add_widget(ReturnsScreen(name="returns"))
        self.sm.add_widget(WarrantyScreen(name="warranty"))

        nav_layout.add_widget(self.sm)

        # Navigation Drawer
        self.nav_drawer = MDNavigationDrawer(
            id="nav_drawer",
            radius=[0, dp(16), dp(16), 0],
            elevation=0,
        )
        self.nav_drawer.md_bg_color = [0.12, 0.12, 0.14, 1]

        drawer_content = ContentNavigationDrawer()
        self.nav_drawer.add_widget(drawer_content)

        nav_layout.add_widget(self.nav_drawer)

        return nav_layout

    def open_drawer(self):
        self.nav_drawer.set_state("open")

    def nav_to(self, screen_name):
        self.sm.current = screen_name
        self.nav_drawer.set_state("close")


if __name__ == "__main__":
    BukhuchetApp().run()
