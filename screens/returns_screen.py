from datetime import date as dt_date

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

import db

Builder.load_string("""
<ReturnsScreen>:
    md_bg_color: 0.12, 0.12, 0.14, 1

    MDFloatLayout:

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Возвраты"
                elevation: 0
                md_bg_color: 0.10, 0.10, 0.12, 1
                specific_text_color: 1, 1, 1, 1
                left_action_items: [["menu", lambda x: app.open_drawer()]]

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
                    padding: dp(8), dp(4)
                    spacing: dp(6)
                    id: returns_list

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: 0.85, 0.30, 0.30, 1
            text_color: 1, 1, 1, 1
            elevation: 6
            pos_hint: {"right": 0.93, "y": 0.03}
            on_release: root.add_return()
""")


def _fmt_money(val):
    try:
        v = float(val)
    except (TypeError, ValueError):
        v = 0.0
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}р."


class ReturnsScreen(MDScreen):
    status_filter = StringProperty("all")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None

    # ── lifecycle ──────────────────────────────────────────────
    def on_enter(self, *args):
        self._build_filter_chips()
        self.load_returns()

    def go_back(self):
        self.manager.current = "main_menu"

    # ── filter chips ──────────────────────────────────────────
    def set_filter(self, f):
        self.status_filter = f
        self._build_filter_chips()
        self.load_returns()

    def _build_filter_chips(self):
        row = self.ids.filter_row
        row.clear_widgets()
        chips = [("all", "Все"), ("open", "Открытые"), ("closed", "Закрытые")]
        for key, label in chips:
            if key == self.status_filter:
                btn = MDRaisedButton(
                    text=label,
                    md_bg_color=(0.85, 0.30, 0.30, 1),
                    text_color=(1, 1, 1, 1),
                    font_size="13sp",
                    size_hint_y=None,
                    height=dp(30),
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            else:
                btn = MDFlatButton(
                    text=label,
                    text_color=(0.6, 0.6, 0.6, 1),
                    font_size="13sp",
                    size_hint_y=None,
                    height=dp(30),
                    on_release=lambda x, k=key: self.set_filter(k),
                )
            row.add_widget(btn)

    # ── load & display ────────────────────────────────────────
    def load_returns(self):
        container = self.ids.returns_list
        container.clear_widgets()

        status = None if self.status_filter == "all" else self.status_filter
        returns = db.get_returns(status=status) or []

        if not returns:
            container.add_widget(
                MDLabel(
                    text="Нет возвратов",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=dp(60),
                )
            )
            return

        for ret in returns:
            container.add_widget(self._make_return_card(ret))

    # ── card ──────────────────────────────────────────────────
    def _make_return_card(self, ret):
        is_open = ret.get("status", "open") == "open"
        bar_color = (0.85, 0.30, 0.30, 1) if is_open else (0.45, 0.45, 0.45, 1)
        type_icon = "\U0001f504" if ret.get("return_type") == "refund" else "\U0001f501"
        status_text = "Открыт" if is_open else "Закрыт"
        amount = (ret.get("sale_price") or 0) * (ret.get("quantity") or 0)

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            md_bg_color=(0.18, 0.18, 0.20, 1),
            radius=[dp(10)],
            padding=0,
            ripple_behavior=True,
            on_release=lambda x, rid=ret["id"]: self._view_return(rid),
        )

        # left accent bar
        bar = MDBoxLayout(
            size_hint_x=None,
            width=dp(5),
            md_bg_color=bar_color,
            radius=[dp(10), 0, 0, dp(10)],
        )
        card.add_widget(bar)

        # main content
        content = MDBoxLayout(
            orientation="vertical",
            padding=(dp(10), dp(8)),
            spacing=dp(2),
        )

        top_row = MDBoxLayout(size_hint_y=None, height=dp(22))
        top_row.add_widget(
            MDLabel(
                text=ret.get("product_name", "—"),
                font_style="Body1",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                shorten=True,
                shorten_from="right",
            )
        )
        top_row.add_widget(
            MDLabel(
                text=_fmt_money(amount),
                font_style="Body1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.85, 0.30, 0.30, 1),
                halign="right",
                size_hint_x=None,
                width=dp(110),
            )
        )
        content.add_widget(top_row)

        mid_row = MDBoxLayout(size_hint_y=None, height=dp(18))
        mid_row.add_widget(
            MDLabel(
                text=f"{ret.get('date', '')}  |  Кол-во: {ret.get('quantity', 0)}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
            )
        )
        content.add_widget(mid_row)

        bot_row = MDBoxLayout(size_hint_y=None, height=dp(18))
        bot_row.add_widget(
            MDLabel(
                text=f"{type_icon}  {status_text}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.55, 0.55, 1),
            )
        )
        content.add_widget(bot_row)

        card.add_widget(content)
        return card

    # ── view detail dialog ────────────────────────────────────
    def _view_return(self, return_id):
        ret = db.get_return(return_id)
        if not ret:
            return

        is_open = ret.get("status", "open") == "open"

        buyer_name = "—"
        if ret.get("buyer_id"):
            buyer = db.get_buyer(ret["buyer_id"])
            if buyer:
                buyer_name = buyer.get("name", "—")

        supplier_name = "—"
        if ret.get("supplier_id"):
            sup = db.get_suppliers() or []
            for s in sup:
                if s["id"] == ret["supplier_id"]:
                    supplier_name = s.get("name", "—")
                    break

        type_label = "Возврат средств" if ret.get("return_type") == "refund" else "Обмен"
        status_label = "Открыт" if is_open else "Закрыт"
        amount = (ret.get("sale_price") or 0) * (ret.get("quantity") or 0)

        detail_text = (
            f"[b]Товар:[/b] {ret.get('product_name', '—')}\n"
            f"[b]Дата:[/b] {ret.get('date', '—')}\n"
            f"[b]Покупатель:[/b] {buyer_name}\n"
            f"[b]Поставщик:[/b] {supplier_name}\n"
            f"[b]Кол-во:[/b] {ret.get('quantity', 0)}\n"
            f"[b]Цена закупки:[/b] {_fmt_money(ret.get('purchase_price', 0))}\n"
            f"[b]Цена продажи:[/b] {_fmt_money(ret.get('sale_price', 0))}\n"
            f"[b]Сумма:[/b] {_fmt_money(amount)}\n"
            f"[b]Причина:[/b] {ret.get('reason', '—')}\n"
            f"[b]Тип:[/b] {type_label}\n"
            f"[b]Статус:[/b] {status_label}"
        )

        detail_label = MDLabel(
            text=detail_text,
            markup=True,
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
        )
        detail_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(detail_label)

        buttons = []
        if is_open:
            buttons.append(
                MDRaisedButton(
                    text="Закрыть",
                    md_bg_color=(0.85, 0.30, 0.30, 1),
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x, rid=return_id: self._close_return(rid),
                )
            )
        buttons.append(
            MDFlatButton(
                text="Удалить",
                text_color=(0.85, 0.30, 0.30, 1),
                on_release=lambda x, rid=return_id: self._delete_return(rid),
            )
        )
        buttons.append(
            MDFlatButton(
                text="Отмена",
                text_color=(0.6, 0.6, 0.6, 1),
                on_release=lambda x: self._dismiss_dialog(),
            )
        )

        self._dismiss_dialog()
        self._dialog = MDDialog(
            title="Возврат",
            type="custom",
            content_cls=box,
            buttons=buttons,
        )
        self._dialog.md_bg_color = (0.18, 0.18, 0.20, 1)
        self._dialog.open()

    # ── close return ──────────────────────────────────────────
    def _close_return(self, return_id):
        ret = db.get_return(return_id)
        if ret and ret.get("return_type") == "refund" and ret.get("buyer_id"):
            buyer = db.get_buyer(ret["buyer_id"])
            if buyer:
                refund_amount = (ret.get("sale_price") or 0) * (ret.get("quantity") or 0)
                new_deposit = (buyer.get("deposit") or 0) + refund_amount
                db.update_buyer(ret["buyer_id"], deposit=new_deposit)

        db.close_return(return_id)
        self._dismiss_dialog()
        self.load_returns()

    # ── delete return ─────────────────────────────────────────
    def _delete_return(self, return_id):
        db.delete_return(return_id)
        self._dismiss_dialog()
        self.load_returns()

    # ── add return (two-step dialog) ──────────────────────────
    def add_return(self):
        buyers = db.get_buyers() or []
        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))

        box.add_widget(
            MDLabel(
                text="Выберите покупателя:",
                theme_text_color="Custom",
                text_color=(0.9, 0.9, 0.9, 1),
                size_hint_y=None,
                height=dp(30),
            )
        )

        # "no buyer" button
        box.add_widget(
            MDFlatButton(
                text="Без покупателя",
                text_color=(0.6, 0.6, 0.6, 1),
                size_hint_x=1,
                on_release=lambda x: self._show_return_form(buyer_id=None),
            )
        )

        for b in buyers:
            box.add_widget(
                MDRaisedButton(
                    text=b.get("name", f"ID {b['id']}"),
                    md_bg_color=(0.25, 0.25, 0.28, 1),
                    text_color=(1, 1, 1, 1),
                    size_hint_x=1,
                    on_release=lambda x, bid=b["id"]: self._show_return_form(buyer_id=bid),
                )
            )

        self._dismiss_dialog()
        self._dialog = MDDialog(
            title="Покупатель",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self._dismiss_dialog(),
                )
            ],
        )
        self._dialog.md_bg_color = (0.18, 0.18, 0.20, 1)
        self._dialog.open()

    def _show_return_form(self, buyer_id):
        self._dismiss_dialog()
        self._selected_buyer_id = buyer_id

        field_color = (0.9, 0.9, 0.9, 1)
        hint_color = (0.5, 0.5, 0.5, 1)

        self._field_product = MDTextField(
            hint_text="Наименование товара",
            mode="fill",
            fill_color_normal=(0.22, 0.22, 0.24, 1),
            text_color_normal=field_color,
            hint_text_color_normal=hint_color,
            size_hint_y=None,
            height=dp(48),
        )
        self._field_qty = MDTextField(
            hint_text="Количество",
            mode="fill",
            fill_color_normal=(0.22, 0.22, 0.24, 1),
            text_color_normal=field_color,
            hint_text_color_normal=hint_color,
            input_filter="int",
            text="1",
            size_hint_y=None,
            height=dp(48),
        )
        self._field_purchase = MDTextField(
            hint_text="Цена закупки",
            mode="fill",
            fill_color_normal=(0.22, 0.22, 0.24, 1),
            text_color_normal=field_color,
            hint_text_color_normal=hint_color,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
        )
        self._field_sale = MDTextField(
            hint_text="Цена продажи",
            mode="fill",
            fill_color_normal=(0.22, 0.22, 0.24, 1),
            text_color_normal=field_color,
            hint_text_color_normal=hint_color,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
        )
        self._field_reason = MDTextField(
            hint_text="Причина возврата",
            mode="fill",
            fill_color_normal=(0.22, 0.22, 0.24, 1),
            text_color_normal=field_color,
            hint_text_color_normal=hint_color,
            size_hint_y=None,
            height=dp(48),
        )

        # type selector row
        type_row = MDBoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
            padding=(0, dp(4)),
        )
        type_row.add_widget(
            MDRaisedButton(
                text="Возврат средств",
                md_bg_color=(0.85, 0.30, 0.30, 1),
                text_color=(1, 1, 1, 1),
                size_hint_x=0.5,
                on_release=lambda x: self._submit_return("refund"),
            )
        )
        type_row.add_widget(
            MDRaisedButton(
                text="Обмен",
                md_bg_color=(0.30, 0.30, 0.35, 1),
                text_color=(1, 1, 1, 1),
                size_hint_x=0.5,
                on_release=lambda x: self._submit_return("exchange"),
            )
        )

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=(dp(16), dp(8)),
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))
        for w in [
            self._field_product,
            self._field_qty,
            self._field_purchase,
            self._field_sale,
            self._field_reason,
            type_row,
        ]:
            box.add_widget(w)

        self._dialog = MDDialog(
            title="Новый возврат",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self._dismiss_dialog(),
                )
            ],
        )
        self._dialog.md_bg_color = (0.18, 0.18, 0.20, 1)
        self._dialog.open()

    def _submit_return(self, return_type):
        product = self._field_product.text.strip()
        if not product:
            return

        try:
            qty = int(self._field_qty.text.strip() or "1")
        except ValueError:
            qty = 1
        try:
            purchase_price = float(self._field_purchase.text.strip() or "0")
        except ValueError:
            purchase_price = 0.0
        try:
            sale_price = float(self._field_sale.text.strip() or "0")
        except ValueError:
            sale_price = 0.0

        reason = self._field_reason.text.strip()
        today = dt_date.today().isoformat()

        db.add_return(
            date=today,
            buyer_id=self._selected_buyer_id,
            supplier_id=None,
            order_id=None,
            product_name=product,
            quantity=qty,
            purchase_price=purchase_price,
            sale_price=sale_price,
            reason=reason,
            return_type=return_type,
        )

        self._dismiss_dialog()
        self.load_returns()

    # ── helpers ────────────────────────────────────────────────
    def _dismiss_dialog(self):
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None
