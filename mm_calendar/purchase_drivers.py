"""Always-on purchase drivers — lift revenue/PU but are not Monday board promos."""

MONTH_OPEN_BIGGEST_DENOM = {
    "id": "month_open_biggest_denom",
    "label": "1st of month — biggest store denom",
    "kind": "purchase_driver",
    "monday_product": "Offers & coin sale",
    "desc": (
        "Added to the store denom,\n"
        "gives both coins & gems like the american denom in 4th of july"
    ),
}


def ensure_month_open_biggest_denom(day: dict) -> None:
    if day.get("date") != 1:
        return
    drivers = list(day.get("purchaseDrivers") or [])
    if any(d.get("id") == MONTH_OPEN_BIGGEST_DENOM["id"] for d in drivers):
        day["purchaseDrivers"] = drivers
        return
    drivers.append(dict(MONTH_OPEN_BIGGEST_DENOM))
    day["purchaseDrivers"] = drivers


def ensure_all_months(months: dict) -> None:
    for days in months.values():
        for day in days:
            ensure_month_open_biggest_denom(day)
