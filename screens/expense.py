"""Экран расходных — тёмная тема, синие полоски, группировка по датам."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from datetime import date as dt_date, timedelta
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<ExpenseScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Документы"
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1
                left_action_items: [["arrow-left", lambda x: root.go_back()]]
                right_action_items: [["magnify", lambda x: None], ["microsoft-excel", lambda x: None]]

            # Tabs
            MDBoxLayout:
                size_hint_y: None
                height: dp(40)
                md_bg_color: 0.10, 0.10, 0.12, 1

                MDFlatButton:
                    text: "ПРИХОДНЫЕ"
                    pos_hint: {"center_y": 0.5}
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.6, 0.6, 1
                    font_size: "13sp"
                    on_release: root.go_income_tab()

                MDFlatButton:
                    text: "РАСХОДНЫЕ"
                    pos_hint: {"center_y": 0.5}
                    theme_text_color: "Custom"
                    text_color: 0.20, 0.60, 0.95, 1
                    font_size: "13sp"
                    on_release: root.show_expense()

            # Separator line
            MDBoxLayout:
                size_hint_y: None
                height: dp(2)
                md_bg_color: 0.20, 0.60, 0.95, 1

            # Date filter chips
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
                    id: doc_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.20, 0.60, 0.95, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.new_expense()
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


def _fmt_date_short(date_str):
    try:
        d = dt_date.fromisoformat(date_str)
        return d.strftime("%d.%m.%Y")
    except Exception:
        return date_str


class ExpenseScreen(MDScreen):
    date_filter = StringProperty("today")

    def on_enter(self):
        self._build_filter_chips()
        self.load_docs()

    def show_expense(self):
        self.load_docs()

    def go_income_tab(self):
        self.manager.current = "income"

    def set_filter(self, f):
        self.date_filter = f
        self._build_filter_chips()
        self.load_docs()

    def _build_filter_chips(self):
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        row = self.ids.filter_row
        row.clear_widgets()
        filters = [("today", "Сегодня"), ("week", "Неделя"), ("month", "Месяц"), ("all", "Все")]
        for key, label in filters:
            active = self.date_filter == key
            if active:
                btn = MDRaisedButton(
                    text=label, font_size="12sp",
                    md_bg_color=[0.20, 0.60, 0.95, 1],
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
            d_from = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            return d_from, today.strftime("%Y-%m-%d")
        elif self.date_filter == "month":
            d_from = today.replace(day=1).strftime("%Y-%m-%d")
            return d_from, today.strftime("%Y-%m-%d")
        return None, None

    # ── helpers ──────────────────────────────────────────────
    def _make_bar(self, color):
        from kivy.graphics import Color as GColor, RoundedRectangle as GRR
        bar = Widget(size_hint=(None, 1), width=dp(4))
        with bar.canvas:
            GColor(*color)
            bar._rect = GRR(pos=bar.pos, size=(dp(4), bar.height), radius=[dp(2)])
        bar.bind(pos=lambda w, p: setattr(w._rect, 'pos', (p[0], p[1] + dp(8))))
        bar.bind(size=lambda w, s: setattr(w._rect, 'size', (dp(4), s[1] - dp(16))))
        return bar

    def _make_card(self, bar_color, title, subtitle, name,
                   icon, icon_color, qty_text, amount_text, time_text,
                   on_tap=None):
        from kivymd.uix.label import MDIcon
        card = MDCard(
            orientation="horizontal",
            size_hint_y=None, height=dp(90),
            elevation=0, radius=[0],
            md_bg_color=[0.12, 0.12, 0.14, 1],
            ripple_behavior=True if on_tap else False,
        )
        if on_tap:
            card.bind(on_release=on_tap)
        card.add_widget(self._make_bar(bar_color))

        left = MDBoxLayout(orientation="vertical",
                           padding=[dp(12), dp(8)], spacing=dp(2),
                           size_hint_x=0.6)
        left.add_widget(MDLabel(text=title, font_style="H6", bold=True,
            theme_text_color="Custom", text_color=[1, 1, 1, 1], size_hint_y=0.35))
        left.add_widget(MDLabel(text=subtitle, font_style="Caption",
            theme_text_color="Custom", text_color=[0.6, 0.6, 0.6, 1], size_hint_y=0.3))
        left.add_widget(MDLabel(text=name, font_style="Body2",
            theme_text_color="Custom", text_color=[0.8, 0.8, 0.8, 1], size_hint_y=0.35))
        card.add_widget(left)

        right = MDBoxLayout(orientation="vertical",
                            padding=[dp(8)], spacing=dp(2),
                            size_hint_x=0.4)
        right.add_widget(MDIcon(icon=icon, halign="right", font_size="18sp",
            theme_text_color="Custom", text_color=icon_color, size_hint_y=0.25))
        right.add_widget(MDLabel(text=qty_text, halign="right",
            font_style="H6", bold=True,
            theme_text_color="Custom", text_color=[1, 1, 1, 1], size_hint_y=0.3))
        right.add_widget(MDLabel(text=amount_text, halign="right",
            font_style="Body2",
            theme_text_color="Custom", text_color=[0.8, 0.8, 0.8, 1], size_hint_y=0.25))
        right.add_widget(MDLabel(text=time_text, halign="right",
            font_style="Caption",
            theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1], size_hint_y=0.2))
        card.add_widget(right)
        return card

    # ── main loader ─────────────────────────────────────────
    def load_docs(self):
        box = self.ids.doc_list
        box.clear_widgets()

        today = dt_date.today().strftime("%Y-%m-%d")
        d_from, d_to = self._get_date_range()

        def in_range(date_str):
            if d_from is None:
                return True
            return d_from <= date_str <= d_to

        # 1. Подтверждённые расходные (expense)
        orders = db.get_orders_by_type("expense")
        orders = [o for o in orders if in_range(o["date"])]

        # 2. Открытые продажи (status='open') — это будущие расходные
        open_sales = db.get_open_sales(status="open")
        open_data = []
        for sale in open_sales:
            items = db.get_open_sale_items(sale["id"])
            if not items:
                continue
            d = (sale.get("created_at") or "")[:10] or today
            if not in_range(d):
                continue
            open_data.append({
                "sale": sale,
                "items": items,
                "date": d,
            })

        # 3. Строим события
        events = []
        # Группируем open_data по buyer_name + date для мерджа
        open_by_key = {}
        for od in open_data:
            buyer_name = (od["sale"].get("buyer_name") or "").strip().lower()
            key = (buyer_name, od["date"])
            open_by_key.setdefault(key, []).append(od)

        merged_keys = set()

        for o in orders:
            buyer_obj = db.get_buyer(o.get("buyer_id")) if o.get("buyer_id") else None
            buyer_name = buyer_obj["name"] if buyer_obj else "—"
            key = (buyer_name.strip().lower(), o["date"])

            extras = open_by_key.get(key, [])
            if extras:
                merged_keys.add(key)

            events.append({
                "type": "confirmed",
                "date": o["date"],
                "order": o,
                "buyer_name": buyer_name,
                "extras": extras,
            })

        # Несопоставленные открытые
        for key, od_list in open_by_key.items():
            if key not in merged_keys:
                first_sale = od_list[0]["sale"]
                all_items = []
                sale_ids = []
                for od in od_list:
                    all_items.extend(od["items"])
                    sale_ids.append(od["sale"]["id"])
                events.append({
                    "type": "open",
                    "date": key[1] or today,
                    "buyer_name": first_sale.get("buyer_name") or "—",
                    "buyer_id": first_sale.get("buyer_id"),
                    "items": all_items,
                    "sale_ids": sale_ids,
                })

        if not events:
            box.add_widget(MDLabel(
                text="Нет расходных документов",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(80),
            ))
            return

        events.sort(key=lambda e: e["date"], reverse=True)

        total_confirmed = 0
        total_open = 0

        by_date = {}
        for ev in events:
            by_date.setdefault(ev["date"], []).append(ev)

        for date_str in sorted(by_date.keys(), reverse=True):
            hdr = MDBoxLayout(
                size_hint_y=None, height=dp(36),
                md_bg_color=[0.15, 0.15, 0.17, 1],
                padding=[dp(16), 0],
            )
            hdr.add_widget(MDLabel(
                text=_fmt_date_header(date_str),
                font_style="Subtitle2", bold=True,
                theme_text_color="Custom", text_color=[0.9, 0.9, 0.9, 1],
                valign="center",
            ))
            box.add_widget(hdr)

            for ev in by_date[date_str]:
                if ev["type"] == "confirmed":
                    o = ev["order"]
                    doc_num = o.get("doc_number") or f"#{o['id']}"
                    items = db.get_order_items(o["id"])
                    qty = sum(it["quantity"] for it in items)
                    total = o.get("total_sale", o.get("total_purchase", 0))
                    total_confirmed += total

                    created = o.get("created_at", "")
                    time_str = created[:16].replace("T", " ") if created and len(created) > 10 else ""

                    box.add_widget(self._make_card(
                        bar_color=[0.20, 0.60, 0.95, 1],
                        title=doc_num,
                        subtitle=_fmt_date_short(o["date"]),
                        name=ev["buyer_name"],
                        icon="check-decagram",
                        icon_color=[0.3, 0.85, 0.5, 1],
                        qty_text=f"{qty} шт",
                        amount_text=_fmt_money(total),
                        time_text=time_str,
                        on_tap=lambda x, oid=o["id"]: self._open_doc(oid, "confirmed"),
                    ))

                    # Мердж: открытые позиции того же покупателя
                    extras = ev.get("extras", [])
                    if extras:
                        ext_items = []
                        ext_sale_ids = []
                        for od in extras:
                            ext_items.extend(od["items"])
                            ext_sale_ids.append(od["sale"]["id"])
                        ext_qty = sum(it["quantity"] for it in ext_items)
                        ext_amount = sum(it["purchase_price"] * it["quantity"] for it in ext_items)
                        total_open += ext_amount
                        box.add_widget(self._make_card(
                            bar_color=[0.85, 0.20, 0.20, 1],
                            title=f"+{ext_qty} шт (открытые)",
                            subtitle=ev["buyer_name"],
                            name="Ожидают подтверждения",
                            icon="timer-sand",
                            icon_color=[0.85, 0.20, 0.20, 1],
                            qty_text=f"+{ext_qty}",
                            amount_text=f"+{_fmt_money(ext_amount)}",
                            time_text="открытые",
                            on_tap=lambda x, sids=list(ext_sale_ids), its=list(ext_items):
                                self._open_doc(0, "open", sids, its),
                        ))
                        box.add_widget(self._make_action_row(
                            ext_sale_ids, ext_items, ev["date"],
                            ev.get("order", {}).get("buyer_id")))

                elif ev["type"] == "open":
                    items = ev["items"]
                    qty = sum(it["quantity"] for it in items)
                    amount = sum(it["purchase_price"] * it["quantity"] for it in items)
                    total_open += amount
                    sale_ids = ev["sale_ids"]

                    box.add_widget(self._make_card(
                        bar_color=[0.85, 0.20, 0.20, 1],
                        title=f"Открытая ({qty} шт)",
                        subtitle=_fmt_date_short(ev["date"]),
                        name=ev["buyer_name"],
                        icon="timer-sand",
                        icon_color=[0.85, 0.20, 0.20, 1],
                        qty_text=f"{qty} шт",
                        amount_text=_fmt_money(amount),
                        time_text="ожидание",
                        on_tap=lambda x, sids=list(sale_ids), its=list(items):
                            self._open_doc(0, "open", sids, its),
                    ))
                    box.add_widget(self._make_action_row(
                        sale_ids, items, ev["date"], ev.get("buyer_id")))

        # Итоговая карточка
        grand_total = total_confirmed + total_open
        summary = MDCard(
            orientation="vertical",
            padding=dp(16), spacing=dp(4),
            size_hint_y=None, height=dp(90),
            elevation=0, radius=[dp(12)],
            md_bg_color=[0.18, 0.18, 0.20, 1],
        )
        summary.add_widget(MDLabel(
            text=f"Итого: {_fmt_money(grand_total)}",
            font_style="H6", bold=True,
            theme_text_color="Custom", text_color=[1, 1, 1, 1],
        ))
        if total_open > 0:
            summary.add_widget(MDLabel(
                text=f"  Подтверждённые: {_fmt_money(total_confirmed)}",
                font_style="Body2",
                theme_text_color="Custom", text_color=[0.3, 0.85, 0.5, 1],
            ))
            summary.add_widget(MDLabel(
                text=f"  Открытые: +{_fmt_money(total_open)}",
                font_style="Body2",
                theme_text_color="Custom", text_color=[0.85, 0.20, 0.20, 1],
            ))
        box.add_widget(Widget(size_hint_y=None, height=dp(8)))
        box.add_widget(summary)
        box.add_widget(Widget(size_hint_y=None, height=dp(16)))

    def go_back(self):
        self.manager.current = "main_menu"

    def new_expense(self):
        """FAB → переход к созданию нового расходного документа."""
        scr = self.manager.get_screen("new_order")
        scr.preset_type = "expense"
        self.manager.current = "new_order"

    def _open_doc(self, order_id, mode, sale_ids=None, items=None):
        scr = self.manager.get_screen("doc_detail")
        scr.order_id = order_id
        scr.doc_mode = mode
        scr.return_screen = "expense"
        scr.open_sale_ids = sale_ids or []
        scr.open_items_data = items or []
        self.manager.current = "doc_detail"

    # ── action buttons ──────────────────────────────────────
    def _make_action_row(self, sale_ids, items, date_str, buyer_id=None):
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(44),
            padding=[dp(16), dp(4)], spacing=dp(12),
            md_bg_color=[0.14, 0.14, 0.16, 1],
        )
        btn_confirm = MDRaisedButton(
            text="Подтвердить",
            md_bg_color=[0.18, 0.74, 0.42, 1],
            text_color=[1, 1, 1, 1],
            font_size="13sp",
            size_hint_x=0.5,
            on_release=lambda x, sids=sale_ids, its=items, d=date_str, bid=buyer_id:
                self._confirm_open_sales(sids, its, d, bid),
        )
        btn_cancel = MDFlatButton(
            text="Отменить",
            theme_text_color="Custom",
            text_color=[0.85, 0.20, 0.20, 1],
            font_size="13sp",
            size_hint_x=0.5,
            on_release=lambda x, sids=sale_ids:
                self._cancel_open_sales(sids),
        )
        row.add_widget(btn_confirm)
        row.add_widget(btn_cancel)
        return row

    def _confirm_open_sales(self, sale_ids, items, date_str, buyer_id):
        """Подтвердить: создать expense order, закрыть open_sale."""
        order_items = []
        for it in items:
            order_items.append({
                "product_name": it["product_name"],
                "quantity": it["quantity"],
                "purchase_price": it["purchase_price"],
                "sale_price": it.get("sale_price", 0),
            })

        d = date_str if date_str else dt_date.today().strftime("%Y-%m-%d")
        db.create_order(
            date=d,
            supplier_id=None,
            buyer_id=buyer_id,
            items=order_items,
            doc_type="expense",
        )

        for sid in sale_ids:
            db.close_open_sale(sid)

        self.load_docs()

    def _cancel_open_sales(self, sale_ids):
        for sid in sale_ids:
            db.delete_open_sale(sid)
        self.load_docs()
