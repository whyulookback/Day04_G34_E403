# currency_convert Tool

Chuyển đổi tỷ giá ngoại tệ giữa hai đồng tiền dựa trên tỷ giá thị trường thời gian thực.

## Implementation Details

- Endpoint: ExchangeRate Open API (`open.er-api.com`).
- No API key required.

## Arguments

- `from_currency` (str, required): Mã đồng tiền nguồn (ví dụ: "USD", "EUR", "JPY", "VND").
- `to_currency` (str, required): Mã đồng tiền đích (ví dụ: "VND", "USD", "EUR").
- `amount` (float, optional, default=1.0): Số tiền cần quy đổi.

## Returns

Object dạng `dict`:
- `from_currency`: Đồng tiền nguồn
- `to_currency`: Đồng tiền đích
- `amount`: Số tiền ban đầu
- `converted_amount`: Số tiền sau quy đổi
- `rate`: Tỷ giá quy đổi 1 unit
- `items`: Danh sách dữ liệu chi tiết
- `error`: Chuỗi thông báo lỗi (nếu có) hoặc `None`
