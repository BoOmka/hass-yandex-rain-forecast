# Yandex Rain Sensor

_Простой сенсор, который показывает текстом информацию о текущих или грядущих осадках_

![example][example1]

## Установка

Скопировать содержимое директории `/custom_components/yandex_rain/` в `<hass-config>/custom_components/yandex_rain/`.

Или импортировать как кастомный репозиторий в [HACS](https://hacs.xyz/docs/faq/custom_repositories/).


## Конфигурация
  
key | type | description  
:--- | :--- | :---  
**platform (Required)** | string | Платформа сенсора.
**name (Required)** | string | Название сенсора в Home Assistant.
**latitude (Optional)** | float | Широта. По умолчанию берется из конфигурации Home Assistant
**longitude (Optional)** | float | Долгота. По умолчанию берется из конфигурации Home Assistant
**scan_interval (Optional)** | int | Интервал обновления в секундах. По умолчанию 300 секунд (5 минут)


## Пример конфигурации в configuration.yaml

```yaml
sensor:
  platform: yandex_rain
  name: rain_info
  latitude: 12.34
  longitude: 23.45
  scan_interval: 300
```


[example1]: images/example1.png
