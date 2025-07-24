#!/bin/bash

ID="template@template.com"
PW="template_password"

# Mini 데이터셋 다운로드 (개발/테스트용 - 가장 작은 크기)
python download_nuplan.py --username "$ID" --password "$PW" \
    --mini-set --maps --log-db