"""Экран истории заказов — тёмная тема, группировка по датам."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from datetime import date as dt_date
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<OrdersScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Товары / История"
                left_action_items: [["arrow-left", lambda x: root.go_back()]]
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1

            # Summary card
            MDCard:
                orientation: "vertical"
                padding: dp(12)
                size_hint: 0.94, None
                height: dp(50)
                pos_hint: {"center_x": 0.5}
                elevation: 0
                radius: [dp(8)]
                md_bg_color: 0.18, 0.18, 0.20, 1

                MDLabel:
                    id: summary
                    text: ""
                    halign: "center"
                    font_style: "Subtitle2"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.3, 0.85, 0.5, 1

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: dp(8)
                    spacing: dp(0)
                    adaptive_height: True
                    id: order_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.18, 0.74, 0.42, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.new_order()
""")


def _fmt_money(val):
    s = f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}р."


def _fmt_date_header(date_str):
    months = {1: "янв.", 2: "фев.", 3: "мар.", 4: "апр.", 5: "мая",
              6: "июн.", 7: "июл.", 8: "авг.", 9: "сен.", 10: "окт.",
              11: "нояб.", 12: "дек."}
    try:
        d = dt_date.fromisoformat(date_str)
        return f"{d.day} {months[d.month]} {d.year} г."
    except Exception:
        return date_str


class OrdersScreen(MDScreen):

    def on_enter(self):
        self.load_orders()

    def load_orders(self):
        box = self.ids.order_list
        box.clear_widgets()

        orders = db.get_orders()
        if not orders:
            box.add_widget(MDLabel(
                text="Нет заказов",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(60),
            ))
            self.ids.summary.text = ""
            return

        total_profit = sum(o["profit"] for o in orders)
        self.ids.summary.text = f"{len(orders)} заказов  |  Прибыль: {total_profit:.0f}"

        by_date = {}
        for o in orders:
            d = o["date"]
            if d not in by_date:
                by_date[d] = []
            by_date[d].append(o)

        for date_str in sorted(by_date.keys(), reverse=True):
            day_orders = by_date[date_str]

            hdr = MDBoxLayout(
                size_hint_y=None, height=dp(36),
                md_bg_color=[0.15, 0.15, 0.17, 1],
                padding=[dp(16), 0],
            )
            hdr.add_widget(MDLabel(
                text=_fmt_date_header(date_str),
                font_style="Subtitle2", bold=True,
                theme_text_color="Custom", text_color=[0.9,0.9,0.9,1],
                valign="center",
            ))
            box.add_widget(hdr)

            for o in day_orders:
                doc_num = o.get("doc_number", "—")
                doc_type = o.get("doc_type", "income")
                is_income = doc_type == "income"

                if is_income:
                    entity = db.get_supplier(o["supplier_id"]) if o["supplier_id"] else None
                    name = entity["name"] if entity else "—"
                    amount = o["total_purchase"]
                    bar_color = [0.95, 0.55, 0.15, 1]  # Orange
                else:
                    entity = db.get_buyer(o["buyer_id"]) if o["buyer_id"] else None
                    name = entity["name"] if entity else "—"
                    amount = o["total_sale"]
                    bar_color = [0.20, 0.60, 0.95, 1]  # Blue

                items = db.get_order_items(o["id"])
                qty = sum(it["quantity"] for it in items)
                created = o.get("created_at", "")
                time_str = ""
                if created and len(created) > 10:
                    time_str = created[:16].replace("T", " ")

                card = MDCard(
                    orientation="horizontal",
                    size_hint_y=None, height=dp(85),
                    elevation=0, radius=[0],
                    md_bg_color=[0.12, 0.12, 0.14, 1],
                )

                bar = Widget(size_hint=(None, 1), width=dp(4))
                from kivy.graphics import Color, RoundedRectangle
                with bar.canvas:
                    Color(*bar_color)
                    bar._rect = RoundedRectangle(pos=bar.pos, size=(dp(4), bar.height), radius=[dp(2)])
                bar.bind(pos=lambda w, p: setattr(w._rect, 'pos', (p[0], p[1]+dp(8))))
                bar.bind(size=lambda w, s: setattr(w._rect, 'size', (dp(4), s[1]-dp(16))))
                card.add_widget(bar)

                left = MDBoxLayout(orientation="vertical", padding=[dp(12),dp(8)], spacing=dp(2), size_hint_x=0.6)
                left.add_widget(MDLabel(text=doc_num, font_style="H6", bold=True,
                    theme_text_color="Custom", text_color=[1,1,1,1], size_hint_y=0.4))
                type_label = "Приход" if is_income else "Расход"
                left.add_widget(MDLabel(text=f"{type_label} • {name}", font_style="Caption",
                    theme_text_color="Custom", text_color=[0.6,0.6,0.6,1], size_hint_y=0.3))
                left.add_widget(MDLabel(text=time_str, font_style="Caption",
                    theme_text_color="Custom", text_color=[0.45,0.45,0.45,1], size_hint_y=0.3))
                card.add_widget(left)

                right = MDBoxLayout(orientation="vertical", padding=[dp(8)], spacing=dp(2), size_hint_x=0.4)
                from kivymd.uix.label import MDIcon
                right.add_widget(MDIcon(icon="check-decagram", halign="right", font_size="18sp",
                    theme_text_color="Custom", text_color=[0.3,0.85,0.5,1], size_hint_y=0.25))
                right.add_widget(MDLabel(text=str(qty), halign="right", font_style="H6", bold=True,
                    theme_text_color="Custom", text_color=[1,1,1,1], size_hint_y=0.35))
                right.add_widget(MDLabel(text=_fmt_money(amount), halign="right",
                    font_style="Body2", theme_text_color="Custom", text_color=[0.8,0.8,0.8,1], size_hint_y=0.4))
                card.add_widget(right)

                box.add_widget(card)

    def new_order(self):
        self.manager.current = "new_order"

    def go_back(self):
        self.manager.current = "main_menu"
