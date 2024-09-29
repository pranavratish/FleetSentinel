# filtering_service.py
from utils.query_helpers import build_filter_query, apply_sorting_query

def filter_records(query, filter_params, sort_params, model):
    # Apply filtering
    query = build_filter_query(query, filter_params, model)
    
    # Apply sorting
    if sort_params.get('sort_by') and sort_params.get('order'):
        query = apply_sorting_query(query, sort_params['sort_by'], sort_params['order'], model)
    
    return query