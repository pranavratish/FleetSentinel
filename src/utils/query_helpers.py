# query_helpers.py
import json
from sqlalchemy import and_, or_

def parse_filter_params(filter_string):
    try:
        return json.loads(filter_string)
    except (ValueError, TypeError):
        return {}

def parse_sort_params(sort_string):
    try:
        return json.loads(sort_string)
    except (ValueError, TypeError):
        return {}

def build_filter_query(query, filters, model):
    for key, value in filters.items():
        if hasattr(model, key):
            column = getattr(model, key)
            if isinstance(value, list):
                query = query.filter(column.in_(value))
            else:
                query = query.filter(column == value)
    return query

def apply_sorting_query(query, sort_by, order, model):
    if hasattr(model, sort_by):
        sort_column = getattr(model, sort_by)
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    return query
