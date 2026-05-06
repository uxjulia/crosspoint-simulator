#pragma once

#include "esp_err.h"

#include <stddef.h>

enum esp_partition_type_t { ESP_PARTITION_TYPE_DATA };

enum esp_partition_subtype_t {
  ESP_PARTITION_SUBTYPE_DATA_OTA,
  ESP_PARTITION_SUBTYPE_APP_OTA_0,
};

struct esp_partition_t {
  esp_partition_subtype_t subtype = ESP_PARTITION_SUBTYPE_APP_OTA_0;
  uint32_t address = 0;
  uint32_t size = 0;
  char label[17] = {};
};

inline const esp_partition_t* esp_partition_find_first(esp_partition_type_t type, esp_partition_subtype_t subtype, const char* label) {
  return nullptr;
}

inline esp_err_t esp_partition_read(const esp_partition_t* partition, size_t src_offset, void* dst, size_t size) {
  return ESP_FAIL;
}

inline esp_err_t esp_partition_erase_range(const esp_partition_t* partition, size_t offset, size_t size) {
  return ESP_FAIL;
}

inline esp_err_t esp_partition_write(const esp_partition_t* partition, size_t dst_offset, const void* src, size_t size) {
  return ESP_FAIL;
}
