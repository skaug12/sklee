#!/bin/bash
# content.md 를 index.html 에 반영하고 배포한다
set -e
cd "$(dirname "$0")"
python3 tools/portfolio.py apply
if git diff --quiet; then echo "바뀐 내용 없음. 배포 생략"; exit 0; fi
git add -A
git -c user.name="이슬기" -c user.email="skaug12@gmail.com" commit -q -m "${1:-포트폴리오 텍스트 수정}"
git push -q origin main
echo "배포함 → https://seulkilog.today/sklee/  (1~2분 뒤 반영)"
