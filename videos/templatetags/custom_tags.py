from django import template
import math

from datetime import timedelta
from datetime import datetime
register = template.Library()

@register.filter(name='diff_dates')
def diff_dates(value):
    if not isinstance(value, timedelta):
        raise ValueError("El valor debe ser un objeto timedelta")

    total_minutes = int(value.total_seconds() // 60)
    value = total_minutes
    format_dates = "minutos"

    if total_minutes > 60:
        total_hours = total_minutes // 60
        value = total_hours
        format_dates = "horas"

        if total_hours > 24:
            total_days = total_hours // 24
            value = total_days
            format_dates = "días"

            if total_days > 30:
                total_weeks = total_days // 7
                value = total_weeks
                format_dates = "semanas"

                if total_weeks > 4:
                    total_months = total_days // 30
                    value = total_months
                    format_dates = "meses"

                    if total_months > 12:
                        total_years = total_months // 12
                        value = total_years
                        format_dates = "años"

    return [value, format_dates]