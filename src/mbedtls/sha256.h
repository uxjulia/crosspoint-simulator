#pragma once

#include <stddef.h>

struct mbedtls_sha256_context {
};

inline void mbedtls_sha256_init(mbedtls_sha256_context *ctx) {
}

inline int mbedtls_sha256_starts(mbedtls_sha256_context *ctx, int is224) {
  return 0;
}

inline int mbedtls_sha256_finish(mbedtls_sha256_context *ctx, unsigned char *output) {
  return 0;
}

inline void mbedtls_sha256_free(mbedtls_sha256_context *ctx) {
}

inline int mbedtls_sha256_update(mbedtls_sha256_context *ctx, const unsigned char *input, size_t ilen) {
  return 0;
}
