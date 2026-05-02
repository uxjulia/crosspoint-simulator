#pragma once

#include <Arduino.h>

#include "HalGPIO.h"

namespace CrossPointOrientation {
enum Value : uint8_t { PORTRAIT = 0, LANDSCAPE_CW = 1, INVERTED = 2, LANDSCAPE_CCW = 3 };
}

namespace CrossPointTiltPageTurn {
enum Value : uint8_t { TILT_OFF = 0, TILT_NORMAL = 1, TILT_INVERTED = 2 };
}

class HalTiltSensor;
extern HalTiltSensor halTiltSensor;

class HalTiltSensor {
 private:
  bool _available = false;
  bool _isAwake = false;

 public:
  void begin() {
#ifdef FORCE_TILT_SENSOR_AVAILABLE
    _available = true;
#else
    _available = false;
#endif
    _isAwake = false;
  }

  bool wake() {
    if (!_available) return false;
    _isAwake = true;
    return true;
  }

  bool deepSleep() {
    if (!_available) return false;
    _isAwake = false;
    return true;
  }

  bool isAvailable() const { return _available; }
  void update(uint8_t /*mode*/, uint8_t /*orientation*/, bool /*inReader*/) {}
  bool wasTiltedForward() { return false; }
  bool wasTiltedBack() { return false; }
  bool hadActivity() { return false; }
  void clearPendingEvents() {}
};
