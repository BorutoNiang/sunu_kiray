import datetime

def fix_timedelta(row: dict, fields: list = None) -> dict:
    """Convertit les timedelta MySQL en string HH:MM:SS et les dates en string."""
    if fields is None:
        fields = list(row.keys())
    for k in fields:
        v = row.get(k)
        if isinstance(v, datetime.timedelta):
            s = int(v.total_seconds())
            row[k] = f"{s//3600:02d}:{(s%3600)//60:02d}:00"
        elif isinstance(v, (datetime.date, datetime.datetime)):
            row[k] = str(v)
    return row

def fix_rows(rows: list, fields: list = None) -> list:
    return [fix_timedelta(r, fields) for r in rows]
