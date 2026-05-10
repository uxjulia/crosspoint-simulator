#include <Logging.h>

#include "network/OtaUpdater.h"

bool OtaUpdater::isUpdateNewer() const { return false; }
const std::string &OtaUpdater::getLatestVersion() const {
  static const std::string version = CROSSPOINT_VERSION;
  return version;
}

OtaUpdater::OtaUpdaterError OtaUpdater::checkForUpdate() {
  LOG_DBG("OTA", "[SIM] OTA check is non-destructive; reporting no update");
  return NO_UPDATE;
}

OtaUpdater::OtaUpdaterError
OtaUpdater::installUpdate(ProgressCallback onProgress, void *ctx
#ifdef CROSSINK_VERSION
                          ,
                          std::atomic<bool> *cancelRequested
#endif
) {
  LOG_DBG("OTA", "[SIM] OTA install is not supported in the native simulator");
  processedSize = 1;
  totalSize = 1;
  if (onProgress)
    onProgress(ctx);
#ifdef CROSSINK_VERSION
  if (cancelRequested && cancelRequested->load())
    return CANCELLED_ERROR;
#endif
  return INTERNAL_UPDATE_ERROR;
}
