# Режим отладки

> На данный момент имеет минимальный функционал. Находится на стадии разработки.

## arfi_debug

Тип: `#!python bool`
Значение по умолчанию: `#!python False`


## Включение в файле `pyproject.toml`

```toml title="pyproject.toml"
[tool.arfi_settings]
arfi_debug = true
```

## Включение в коде

> Полноценно включается только в файле `pyproject.toml`. Включение при инициализации класса выдаёт урезанную информацию.

```py title="settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig(_arfi_debug=True)
```
