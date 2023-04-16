import datetime

def ms_to_readable_string(milliseconds: int) -> str:
    seconds, remaining_milliseconds = divmod(int(milliseconds), 1000)
    minutes, remaining_seconds = divmod(seconds, 60)
    hours, remaining_minutes = divmod(minutes, 60)
    days, remaining_hours = divmod(hours, 24)

    parts = []

    if days > 0:
        parts.append(f"{days} days")

    if remaining_hours > 0:
        parts.append(f"{remaining_hours} hours")

    if remaining_minutes > 0:
        parts.append(f"{remaining_minutes} minutes")

    if remaining_seconds > 0:
        parts.append(f"{remaining_seconds} minutes")
        # second_str = f"{remaining_seconds}.{remaining_milliseconds:03} seconds"
        # if remaining_milliseconds > 0:
        #     second_str += f" ({remaining_milliseconds} milliseconds)"
        # parts.append(second_str)

    if remaining_milliseconds > 0:
        parts.append(f"{remaining_milliseconds} ms")
        

    return ", ".join(parts)

def secs_to_readable_string(seconds: int) -> str:
    return ms_to_readable_string(seconds * 1000)


# # Example usage
# milliseconds = 43572002
# human_readable = milliseconds_to_human_readable(milliseconds)
# print(f"{milliseconds} milliseconds is: {human_readable}")

# backoff delay algorith to reduce furious attempts to reconnect

BACKOFF_DELAY_MIN_MS = 200
BACKOFF_DELAY_MAX_MS = 5 * 60 * 1000 # 5 minutes

def backoff_delay(time_ref: datetime, attempts: int) -> float:

    trying_ms: int = ((datetime.now() - time_ref).total_seconds() * 1000)
    delay_ms: int = 0

    if trying_ms >= 5 * 1000: # >= 5 seconds = 100 ms
        delay_ms = 1000
    elif trying_ms >= 2 * 60 * 1000: # >= 2 minutes: 2 seconds
        delay_ms = 5 * 1000
    elif trying_ms >= 20 * 60 * 1000: # >= 20 minutes = 2 seconds
        delay_ms = 30 * 1000

    delay_ms = min(max(BACKOFF_DELAY_MIN_MS,delay_ms),BACKOFF_DELAY_MAX_MS)
    delay_secs = float(delay_ms / 1000)

    return delay_secs
