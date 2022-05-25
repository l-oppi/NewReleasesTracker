import json
import pendulum as pdl
import pprint as pp


pp.PrettyPrinter(indent=4)


def get_epoch(datetime: str = "", timezone="America/Sao_Paulo") -> int:
    if datetime == "":
        return pdl.now(tz=timezone).int_timestamp
    return pdl.parse(datetime, tz=timezone).int_timestamp


def get_date(format="DD_MM_YYYY", timezone="America/Sao_Paulo") -> str:
    return pdl.now(tz=timezone).format(format)


def epoch_to_str(epoch, timezone="America/Sao_Paulo") -> str:
    return pdl.from_timestamp(epoch, tz=timezone).format("DD_MM_YYYY")


def open_json(filename) -> dict:
    with open(filename, "r") as f:
        return json.load(f)


def update_json(filename, data) -> None:
    with open(filename, "r") as f:
        json_data = json.load(f)
    json_data.update(data)
    with open(filename, "w") as f:
        json.dump(json_data, f, indent=4)


def save_json(filename, data, indent=4) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=indent)


def from_obj(filename, value):
    data = open_json(filename)
    if value in data:
        return data[value]
    return None


def debug_json(object) -> None:
    pp.pprint(object)


if __name__ == "__main__":
    # print(Utils().from_obj("include/CONFIG.json", "refresh_token"))
    print(get_epoch())
