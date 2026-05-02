#pragma once

#include <cstdint>

class HalTiltSensor {
public:
  void begin() {}
  bool wake() { return false; }
  bool deepSleep() { return false; }
  bool isAvailable() const { return false; }
  void update(const uint8_t, const uint8_t, const bool) {}
  bool wasTiltedForward() { return false; }
  bool wasTiltedBack() { return false; }
  bool hadActivity() { return false; }
  void clearPendingEvents() {}
};

extern HalTiltSensor halTiltSensor;
