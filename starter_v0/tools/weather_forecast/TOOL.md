# weather_forecast Tool

Tra cứu thời tiết hiện tại và dự báo thời tiết cho một vị trí/thành phố cụ thể.

## Implementation Details

- Endpoint: Open-Meteo Free Public Geocoding & Weather API (`api.open-meteo.com`).
- No API key required.

## Arguments

- `location` (str, required): Tên thành phố hoặc vị trí (ví dụ: "Hanoi", "Ho Chi Minh City", "Tokyo", "London").
- `days` (int, optional, default=1): Số ngày dự báo (từ 1 đến 7).

## Returns

Object dạng `dict`:
- `location`: Tên vị trí đã xác thực
- `latitude`: Vĩ độ
- `longitude`: Kinh độ
- `current_temperature`: Nhiệt độ hiện tại (°C)
- `weather_condition`: Trạng thái thời tiết
- `items`: Danh sách dữ liệu chi tiết
- `error`: Chuỗi thông báo lỗi (nếu có) hoặc `None`
