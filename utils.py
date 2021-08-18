from datetime import datetime, timezone

def get_date(format="%d_%m_%Y"):
    return datetime.strftime(datetime.now(), format)

def epoch_to_string(epoch):
    readable_date = datetime.utcfromtimestamp(epoch).replace(tzinfo=timezone.utc)
    return datetime.strftime(readable_date, "%d/%m/%Y")