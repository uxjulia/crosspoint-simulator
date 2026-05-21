#include "HalClock.h"

#include <cstdio>
#include <ctime>

HalClock halClock;

void HalClock::begin() {
#if defined(SIMULATOR_DEVICE_X3)
  _available = true;
#else
  _available = false;
#endif
}

bool HalClock::getTime(uint8_t &hour, uint8_t &minute) const {
  if (!_available)
    return false;

  const std::time_t now = std::time(nullptr);
  std::tm utcTime{};
#if defined(_WIN32)
  gmtime_s(&utcTime, &now);
#else
  gmtime_r(&now, &utcTime);
#endif
  hour = static_cast<uint8_t>(utcTime.tm_hour);
  minute = static_cast<uint8_t>(utcTime.tm_min);
  return true;
}

bool HalClock::formatTime(char *buf, size_t bufSize,
                          uint8_t utcOffsetQuarterHoursBiased,
                          bool use12Hour) const {
  if (bufSize < (use12Hour ? 9u : 6u))
    return false;

  uint8_t hour;
  uint8_t minute;
  if (!getTime(hour, minute))
    return false;

  if (utcOffsetQuarterHoursBiased > 104)
    utcOffsetQuarterHoursBiased = 104;
  const int offsetQuarterHours =
      static_cast<int>(utcOffsetQuarterHoursBiased) - 48;
  int totalMinutes =
      static_cast<int>(hour) * 60 + static_cast<int>(minute) +
      offsetQuarterHours * 15;
  totalMinutes = ((totalMinutes % 1440) + 1440) % 1440;

  const int hour24 = totalMinutes / 60;
  const int min = totalMinutes % 60;
  if (use12Hour) {
    const bool pm = hour24 >= 12;
    int hour12 = hour24 % 12;
    if (hour12 == 0)
      hour12 = 12;
    std::snprintf(buf, bufSize, "%d:%02d %s", hour12, min,
                  pm ? "PM" : "AM");
  } else {
    std::snprintf(buf, bufSize, "%02d:%02d", hour24, min);
  }
  return true;
}

bool HalClock::syncFromNTP() { return _available; }
