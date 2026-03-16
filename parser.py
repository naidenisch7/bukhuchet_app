"""
Умный парсер товарных строк для бота Бухучет.

Распознаёт ЛЮБОЙ формат записи товара:
- Название на одной/двух строках
- Цены с пробелами, точками, запятыми: 54.400, 57 300, 31,000
- Пара цен: ЗАКУПКА(ПРОДАЖА) с любыми пробелами
- Количество: -1-, 1-, -1шт-, • N шт, N шт, 1шт, или нет (=1)
- Ведущие 1., 3. = номер строки, НЕ количество
- Менеджер N = деление прибыли
- Поставщик (покупатель) = заголовок
"""
import re
from dataclasses import dataclass, field


@dataclass
class ParsedItem:
    """Одна распознанная товарная позиция."""
    product_name: str
    quantity: int = 1
    purchase_price: int = 0
    sale_price: int = 0

    @property
    def purchase_total(self) -> int:
        return self.purchase_price * self.quantity

    @property
    def sale_total(self) -> int:
        return self.sale_price * self.quantity

    @property
    def profit(self) -> int:
        return self.sale_total - self.purchase_total


@dataclass
class ParsedOrder:
    """Результат парсинга целого сообщения."""
    supplier: str = ""
    buyer: str = ""
    manager_count: int = 1
    items: list = field(default_factory=list)  # list[ParsedItem]

    @property
    def total_quantity(self) -> int:
        return sum(it.quantity for it in self.items)

    @property
    def total_purchase(self) -> int:
        return sum(it.purchase_total for it in self.items)

    @property
    def total_sale(self) -> int:
        return sum(it.sale_total for it in self.items)

    @property
    def total_profit(self) -> int:
        return self.total_sale - self.total_purchase

    @property
    def profit_per_manager(self) -> float:
        if self.manager_count <= 1:
            return float(self.total_profit)
        return self.total_profit / self.manager_count


def _normalize_price(s: str) -> int:
    """
    Нормализует строку цены в целое число.
    Убирает пробелы, точки, запятые, ₽, руб и т.д.
    '54.400' → 54400, '57 300' → 57300, '31,000' → 31000, '46. 000' → 46000
    '10.000' → 10000
    """
    s = s.strip()
    # Убираем ₽, руб, р
    s = re.sub(r'[₽рР]|руб\.?', '', s, flags=re.IGNORECASE).strip()
    # Убираем все пробелы внутри числа
    s = s.replace(' ', '')
    # Обработка точек и запятых:
    # Если после точки/запятой ровно 3 цифры (и нет других цифр после) — это разделитель тысяч
    # Например: 10.000 → 10000, 31,000 → 31000, 46.000 → 46000
    # Но 10.50 → оставляем как есть (маловероятно для товаров)
    # Для наших целей: убираем все точки и запятые (цены всегда целые рубли)
    s = s.replace('.', '').replace(',', '')
    # Убираем всё кроме цифр
    s = re.sub(r'[^\d]', '', s)
    if not s:
        return 0
    return int(s)


# Паттерн для пары цен: ЗАКУПКА(ПРОДАЖА) или ЗАКУПКА (ПРОДАЖА)
# Цены: 62700, 54.400, 57 300, 31,000, 46. 000
# Пробел/точка/запятая в числе — только перед группой ровно из 3 цифр (разделитель тысяч)
_PRICE_NUM = r'\d{1,3}(?:[.,\s]\s*\d{3})+|\d{4,}|\d{1,3}'
_PRICE_PAIR_RE = re.compile(
    r'(-?\s*)'                        # возможный дефис перед ценой
    r'(' + _PRICE_NUM + r')'          # закупочная цена (group 2)
    r'\s*'
    r'\(\s*'                          # открывающая скобка
    r'(' + _PRICE_NUM + r')'          # продажная цена (group 3)
    r'\s*\)'                          # закрывающая скобка
)

# Количество в разных форматах ПОСЛЕ пары цен:
# -1-, 1-, -1шт-, -1 шт-, 1шт, 1 шт
_QTY_AFTER_RE = re.compile(
    r'[\s\-]*(\d+)\s*(?:шт\.?)?[\s\-]*$'
)

# Количество ПЕРЕД ценой:
# • 1 шт, • 2 шт, 1 шт, 2шт, 1шт
_QTY_BEFORE_RE = re.compile(
    r'(?:•\s*)?(\d+)\s*шт\.?\s*'
)

# Количество в самом начале строки: "1шт", "1 шт" (если строка начинается с числа+шт)
_QTY_START_RE = re.compile(
    r'^(\d+)\s*шт\.?\s+'
)

# Номер строки в начале: "1.", "3.", "12."
_LINE_NUM_RE = re.compile(r'^\d+\.\s*')

# Менеджер: "менеджер 2", "менеджеры 3", "менеджера 2"
_MANAGER_RE = re.compile(
    r'менеджер[аыов]*\s*(\d+)',
    re.IGNORECASE
)

# Заголовок: поставщик (покупатель) или просто имя (имя)
_HEADER_RE = re.compile(
    r'^(.+?)\s*\(\s*(.+?)\s*\)\s*$'
)

# Строка с одной ценой через em-dash или валютный символ: "17 256GB Blue — 62300-2-" или "SM-S948B/DS€ 86300"
_EMDASH_LINE_RE = re.compile(
    r'^(.+?)\s*[—–€$£]\s*'           # название + em-dash / currency (group 1)
    r'(\d[\d\s.,]*\d|\d+)'           # цена (group 2)
    r'[\s.]*'                          # опц. точки/пробелы
    r'(?:[-–—]\s*(\d+)\s*(?:шт\.?)?\s*[-–—]*)?'  # опц. -кол-во[шт]- (group 3)
    r'\s*$'
)

# Строка одна цена через дефис: "граве-300-1-"
_DASH_SINGLE_RE = re.compile(
    r'^(.+?)'                          # название (group 1)
    r'\s*-\s*'                         # дефис
    r'(\d[\d\s.,]*\d|\d{3,})'         # цена >= 3 цифр (group 2)
    r'\s*-\s*'                         # дефис
    r'(\d+)'                           # количество (group 3)
    r'\s*(?:шт\.?)?\s*-?\s*$'          # опц. шт и -
)

# Строка-число (цена на отдельной строке): "150000"
_STANDALONE_NUM_RE = re.compile(
    r'^\s*(\d[\d\s.,]*\d|\d{4,})\s*$'
)

# Строка с ценой в конце через пробел: "Samsung Galaxy S26 86300" или "Samsung Galaxy S26 86300-1-"
_TRAILING_PRICE_RE = re.compile(
    r'^(.+?)\s+'                       # название (group 1)
    r'(\d{4,}(?:[.,\s]\d{3})*)'       # цена >= 4 цифр (group 2)
    r'[\s.]*'                           # опц. точки/пробелы
    r'(?:[-–—]\s*(\d+)\s*(?:шт\.?)?\s*[-–—]*)?'  # опц. -кол-во[шт]- (group 3)
    r'\s*$'
)


def _try_parse_single_price(line: str):
    """Пытается распознать строку с одной ценой (без пары).
    Returns (name, price, qty) or None."""
    # Пропускаем строки с обычными скобками (мб заголовок или спецификация)
    # но только если скобки содержат не-числовой текст
    
    # 1) em-dash: "name — price -qty-"
    m = _EMDASH_LINE_RE.match(line)
    if m:
        name = _clean_product_name(m.group(1))
        price = _normalize_price(m.group(2))
        qty = int(m.group(3)) if m.group(3) else 1
        if name and price > 0:
            return (name, price, qty)

    # 2) дефис-дефис: "name-price-qty-"
    if '—' not in line and '–' not in line and '€' not in line:
        m = _DASH_SINGLE_RE.match(line)
        if m:
            name = _clean_product_name(m.group(1))
            price = _normalize_price(m.group(2))
            qty = int(m.group(3))
            if name and price > 0:
                return (name, price, qty)

    # 3) Цена в конце строки через пробел: "Samsung Galaxy S26 86300" или "Name 86300-1-"
    m = _TRAILING_PRICE_RE.match(line)
    if m:
        name = _clean_product_name(m.group(1))
        price = _normalize_price(m.group(2))
        qty = int(m.group(3)) if m.group(3) else 1
        if name and price >= 1000:
            return (name, price, qty)

    return None


def _is_price_line(line: str) -> bool:
    """Проверяет, содержит ли строка пару цен."""
    return bool(_PRICE_PAIR_RE.search(line))


def _extract_quantity_after(text_after_price: str) -> int:
    """Извлекает количество из текста ПОСЛЕ пары цен."""
    text = text_after_price.strip()
    if not text:
        return 1
    m = _QTY_AFTER_RE.search(text)
    if m:
        return int(m.group(1))
    return 1


def _extract_quantity_before(text_before_price: str) -> int | None:
    """Извлекает количество из текста ПЕРЕД ценой (• N шт, N шт)."""
    m = _QTY_BEFORE_RE.search(text_before_price)
    if m:
        return int(m.group(1))
    m = _QTY_START_RE.match(text_before_price.strip())
    if m:
        return int(m.group(1))
    return None


def _clean_product_name(name: str) -> str:
    """Убирает номер строки, лишние тире, пробелы из названия."""
    name = name.strip()
    # Убираем ведущий номер строки: "1.", "3."
    name = _LINE_NUM_RE.sub('', name)
    # Убираем ведущие/завершающие тире и пробелы
    name = name.strip(' -–—•·')
    # Убираем количество в начале: "1шт", "1 шт"
    name = re.sub(r'^\d+\s*шт\.?\s*', '', name, flags=re.IGNORECASE)
    # Убираем флаги-эмодзи в конце для чистоты (оставляем — они часть названия)
    # Нет, пользователь хочет полное название — оставляем
    return name.strip(' -–—•·')


def parse_product_lines(text: str) -> list[ParsedItem]:
    """
    Парсит текст с товарами и возвращает список ParsedItem.

    Поддерживает форматы:
    1) Пара цен: название ЗАКУПКА(ПРОДАЖА) кол-во
    2) Одна цена: название — цена -кол-во- (em-dash)
    3) Одна цена: название-цена-кол-во- (дефис)
    4) Название на одной строке, цена на следующей
    """
    lines = text.strip().split('\n')
    items = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Пропускаем строки-заголовки (поставщик/покупатель, менеджер)
        if _MANAGER_RE.search(line) and not _PRICE_PAIR_RE.search(line):
            i += 1
            continue

        # Пропускаем если это чистый заголовок поставщик(покупатель) без цены
        if _HEADER_RE.match(line) and not _PRICE_PAIR_RE.search(line):
            i += 1
            continue

        # === 1) Ищем пару цен в текущей строке ===
        price_match = _PRICE_PAIR_RE.search(line)

        if price_match:
            before_price = line[:price_match.start()]
            after_price = line[price_match.end():]
            purchase = _normalize_price(price_match.group(2))
            sale = _normalize_price(price_match.group(3))

            qty_before = _extract_quantity_before(before_price)
            qty_after = _extract_quantity_after(after_price)

            if qty_before is not None:
                qty = qty_before
                before_clean = _QTY_BEFORE_RE.sub('', before_price)
                if not before_clean.strip():
                    before_clean = _QTY_START_RE.sub('', before_price)
            else:
                qty = qty_after
                before_clean = before_price

            product_name = _clean_product_name(before_clean)

            if not product_name and i > 0:
                prev = lines[i - 1].strip()
                if prev and not _is_price_line(prev):
                    product_name = _clean_product_name(prev)

            if purchase > 0 and sale > 0 and product_name:
                items.append(ParsedItem(
                    product_name=product_name,
                    quantity=qty,
                    purchase_price=purchase,
                    sale_price=sale,
                ))
            i += 1
            continue

        # === 2) Одна цена в текущей строке (em-dash / дефис) ===
        single = _try_parse_single_price(line)
        if single:
            name, price, qty = single
            items.append(ParsedItem(
                product_name=name,
                quantity=qty,
                purchase_price=price,
                sale_price=price,
            ))
            i += 1
            continue

        # === 3) Текущая строка — название, следующая — цена ===
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            # 3a) Следующая строка — пара цен
            next_price_match = _PRICE_PAIR_RE.search(next_line)
            if next_price_match:
                before_price = next_line[:next_price_match.start()]
                after_price = next_line[next_price_match.end():]
                purchase = _normalize_price(next_price_match.group(2))
                sale = _normalize_price(next_price_match.group(3))

                qty_before = _extract_quantity_before(before_price)
                qty_after = _extract_quantity_after(after_price)

                if qty_before is not None:
                    qty = qty_before
                else:
                    qty = qty_after

                product_name = _clean_product_name(line)

                if purchase > 0 and sale > 0 and product_name:
                    items.append(ParsedItem(
                        product_name=product_name,
                        quantity=qty,
                        purchase_price=purchase,
                        sale_price=sale,
                    ))
                i += 2
                continue

            # 3b) Следующая строка — одиночное число (цена)
            standalone_m = _STANDALONE_NUM_RE.match(next_line)
            if standalone_m:
                price = _normalize_price(standalone_m.group(1))
                product_name = _clean_product_name(line)
                if product_name and price > 0:
                    items.append(ParsedItem(
                        product_name=product_name,
                        quantity=1,
                        purchase_price=price,
                        sale_price=price,
                    ))
                    i += 2
                    continue

        i += 1

    return items


def parse_header(text: str) -> tuple[str, str, int]:
    """
    Извлекает из текста поставщика, покупателя и кол-во менеджеров.
    Возвращает: (supplier, buyer, manager_count)
    """
    supplier = ""
    buyer = ""
    manager_count = 1

    lines = text.strip().split('\n')
    for line in lines[:10]:  # смотрим первые 10 строк
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Менеджер
        m_mgr = _MANAGER_RE.search(line_stripped)
        if m_mgr and not _PRICE_PAIR_RE.search(line_stripped):
            manager_count = int(m_mgr.group(1))
            # Если есть текст до "менеджер" — это может быть заголовок
            before_mgr = line_stripped[:m_mgr.start()].strip()
            if before_mgr:
                hm = _HEADER_RE.match(before_mgr)
                if hm:
                    supplier = hm.group(1).strip()
                    buyer = hm.group(2).strip()
            continue

        # Заголовок поставщик(покупатель) — без цены
        if not _PRICE_PAIR_RE.search(line_stripped):
            hm = _HEADER_RE.match(line_stripped)
            if hm and not supplier and not buyer:
                supplier = hm.group(1).strip()
                buyer = hm.group(2).strip()
                continue

    return supplier, buyer, manager_count


def parse_full_message(text: str) -> ParsedOrder:
    """
    Полный парсинг: заголовок + товары.
    Возвращает ParsedOrder с поставщиком, покупателем, менеджерами, товарами.
    """
    supplier, buyer, manager_count = parse_header(text)
    items = parse_product_lines(text)
    return ParsedOrder(
        supplier=supplier,
        buyer=buyer,
        manager_count=manager_count,
        items=items,
    )


def format_order_report(order: ParsedOrder, date: str = "",
                        supplier_deposit: float = 0, supplier_debt: float = 0,
                        buyer_deposit: float = 0, buyer_debt: float = 0) -> str:
    """Форматирует красивый отчёт о заказе."""
    lines = ["✅ Заказ создан!"]
    if date:
        lines.append(f"📅 Дата: {date}")

    lines.append(f"📦 Поставщик: {order.supplier or '—'}")
    lines.append(f"🛒 Покупатель: {order.buyer or '—'}")

    if order.manager_count > 1:
        lines.append(f"👥 Менеджеров: {order.manager_count}")

    lines.append("")
    lines.append("📊 Товары:")

    for idx, item in enumerate(order.items, 1):
        lines.append(
            f"{idx}. ✅ {item.product_name} - {item.quantity} шт "
            f"| {item.purchase_price}→{item.sale_price} руб"
        )

    lines.append("")
    lines.append(f"   Итого: {order.total_quantity} шт |")
    lines.append(f"   ✅ Закупка: {order.total_purchase} руб |")
    lines.append(f"   ➡️ Продажа: {order.total_sale} руб |")
    lines.append(f"   💰 Прибыль: {order.total_profit} руб")

    if order.manager_count > 1:
        lines.append("")
        lines.append("💰 Прибыль для менеджеров:")
        lines.append(
            f"   Прибыль на менеджера ({order.manager_count} чел.): "
            f"{order.profit_per_manager:.2f} руб"
        )

    # Информация о депозите/долге (справочно)
    info_lines = []
    if supplier_deposit > 0:
        info_lines.append(f"   📥 Депозит поставщика: {supplier_deposit:.0f} руб")
    if supplier_debt > 0:
        info_lines.append(f"   📤 Долг поставщику: {supplier_debt:.0f} руб")
    if buyer_deposit > 0:
        info_lines.append(f"   📥 Депозит покупателя: {buyer_deposit:.0f} руб")
    if buyer_debt > 0:
        info_lines.append(f"   📤 Долг покупателя: {buyer_debt:.0f} руб")

    if info_lines:
        lines.append("")
        lines.append("💳 Баланс:")
        lines.extend(info_lines)
    lines.append(f"\n💵 Итого к оплате: {order.total_sale:.0f} руб")

    return "\n".join(lines)
