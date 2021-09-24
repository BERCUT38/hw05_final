from django.utils import timezone as tz


def year(request):
    """Добавляет переменную с текущим годом."""
    now = tz.localtime(tz.now())
    year = int(now.strftime("%Y"))
    return {'year': year, }
