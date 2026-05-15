#include "SimulatorLifecycle.h"

#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>

namespace {

constexpr const char* kWakeReasonEnv = "MARGINALIA_SIM_WAKE_REASON";
constexpr const char* kLegacyWakeReasonEnv = "CROSSPOINT_SIM_WAKE_REASON";
char** gArgv = nullptr;

}  // namespace

namespace SimulatorLifecycle {

void initProcessArgs(char** argv) { gArgv = argv; }

WakeReason consumeWakeReason() {
  const char* envName = kWakeReasonEnv;
  const char* value = std::getenv(envName);
  if (!value) {
    envName = kLegacyWakeReasonEnv;
    value = std::getenv(envName);
  }
  if (!value) {
    return WakeReason::None;
  }

  unsetenv(envName);
  if (std::strcmp(value, "power") == 0) {
    return WakeReason::PowerButton;
  }
  return WakeReason::None;
}

[[noreturn]] void rebootAsPowerWake() {
  if (!gArgv || !gArgv[0]) {
    std::fputs("SimulatorLifecycle: missing argv for reboot\n", stderr);
    _exit(1);
  }

  setenv(kWakeReasonEnv, "power", 1);
  execvp(gArgv[0], gArgv);

  std::perror("execvp");
  _exit(1);
}

}  // namespace SimulatorLifecycle
