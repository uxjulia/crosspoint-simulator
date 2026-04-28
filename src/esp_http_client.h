#pragma once

#include <cstddef>
#include <cstdint>

typedef void *esp_http_client_handle_t;
typedef int esp_err_t;

#define ESP_OK 0
#define ESP_ERR_NO_MEM -1
#define ESP_FAIL -2

enum http_event { HTTP_EVENT_ON_DATA };

struct esp_http_client_event_t {
  http_event event_id;
  esp_http_client_handle_t client;
  void *data;
  int data_len;
};

typedef esp_err_t (*http_event_handler_cb)(esp_http_client_event_t *evt);

struct esp_http_client_config_t {
  const char *url = nullptr;
  http_event_handler_cb event_handler = nullptr;
  int timeout_ms = 0;
  int buffer_size = 0;
  int buffer_size_tx = 0;
  bool skip_cert_common_name_check = false;
  esp_err_t (*crt_bundle_attach)(void *conf) = nullptr;
  bool keep_alive_enable = false;
};

inline esp_err_t esp_http_client_set_header(esp_http_client_handle_t,
                                            const char *, const char *) {
  return ESP_OK;
}
inline bool esp_http_client_is_chunked_response(esp_http_client_handle_t) {
  return false;
}
inline int esp_http_client_get_content_length(esp_http_client_handle_t) {
  return 0;
}
inline esp_err_t esp_http_client_get_chunk_length(esp_http_client_handle_t,
                                                  int *len) {
  if (len)
    *len = 0;
  return ESP_OK;
}
inline esp_http_client_handle_t
esp_http_client_init(const esp_http_client_config_t *) {
  return nullptr;
}
inline esp_err_t esp_http_client_perform(esp_http_client_handle_t) {
  return ESP_FAIL;
}
inline esp_err_t esp_http_client_cleanup(esp_http_client_handle_t) {
  return ESP_OK;
}
inline const char *esp_err_to_name(esp_err_t) { return "simulator-stub"; }

// The firmware redeclares esp_crt_bundle_attach as `extern "C" extern` and
// links against ESP-IDF for the real implementation. In the simulator we
// satisfy the link with a no-op stub.
extern "C" {
inline esp_err_t esp_crt_bundle_attach(void *) { return ESP_OK; }
}
