#!/usr/bin/env bash
set -euo pipefail
# Keep the Android API 24 configuration from selecting API 28+ spawn functions.
export ac_cv_func_posix_spawn=no
export ac_cv_func_posix_spawnp=no
export TAR_OPTIONS="${TAR_OPTIONS:---no-same-owner}"
exec buildozer -v android debug
