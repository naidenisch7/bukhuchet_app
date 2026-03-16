"""Экран приходных — тёмная тема, цветные полоски, группировка по датам."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from datetime import date as dt_date, timedelta
import db

Builder.load_string("""
#:import dp kivy.metrics.dp

<DocCard@MDCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(90)
    elevation: 0
    radius: [0]
    md_bg_color: 0.12, 0.12, 0.14, 1
    bar_color: 0.95, 0.55, 0.15, 1
    doc_num: ""
    doc_date: ""
    doc_name: ""
    doc_qty: ""
    doc_amount: ""
    doc_time: ""

    canvas.before:
        Color:
            rgba: 0.25, 0.25, 0.27, 1
        Line:
            points: [self.x, self.y, self.x + self.width, self.y]
            width: 0.5

    # Colored left bar
    Widget:
        size_hint: None, 1
        width: dp(4)
        canvas:
            Color:
                rgba: root.bar_color
            RoundedRectangle:
                pos: self.pos[0], self.pos[1] + dp(10)
                size: dp(4), self.height - dp(20)
                radius: [dp(2)]

    # Left info
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12), dp(8)
        spacing: dp(2)
        size_hint_x: 0.6

        MDLabel:
            text: root.doc_num
            font_style: "H6"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_y: 0.35

        MDLabel:
            text: root.doc_date
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1
            size_hint_y: 0.3

        MDLabel:
            text: root.doc_name
            font_style: "Body2"
            theme_text_color: "Custom"
            text_color: 0.8, 0.8, 0.8, 1
            size_hint_y: 0.35

    # Right info
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(8)
        spacing: dp(2)
        size_hint_x: 0.4

        MDIcon:
            icon: "check-decagram"
            halign: "right"
            font_size: "18sp"
            theme_text_color: "Custom"
            text_color: 0.3, 0.85, 0.5, 1
            size_hint_y: 0.2

        MDLabel:
            text: root.doc_qty
            halign: "right"
            font_style: "H6"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_y: 0.3

        MDLabel:
            text: root.doc_amount
            halign: "right"
            font_style: "Body2"
            theme_text_color: "Custom"
            text_color: 0.8, 0.8, 0.8, 1
            size_hint_y: 0.3

        MDLabel:
            text: root.doc_time
            halign: "right"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            size_hint_y: 0.2

<DateHeader>:
    size_hint_y: None
    height: dp(36)
    md_bg_color: 0.15, 0.15, 0.17, 1
    padding: dp(16), 0

    MDLabel:
        id: date_label
        text: ""
        font_style: "Subtitle2"
        bold: True
        theme_text_color: "Custom"
        text_color: 0.9, 0.9, 0.9, 1
        valign: "center"

<IncomeScreen>:
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
                    text_color: 0.3, 0.85, 0.5, 1
                    font_size: "13sp"
                    on_release: root.show_income()

                MDFlatButton:
                    text: "РАСХОДНЫЕ"
                    pos_hint: {"center_y": 0.5}
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.6, 0.6, 1
                    font_size: "13sp"
                    on_release: root.go_expense_tab()

            # Separator line under active tab
            MDBoxLayout:
                size_hint_y: None
                height: dp(2)
                md_bg_color: 0.3, 0.85, 0.5, 1

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
            md_bg_color: 0.18, 0.74, 0.42, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.new_income()
""")


class DateHeader(MDBoxLayout):
    pass


def _fmt_money(val):
    """Format like 1 384 700,00р."""
    s = f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}р."


def _fmt_date_header(date_str):
    """2026-03-16 → 16 мар. 2026 г."""
    months = {1: "янв.", 2: "фев.", 3: "мар.", 4: "апр.", 5: "мая",
              6: "июн.", 7: "июл.", 8: "авг.", 9: "сен.", 10: "окт.",
              11: "нояб.", 12: "дек."}
    try:
        d = dt_date.fromisoformat(date_str)
        return f"{d.day} {months[d.month]} {d.year} г."
    except Exception:
        return date_str


def _fmt_date_short(date_str):
    """2026-03-16 → 16.03.2026"""
    try:
        d = dt_date.fromisoformat(date_str)
        return d.strftime("%d.%m.%Y")
    except Exception:
        return date_str


class IncomeScreen(MDScreen):
    date_filter = StringProperty("today")

    def on_enter(self):
        self._build_filter_chips()
        self.load_docs()

    def show_income(self):
        self.load_docs()

    def go_expense_tab(self):
        self.manager.current = "expense"

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
                    md_bg_color=[0.18, 0.74, 0.42, 1],
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
        """Returns (date_from, date_to) strings or (None, None) for 'all'."""
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
        """Colored left bar widget."""
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

        # 1. Подтверждённые закупки (income)
        orders = db.get_orders_by_type("income")
        orders = [o for o in orders if in_range(o["date"])]

        # 2. Открытые продажи (status='open')
        open_items = db.get_all_open_sale_items()
        open_items = [it for it in open_items
                      if in_range((it.get("added_at") or "")[:10] or today)]

        # Группируем открытые по (supplier_name_lower, date)
        open_by_key = {}
        for it in open_items:
            sup = (it.get("supplier_name") or "").strip().lower()
            d = (it.get("added_at") or "")[:10] or today
            open_by_key.setdefault((sup, d), []).append(it)

        # 3. Строим события
        events = []
        merged_keys = set()

        for o in orders:
            sup_obj = db.get_supplier(o["supplier_id"]) if o.get("supplier_id") else None
            sup_name = sup_obj["name"] if sup_obj else "—"
            key = (sup_name.strip().lower(), o["date"])

            extras = open_by_key.get(key, [])
            if extras:
                merged_keys.add(key)

            events.append({
                "type": "confirmed",
                "date": o["date"],
                "order": o,
                "sup_name": sup_name,
                "extras": extras,
            })

        # Несопоставленные открытые продажи
        for key, items in open_by_key.items():
            if key not in merged_keys:
                events.append({
                    "type": "open",
                    "date": key[1] or today,
                    "sup_name": items[0].get("supplier_name") or "—",
                    "items": items,
                })

        if not events:
            box.add_widget(MDLabel(
                text="Нет приходных документов",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None, height=dp(80),
            ))
            return

        events.sort(key=lambda e: e["date"], reverse=True)

        # 4. Итоги
        total_confirmed = 0
        total_open = 0

        # 5. Рисуем
        by_date = {}
        for ev in events:
            by_date.setdefault(ev["date"], []).append(ev)

        for date_str in sorted(by_date.keys(), reverse=True):
            hdr = DateHeader()
            hdr.ids.date_label.text = _fmt_date_header(date_str)
            box.add_widget(hdr)

            for ev in by_date[date_str]:
                if ev["type"] == "confirmed":
                    o = ev["order"]
                    doc_num = o.get("doc_number") or f"#{o['id']}"
                    items = db.get_order_items(o["id"])
                    qty = sum(it["quantity"] for it in items)
                    amount = o["total_purchase"]
                    total_confirmed += amount

                    created = o.get("created_at", "")
                    time_str = created[:16].replace("T", " ") if created and len(created) > 10 else ""

                    # Подтверждённая карточка (оранжевая полоса, зелёная галка)
                    box.add_widget(self._make_card(
                        bar_color=[0.95, 0.55, 0.15, 1],
                        title=doc_num,
                        subtitle=_fmt_date_short(o["date"]),
                        name=ev["sup_name"],
                        icon="check-decagram",
                        icon_color=[0.3, 0.85, 0.5, 1],
                        qty_text=f"{qty} шт",
                        amount_text=_fmt_money(amount),
                        time_text=time_str,
                        on_tap=lambda x, oid=o["id"]: self._open_doc(oid, "confirmed"),
                    ))

                    # Если есть открытые позиции от того же поставщика
                    extras = ev.get("extras", [])
                    if extras:
                        ext_qty = sum(it["quantity"] for it in extras)
                        ext_amount = sum(it["purchase_price"] * it["quantity"] for it in extras)
                        total_open += ext_amount
                        sale_ids = list({it["sale_id"] for it in extras})
                        box.add_widget(self._make_card(
                            bar_color=[0.85, 0.20, 0.20, 1],
                            title=f"+{ext_qty} шт (открытые)",
                            subtitle=ev["sup_name"],
                            name="Ожидают подтверждения",
                            icon="timer-sand",
                            icon_color=[0.85, 0.20, 0.20, 1],
                            qty_text=f"+{ext_qty}",
                            amount_text=f"+{_fmt_money(ext_amount)}",
                            time_text="открытые",
                            on_tap=lambda x, sids=sale_ids, its=list(extras):
                                self._open_doc(0, "open", sids, its),
                        ))
                        box.add_widget(self._make_action_row(sale_ids, extras, ev["date"]))

                elif ev["type"] == "open":
                    items = ev["items"]
                    qty = sum(it["quantity"] for it in items)
                    amount = sum(it["purchase_price"] * it["quantity"] for it in items)
                    total_open += amount
                    sale_ids = list({it["sale_id"] for it in items})

                    box.add_widget(self._make_card(
                        bar_color=[0.85, 0.20, 0.20, 1],
                        title=f"Открытая ({qty} шт)",
                        subtitle=_fmt_date_short(ev["date"]),
                        name=ev["sup_name"],
                        icon="timer-sand",
                        icon_color=[0.85, 0.20, 0.20, 1],
                        qty_text=f"{qty} шт",
                        amount_text=_fmt_money(amount),
                        time_text="ожидание",
                        on_tap=lambda x, sids=sale_ids, its=list(items):
                            self._open_doc(0, "open", sids, its),
                    ))
                    box.add_widget(self._make_action_row(sale_ids, items, ev["date"]))

        # 6. Итоговая карточка
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

    def _open_doc(self, order_id, mode, sale_ids=None, items=None):
        """Navigate to doc detail screen."""
        scr = self.manager.get_screen("doc_detail")
        scr.order_id = order_id
        scr.doc_mode = mode
        scr.return_screen = "income"
        scr.open_sale_ids = sale_ids or []
        scr.open_items_data = items or []
        self.manager.current = "doc_detail"

    def new_income(self):
        """FAB → переход к созданию нового приходного документа."""
        scr = self.manager.get_screen("new_order")
        scr.preset_type = "income"
        self.manager.current = "new_order"

    def go_back(self):
        self.manager.current = "main_menu"
    def _make_action_row(self, sale_ids, items, date_str):
        """Row with Подтвердить / Отменить buttons for open sales."""
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
            on_release=lambda x, sids=sale_ids, its=items, d=date_str:
                self._confirm_open_sales(sids, its, d),
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

    def _confirm_open_sales(self, sale_ids, items, date_str):
        """Show payment method dialog before confirming."""
        buyer_id = items[0].get("buyer_id") if items else None
        buyer = db.get_buyer(buyer_id) if buyer_id else None

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(12),
            size_hint_y=None, height=dp(180), padding=[dp(8), dp(8)],
        )

        btn_card = MDRaisedButton(
            text="💳  Карта",
            md_bg_color=[0.20, 0.60, 0.95, 1],
            text_color=[1, 1, 1, 1],
            size_hint_x=1,
            on_release=lambda x: self._do_confirm(sale_ids, items, date_str, "card"),
        )
        btn_cash = MDRaisedButton(
            text="💵  Наличные",
            md_bg_color=[0.18, 0.74, 0.42, 1],
            text_color=[1, 1, 1, 1],
            size_hint_x=1,
            on_release=lambda x: self._do_confirm(sale_ids, items, date_str, "cash"),
        )
        content.add_widget(btn_card)
        content.add_widget(btn_cash)

        if buyer and buyer.get("deposit", 0) > 0:
            dep = buyer["deposit"]
            total = sum(it["purchase_price"] * it["quantity"] for it in items)
            if dep >= total:
                dep_text = f"💰  Депозит ({dep:.0f} → {dep - total:.0f})"
            else:
                shortfall = total - dep
                dep_text = f"💰  Депозит ({dep:.0f}) + доплата {shortfall:.0f}"
            btn_dep = MDRaisedButton(
                text=dep_text,
                md_bg_color=[0.95, 0.55, 0.15, 1],
                text_color=[1, 1, 1, 1],
                size_hint_x=1,
                on_release=lambda x: self._do_confirm(sale_ids, items, date_str, "deposit"),
            )
            content.add_widget(btn_dep)

        self._pay_dialog = MDDialog(
            title="Способ оплаты",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self._pay_dialog.dismiss()),
            ],
        )
        self._pay_dialog.open()

    def _do_confirm(self, sale_ids, items, date_str, pay_method):
        """Actually confirm: create order, handle payment, close open sales."""
        if hasattr(self, '_pay_dialog'):
            self._pay_dialog.dismiss()

        # Find supplier
        sup_name = (items[0].get("supplier_name") or "").strip()
        supplier_id = None
        if sup_name:
            for s in db.get_suppliers():
                if s["name"].strip().lower() == sup_name.lower():
                    supplier_id = s["id"]
                    break

        buyer_id = items[0].get("buyer_id")

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
            supplier_id=supplier_id,
            buyer_id=buyer_id,
            items=order_items,
            doc_type="income",
        )

        # Handle payment method → buyer balance
        if pay_method == "deposit" and buyer_id:
            buyer = db.get_buyer(buyer_id)
            if buyer:
                total = sum(it["purchase_price"] * it["quantity"] for it in items)
                deposit = buyer.get("deposit", 0)
                debt = buyer.get("debt", 0)
                new_deposit = deposit - total
                if new_deposit < 0:
                    new_debt = debt + abs(new_deposit)
                    new_deposit = 0
                else:
                    new_debt = debt
                db.update_buyer(buyer_id, deposit=new_deposit, debt=new_debt)

        # Close open sales
        for sid in sale_ids:
            db.close_open_sale(sid)

        self.load_docs()

    def _cancel_open_sales(self, sale_ids):
        """Отменить: удалить open_sale (items каскадно удалятся)."""
        for sid in sale_ids:
            db.delete_open_sale(sid)
        self.load_docs()
