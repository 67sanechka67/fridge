import datetime
from decimal import Decimal

# Константа формата даты для стандартизации работы со строками
DATE_FORMAT = '%Y-%m-%d'

# Исходный словарь с содержимым холодильника
goods = {}


def add(items, title, amount, expiration_date=None):
    """Добавляет партию продукта в словарь items."""
    if isinstance(expiration_date, str):
        expiration_date = datetime.datetime.strptime(expiration_date, DATE_FORMAT).date()

    amount = Decimal(str(amount))
    new_batch = {'amount': amount, 'expiration_date': expiration_date}

    if title in items:
        items[title].append(new_batch)
    else:
        items[title] = [new_batch]


def add_by_note(items, note):
    """Разбирает текстовую заметку и передает данные в функцию add()."""
    parts = note.split()

    if len(parts) > 1 and '-' in parts[-1] and len(parts[-1]) == 10:
        expiration_date = parts.pop()
    else:
        expiration_date = None

    amount = Decimal(parts.pop())
    title = ' '.join(parts)
    add(items, title, amount, expiration_date)


def find(items, needle):
    """Ищет продукты, в названии которых (без учета регистра) есть строка needle."""
    needle_lower = needle.lower()
    result = []

    for title in items.keys():
        if needle_lower in title.lower():
            result.append(title)

    return result


def get_amount(items, needle):
    """Возвращает суммарное количество всех продуктов, подходящих под needle."""
    found_products = find(items, needle)
    total_amount = Decimal('0')

    for title in found_products:
        for batch in items[title]:
            total_amount += batch['amount']

    return total_amount


def get_expired(items, in_advance_days=0):
    """Возвращает список кортежей (title, amount) для просроченных продуктов.

    Количество просроченных партий одного и того же продукта суммируется.
    """
    # Обрабатываем случай, если тренажер передал in_advance_days=None
    if in_advance_days is None:
        in_advance_days = 0

    # Вычисляем целевую дату: сегодня + запас дней
    target_date = datetime.date.today() + datetime.timedelta(days=in_advance_days)

    # Используем словарь для промежуточного суммирования просрочки по продуктам
    expired_dict = {}

    for title, batches in items.items():
        for batch in batches:
            exp_date = batch['expiration_date']
            # Если срок годности задан и он меньше или равен целевой дате
            if exp_date is not None and exp_date <= target_date:
                if title in expired_dict:
                    expired_dict[title] += batch['amount']
                else:
                    expired_dict[title] = batch['amount']

    # Преобразуем накопленный словарь в список кортежей, как требует тренажер
    return list(expired_dict.items())
