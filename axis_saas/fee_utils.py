import json
from decimal import Decimal


def calculate_fee_total(base_fee, custom_items=None):
    total = Decimal(str(base_fee or 0))
    for item in custom_items or []:
        if not item:
            continue
        title = (item.get('title') or '').strip()
        amount = (item.get('amount') or '').strip()
        if not title or not amount:
            continue
        try:
            total += Decimal(amount)
        except (TypeError, ValueError):
            continue
    return total


def parse_fee_items(value):
    if not value:
        return []
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            return []
        return parse_fee_items(parsed)
    if isinstance(value, dict):
        if 'items' in value:
            return parse_fee_items(value['items'])
        title = (value.get('title') or '').strip()
        amount = (value.get('amount') or '').strip()
        if not title and not amount:
            return []
        return [{'title': title, 'amount': amount}]
    if isinstance(value, list):
        items = []
        for entry in value:
            if not entry:
                continue
            if isinstance(entry, dict):
                title = (entry.get('title') or '').strip()
                amount = (entry.get('amount') or '').strip()
                if title or amount:
                    items.append({'title': title, 'amount': amount})
        return items
    return []


def serialize_fee_items(items):
    parsed = parse_fee_items(items)
    return json.dumps(parsed)
