import json
from calendar import monthrange
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


def get_voucher_state(record):
    if record is None:
        return {'read_only': False, 'can_edit': True, 'mode': 'create', 'watermark': None}

    paid_amount = Decimal(str(getattr(record, 'paid_amount', 0) or 0))
    status = (getattr(record, 'status', '') or '').lower()

    if paid_amount > 0 or status in {'paid', 'partial'}:
        watermark = 'PAID' if status == 'paid' else 'PARTIAL'
        return {'read_only': True, 'can_edit': False, 'mode': 'view', 'watermark': watermark}

    return {'read_only': False, 'can_edit': True, 'mode': 'edit', 'watermark': None}


def should_generate_on_date(today, generation_day):
    try:
        generation_day = int(generation_day)
    except (TypeError, ValueError):
        return False
    if generation_day < 1:
        return False
    max_day = monthrange(today.year, today.month)[1]
    effective_day = min(generation_day, max_day)
    return today.day == effective_day


def resolve_student_fee_plan(student, custom_amount=None, custom_items=None, save_for_future=False):
    from .models import FeeStructure

    base_fee = Decimal('0')
    if custom_amount is not None and str(custom_amount).strip() != '':
        try:
            base_fee = Decimal(str(custom_amount))
        except (TypeError, ValueError):
            raise ValueError('Invalid custom amount')
    else:
        grade = getattr(student, 'grade', None)
        fee_struct = None
        if grade:
            fee_struct = FeeStructure.objects.filter(grade=grade).first()
        if fee_struct:
            base_fee = fee_struct.monthly_fee
        else:
            base_fee = Decimal(str(getattr(student, 'custom_fee', 0) or 0))

        if base_fee > 0 and hasattr(student, 'custom_fee') and getattr(student, 'custom_fee', 0) in {None, 0}:
            student.custom_fee = base_fee
            if hasattr(student, 'save'):
                student.save(update_fields=['custom_fee'])

    if base_fee <= 0:
        raise ValueError('No fee structure defined for this grade and no valid custom amount provided.')

    items = parse_fee_items(custom_items)
    if not items:
        items = parse_fee_items(getattr(student, 'fee_custom_items', []))

    if save_for_future and items:
        if hasattr(student, 'fee_custom_items'):
            student.fee_custom_items = items
            student.save(update_fields=['fee_custom_items'])

    total_amount = calculate_fee_total(base_fee, items)
    return base_fee, items, total_amount
