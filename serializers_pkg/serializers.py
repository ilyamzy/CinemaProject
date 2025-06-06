import json


class GenreSerializer:
    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}
        self.validated_data = {}

    def is_valid(self):
        name = self.data.get('name', '').strip()
        if not name:
            self.errors['name'] = 'Это поле не может быть пустым.'
            return False
        self.validated_data['name'] = name
        return True


class HallCreateSerializer:
    def __init__(self, data: dict, files=None):
        self.data = data
        self.files = files or {}
        self.validated_data = None
        self.errors = {}

    def is_valid(self):
        try:
            name = self.data.get("name", "").strip()
            try:
                rows = int(self.data.get("rows"))
                cols = int(self.data.get("cols"))
            except (TypeError, ValueError):
                self.errors["rows/cols"] = "Поля 'rows' и 'cols' должны быть целыми числами"
                return False

            try:
                seats = json.loads(self.data.get("seats", "[]"))
            except json.JSONDecodeError:
                self.errors["seats"] = "Некорректный JSON в поле 'seats'"
                return False

            if not name:
                self.errors["name"] = "Название обязательно"
            if rows <= 0:
                self.errors["rows"] = "Количество рядов должно быть положительным"
            if cols <= 0:
                self.errors["cols"] = "Количество мест в ряду должно быть положительным"
            if not isinstance(seats, list):
                self.errors["seats"] = "Поле 'seats' должно быть списком"

            parsed_seats = []
            if isinstance(seats, list):
                for i, seat in enumerate(seats):
                    try:
                        row = int(seat["row"])
                        col = int(seat["col"])
                        seat_type = seat["type"]
                        if seat_type not in ["single", "double"]:
                            raise ValueError(f"Неверный тип места: {seat_type}")
                        parsed_seats.append({
                            "row": row,
                            "col": col,
                            "seat_type": seat_type
                        })
                    except (KeyError, ValueError, TypeError) as e:
                        self.errors[f"seats[{i}]"] = f"Ошибка в описании места: {str(e)}"

            if self.errors:
                return False

            self.validated_data = {
                "name": name,
                "rows": rows,
                "cols": cols,
                "seats": parsed_seats,
                "poster": self.files.get("poster")
            }
            return True

        except Exception as e:
            self.errors["non_field_error"] = str(e)
            return False
