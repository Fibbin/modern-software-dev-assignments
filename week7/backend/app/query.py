from sqlalchemy import Select, asc, desc


def apply_sort_and_pagination(
    stmt: Select,
    model: type,
    *,
    skip: int,
    limit: int,
    sort: str,
    allowed_fields: set[str],
    default_field: str = "created_at",
) -> Select:
    """Apply a whitelisted sort (with id tie-breaker) plus skip/limit pagination."""
    descending = sort.startswith("-")
    field = sort.lstrip("-")
    if field not in allowed_fields:
        field = default_field
        descending = default_field == "created_at"

    column = getattr(model, field)
    primary = desc(column) if descending else asc(column)
    if field == "id":
        return stmt.order_by(primary).offset(skip).limit(limit)

    tie = desc(model.id) if descending else asc(model.id)
    return stmt.order_by(primary, tie).offset(skip).limit(limit)
