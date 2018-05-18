#!/bin/bash
set -euo pipefail

sudo fbi -T 2 -d /dev/fb1 -noverbose -a "$@"
