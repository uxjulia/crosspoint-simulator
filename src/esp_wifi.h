#pragma once

#include "esp_http_client.h" // for esp_err_t / ESP_OK

enum wifi_ps_type_t {
  WIFI_PS_NONE = 0,
  WIFI_PS_MIN_MODEM = 1,
  WIFI_PS_MAX_MODEM = 2,
};

inline esp_err_t esp_wifi_set_ps(wifi_ps_type_t) { return ESP_OK; }
