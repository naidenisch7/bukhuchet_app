"""
Модуль базы данных для приложения Бухучет (Android/Desktop).
SQLite: поставщики, покупатели, наценки, заказы, открытые продажи.
"""
import sqlite3
import os
import sys


def _get_db_path() -> str:
    """Определяет путь к БД в зависимости от платформы."""
    try:
        from android.storage import app_storage_path  # type: ignore
        return os.path.join(app_storage_path(), "bukhuchet.db")
    except ImportError:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "bukhuchet.db")


DB_PATH = _get_db_path()
USER_ID = 1  # Мобильное приложение — один пользователь


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Создаёт все таблицы."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            deposit REAL DEFAULT 0,
            debt REAL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            deposit REAL DEFAULT 0,
            debt REAL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS markup_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            markup_amount REAL DEFAULT 0,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            doc_type TEXT NOT NULL DEFAULT 'income',
            doc_number TEXT,
            date TEXT NOT NULL,
            supplier_id INTEGER,
            buyer_id INTEGER,
            manager_count INTEGER DEFAULT 1,
            total_purchase REAL DEFAULT 0,
            total_sale REAL DEFAULT 0,
            profit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchase_price REAL DEFAULT 0,
            sale_price REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS doc_counters (
            user_id INTEGER NOT NULL,
            doc_type TEXT NOT NULL,
            next_num INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, doc_type)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS open_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            buyer_id INTEGER,
            buyer_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS open_sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            supplier_name TEXT DEFAULT '',
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchase_price REAL DEFAULT 0,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES open_sales(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT '',
            amount REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS deposit_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            buyer_id INTEGER NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            date TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            date TEXT NOT NULL,
            buyer_id INTEGER,
            supplier_id INTEGER,
            order_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchase_price REAL DEFAULT 0,
            sale_price REAL DEFAULT 0,
            reason TEXT DEFAULT '',
            return_type TEXT DEFAULT 'refund',
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE SET NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS warranty_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            buyer_id INTEGER,
            device_name TEXT NOT NULL,
            imei TEXT DEFAULT '',
            problem TEXT DEFAULT '',
            cost REAL DEFAULT 0,
            status TEXT DEFAULT 'received',
            received_date TEXT NOT NULL,
            completed_date TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS open_sale_withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES open_sales(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ──── Поставщики ────

def add_supplier(name, user_id=USER_ID):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO suppliers (user_id, name) VALUES (?, ?)", (user_id, name))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_suppliers(user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM suppliers WHERE user_id=? ORDER BY name", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_supplier(supplier_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_supplier(supplier_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        conn.execute(f"UPDATE suppliers SET {k}=? WHERE id=?", (v, supplier_id))
    conn.commit()
    conn.close()


def delete_supplier(supplier_id):
    conn = get_conn()
    conn.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()


def find_supplier_by_name(name, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM suppliers WHERE user_id=? AND LOWER(TRIM(name))=LOWER(TRIM(?))",
        (user_id, name)
    ).fetchall()
    conn.close()
    if rows:
        return dict(rows[0])
    return None


# ──── Покупатели ────

def add_buyer(name, user_id=USER_ID):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO buyers (user_id, name) VALUES (?, ?)", (user_id, name))
    bid = c.lastrowid
    conn.commit()
    conn.close()
    ensure_default_markups(bid)
    return bid


def get_buyers(user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM buyers WHERE user_id=? ORDER BY name", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_buyer(buyer_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM buyers WHERE id=?", (buyer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_buyer(buyer_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        conn.execute(f"UPDATE buyers SET {k}=? WHERE id=?", (v, buyer_id))
    conn.commit()
    conn.close()


def delete_buyer(buyer_id):
    conn = get_conn()
    conn.execute("DELETE FROM buyers WHERE id=?", (buyer_id,))
    conn.commit()
    conn.close()


def find_buyer_by_name(name, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM buyers WHERE user_id=? AND LOWER(TRIM(name))=LOWER(TRIM(?))",
        (user_id, name)
    ).fetchall()
    conn.close()
    if rows:
        return dict(rows[0])
    return None


# ──── Наценки ────

DEFAULT_CATEGORIES = ["Аксессуары", "Телефоны", "Apple Watch", "Макбук"]


def get_markups(buyer_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM markup_categories WHERE buyer_id=? ORDER BY id", (buyer_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_markup(buyer_id, category_name, markup_amount):
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM markup_categories WHERE buyer_id=? AND category_name=?",
        (buyer_id, category_name)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE markup_categories SET markup_amount=? WHERE id=?",
            (markup_amount, row["id"])
        )
    else:
        conn.execute(
            "INSERT INTO markup_categories (buyer_id, category_name, markup_amount) VALUES (?,?,?)",
            (buyer_id, category_name, markup_amount)
        )
    conn.commit()
    conn.close()


def ensure_default_markups(buyer_id):
    conn = get_conn()
    existing = conn.execute(
        "SELECT category_name FROM markup_categories WHERE buyer_id=?", (buyer_id,)
    ).fetchall()
    existing_names = {r["category_name"] for r in existing}
    for cat in DEFAULT_CATEGORIES:
        if cat not in existing_names:
            conn.execute(
                "INSERT INTO markup_categories (buyer_id, category_name, markup_amount) VALUES (?,?,0)",
                (buyer_id, cat)
            )
    conn.commit()
    conn.close()


def get_markup_for_category(buyer_id, category_name):
    conn = get_conn()
    row = conn.execute(
        "SELECT markup_amount FROM markup_categories WHERE buyer_id=? AND category_name=?",
        (buyer_id, category_name)
    ).fetchone()
    conn.close()
    return row["markup_amount"] if row else 0


# ──── Заказы ────

def _next_doc_number(conn, user_id, doc_type):
    row = conn.execute(
        "SELECT next_num FROM doc_counters WHERE user_id=? AND doc_type=?",
        (user_id, doc_type)
    ).fetchone()
    if row:
        num = row["next_num"]
        conn.execute(
            "UPDATE doc_counters SET next_num=? WHERE user_id=? AND doc_type=?",
            (num + 1, user_id, doc_type)
        )
    else:
        num = 1
        conn.execute(
            "INSERT INTO doc_counters (user_id, doc_type, next_num) VALUES (?,?,2)",
            (user_id, doc_type)
        )
    prefix = "ПР" if doc_type == "income" else "РС"
    return f"{prefix}-{num:04d}"


def create_order(date, supplier_id, buyer_id, items,
                 manager_count=1, doc_type="income", user_id=USER_ID):
    conn = get_conn()
    doc_number = _next_doc_number(conn, user_id, doc_type)
    total_purchase = sum(it["purchase_price"] * it["quantity"] for it in items)
    total_sale = sum(it["sale_price"] * it["quantity"] for it in items)
    profit = total_sale - total_purchase

    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (user_id, doc_type, doc_number, date, supplier_id, buyer_id,
                           manager_count, total_purchase, total_sale, profit)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (user_id, doc_type, doc_number, date, supplier_id, buyer_id,
          manager_count, total_purchase, total_sale, profit))
    order_id = c.lastrowid

    for it in items:
        c.execute("""
            INSERT INTO order_items (order_id, product_name, quantity, purchase_price, sale_price)
            VALUES (?,?,?,?,?)
        """, (order_id, it["product_name"], it["quantity"],
              it["purchase_price"], it["sale_price"]))

    conn.commit()
    conn.close()
    return order_id, doc_number


def get_orders(date=None, user_id=USER_ID):
    conn = get_conn()
    if date:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id=? AND date=? ORDER BY id DESC",
            (user_id, date)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY date DESC, id DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orders_by_type(doc_type, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? AND doc_type=? ORDER BY date DESC, id DESC",
        (user_id, doc_type)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orders_by_supplier(supplier_id, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? AND supplier_id=? ORDER BY date DESC, id DESC",
        (user_id, supplier_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orders_by_buyer(buyer_id, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? AND buyer_id=? ORDER BY date DESC, id DESC",
        (user_id, buyer_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order(order_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_order_items(order_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM order_items WHERE order_id=? ORDER BY id", (order_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_order(order_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        conn.execute(f"UPDATE orders SET {k}=? WHERE id=?", (v, order_id))
    conn.commit()
    conn.close()


def recalc_order(order_id):
    conn = get_conn()
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id=?", (order_id,)
    ).fetchall()
    total_purchase = sum(r["purchase_price"] * r["quantity"] for r in items)
    total_sale = sum(r["sale_price"] * r["quantity"] for r in items)
    profit = total_sale - total_purchase
    conn.execute(
        "UPDATE orders SET total_purchase=?, total_sale=?, profit=? WHERE id=?",
        (total_purchase, total_sale, profit, order_id)
    )
    conn.commit()
    conn.close()


def delete_order(order_id):
    conn = get_conn()
    conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def add_order_item(order_id, product_name, quantity, purchase_price, sale_price=0):
    conn = get_conn()
    conn.execute("""
        INSERT INTO order_items (order_id, product_name, quantity, purchase_price, sale_price)
        VALUES (?,?,?,?,?)
    """, (order_id, product_name, quantity, purchase_price, sale_price))
    conn.commit()
    conn.close()
    recalc_order(order_id)


def delete_order_item(item_id, order_id):
    conn = get_conn()
    conn.execute("DELETE FROM order_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    recalc_order(order_id)


# ──── Открытые продажи ────

def create_open_sale(buyer_id, buyer_name, user_id=USER_ID):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO open_sales (user_id, buyer_id, buyer_name) VALUES (?,?,?)",
        (user_id, buyer_id, buyer_name)
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_open_sales(status="open", user_id=USER_ID):
    conn = get_conn()
    if status:
        rows = conn.execute(
            "SELECT * FROM open_sales WHERE user_id=? AND status=? ORDER BY id DESC",
            (user_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM open_sales WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_open_sales_by_buyer(buyer_id, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM open_sales WHERE user_id=? AND buyer_id=? AND status='open' ORDER BY id DESC",
        (user_id, buyer_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_open_sale(sale_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM open_sales WHERE id=?", (sale_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_open_sale_items(sale_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM open_sale_items WHERE sale_id=? ORDER BY id", (sale_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_open_sale_items(user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute("""
        SELECT osi.*, os.buyer_id, os.buyer_name
        FROM open_sale_items osi
        JOIN open_sales os ON osi.sale_id = os.id
        WHERE os.user_id=? AND os.status='open'
        ORDER BY osi.id
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_open_sale_items(sale_id, items):
    conn = get_conn()
    for it in items:
        conn.execute("""
            INSERT INTO open_sale_items (sale_id, supplier_name, product_name, quantity, purchase_price)
            VALUES (?,?,?,?,?)
        """, (sale_id, it.get("supplier_name", ""),
              it["product_name"], it["quantity"], it["purchase_price"]))
    conn.commit()
    conn.close()


def delete_open_sale_item(item_id):
    conn = get_conn()
    conn.execute("DELETE FROM open_sale_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def close_open_sale(sale_id):
    conn = get_conn()
    conn.execute(
        "UPDATE open_sales SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE id=?",
        (sale_id,)
    )
    conn.commit()
    conn.close()


def delete_open_sale(sale_id):
    conn = get_conn()
    conn.execute("DELETE FROM open_sales WHERE id=?", (sale_id,))
    conn.commit()
    conn.close()


# ──── Депозит ────

def add_deposit_payment(buyer_id, amount, date, note="", user_id=USER_ID):
    conn = get_conn()
    conn.execute("""
        INSERT INTO deposit_payments (user_id, buyer_id, amount, date, note)
        VALUES (?,?,?,?,?)
    """, (user_id, buyer_id, amount, date, note))
    conn.execute(
        "UPDATE buyers SET deposit = deposit + ? WHERE id=?", (amount, buyer_id)
    )
    conn.commit()
    conn.close()


def get_deposit_payments_by_buyer(buyer_id, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM deposit_payments WHERE user_id=? AND buyer_id=? ORDER BY id DESC",
        (user_id, buyer_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──── Расходы ────

def add_expense(date, category, amount, description="", user_id=USER_ID):
    conn = get_conn()
    conn.execute("""
        INSERT INTO expenses (user_id, date, category, amount, description)
        VALUES (?,?,?,?,?)
    """, (user_id, date, category, amount, description))
    conn.commit()
    conn.close()


EXPENSE_CATEGORIES = ["Зарплата", "Такси", "Другое"]


def get_expenses(date=None, user_id=USER_ID):
    conn = get_conn()
    if date:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE user_id=? AND date=? ORDER BY id DESC",
            (user_id, date)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC, id DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_expenses_by_period(date_from, date_to, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM expenses WHERE user_id=? AND date>=? AND date<=? ORDER BY date DESC, id DESC",
        (user_id, date_from, date_to)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(expense_id):
    conn = get_conn()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


def delete_deposit_payment(payment_id, buyer_id, amount):
    """Delete deposit payment and reverse the deposit change."""
    conn = get_conn()
    conn.execute("DELETE FROM deposit_payments WHERE id=?", (payment_id,))
    conn.execute(
        "UPDATE buyers SET deposit = deposit - ? WHERE id=?", (amount, buyer_id)
    )
    conn.commit()
    conn.close()


# ──── Отчёты ────

def get_orders_by_period(date_from, date_to, user_id=USER_ID):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? AND date>=? AND date<=? ORDER BY date DESC, id DESC",
        (user_id, date_from, date_to)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──── Возвраты ────

def add_return(date, buyer_id, supplier_id, order_id, product_name,
               quantity, purchase_price, sale_price, reason="",
               return_type="refund", user_id=USER_ID):
    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO returns (user_id, date, buyer_id, supplier_id, order_id,
            product_name, quantity, purchase_price, sale_price, reason, return_type)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (user_id, date, buyer_id, supplier_id, order_id,
          product_name, quantity, purchase_price, sale_price, reason, return_type))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_returns(status=None, user_id=USER_ID):
    conn = get_conn()
    if status:
        rows = conn.execute(
            "SELECT * FROM returns WHERE user_id=? AND status=? ORDER BY date DESC, id DESC",
            (user_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM returns WHERE user_id=? ORDER BY date DESC, id DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_return(return_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM returns WHERE id=?", (return_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def close_return(return_id):
    conn = get_conn()
    conn.execute("UPDATE returns SET status='closed' WHERE id=?", (return_id,))
    conn.commit()
    conn.close()


def delete_return(return_id):
    conn = get_conn()
    conn.execute("DELETE FROM returns WHERE id=?", (return_id,))
    conn.commit()
    conn.close()


# ──── Гарантия / Сервис ────

def add_warranty_case(buyer_id, device_name, imei, problem, cost,
                      received_date, user_id=USER_ID):
    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO warranty_cases (user_id, buyer_id, device_name, imei, problem, cost, received_date)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, buyer_id, device_name, imei, problem, cost, received_date))
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def get_warranty_cases(status=None, user_id=USER_ID):
    conn = get_conn()
    if status:
        rows = conn.execute(
            "SELECT * FROM warranty_cases WHERE user_id=? AND status=? ORDER BY received_date DESC",
            (user_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM warranty_cases WHERE user_id=? ORDER BY received_date DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_warranty_case(case_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM warranty_cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_warranty_case(case_id, **kwargs):
    conn = get_conn()
    allowed = {"device_name", "imei", "problem", "cost", "status",
               "received_date", "completed_date", "buyer_id"}
    for key, val in kwargs.items():
        if key in allowed:
            conn.execute(f"UPDATE warranty_cases SET {key}=? WHERE id=?", (val, case_id))
    conn.commit()
    conn.close()


def delete_warranty_case(case_id):
    conn = get_conn()
    conn.execute("DELETE FROM warranty_cases WHERE id=?", (case_id,))
    conn.commit()
    conn.close()


# ──── Снятия из открытых продаж ────

def add_withdrawal(sale_id, amount):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO open_sale_withdrawals (sale_id, amount) VALUES (?,?)",
        (sale_id, amount)
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def get_withdrawals(sale_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM open_sale_withdrawals WHERE sale_id=? ORDER BY id",
        (sale_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def process_withdrawal(withdrawal_id, buyer_id):
    """Process: pay off debt first, then add to deposit."""
    conn = get_conn()
    w = conn.execute("SELECT * FROM open_sale_withdrawals WHERE id=?", (withdrawal_id,)).fetchone()
    if not w:
        conn.close()
        return
    amount = w["amount"]
    buyer = conn.execute("SELECT * FROM buyers WHERE id=?", (buyer_id,)).fetchone()
    if buyer:
        deposit = buyer["deposit"]
        debt = buyer["debt"]
        if debt > 0:
            if amount >= debt:
                remaining = amount - debt
                conn.execute("UPDATE buyers SET deposit=?, debt=0 WHERE id=?",
                             (deposit + remaining, buyer_id))
            else:
                conn.execute("UPDATE buyers SET debt=? WHERE id=?",
                             (debt - amount, buyer_id))
        else:
            conn.execute("UPDATE buyers SET deposit=? WHERE id=?",
                         (deposit + amount, buyer_id))
    conn.execute(
        "UPDATE open_sale_withdrawals SET status='done', processed_at=CURRENT_TIMESTAMP WHERE id=?",
        (withdrawal_id,))
    conn.commit()
    conn.close()


def delete_withdrawal(withdrawal_id):
    conn = get_conn()
    conn.execute("DELETE FROM open_sale_withdrawals WHERE id=?", (withdrawal_id,))
    conn.commit()
    conn.close()
