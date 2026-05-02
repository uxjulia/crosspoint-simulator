#pragma once

#include <cstdint>

class HalTiltSensor {
public:
  void begin() {}
  bool wake() {
#ifdef FORCE_TILT_SENSOR_AVAILABLE
    return true;
#else
    return false;
#endif
  }
  bool deepSleep() {
#ifdef FORCE_TILT_SENSOR_AVAILABLE
    return true;
#else
    return false;
#endif
  }
  bool isAvailable() const {
#ifdef FORCE_TILT_SENSOR_AVAILABLE
    return true;
#else
    return false;
#endif
  }
  void update(const uint8_t, const uint8_t, const bool) {}
  bool wasTiltedForward() { return false; }
  bool wasTiltedBack() { return false; }
  bool hadActivity() { return false; }
  void clearPendingEvents() {}
};

extern HalTiltSensor halTiltSensor;
