#pragma once

#include "esp_partition.h"

inline const esp_partition_t* esp_ota_get_next_update_partition(const esp_partition_t *start_from) {
  return nullptr;
}
