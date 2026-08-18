# 포트폴리오 텍스트 고치기

배포 주소: https://seulkilog.today/sklee/

## 순서

1. **`content.md` 를 연다** — 페이지의 모든 글이 들어 있다
2. **본문만 고친다** — `[mast.02]` 같은 `[키]` 줄은 건드리지 않는다
3. **터미널에서 한 줄 실행**

```bash
./publish.sh "무엇을 고쳤는지 한 줄"
```

반영과 배포가 한 번에 끝난다. 바뀐 게 없으면 아무것도 하지 않는다.

## content.md 읽는 법

```
[busasu.05]
**결과** — 만족도는 나쁘지 않았는데 회고가 전부 "알겠다"는 말이었습니다.
```

- `[busasu.05]` = 위치를 가리키는 키. **고치면 안 된다**
- 그 아래 빈 줄 전까지가 본문. 여기만 고친다
- 키의 앞부분(`busasu`)은 페이지의 섹션 이름이다

| 키 앞부분 | 페이지 위치 |
|---|---|
| `mast` | 맨 위 제목·소개 |
| `summary` | 01 한눈에 보기 |
| `busasu` | 02 AI 리터러시 교육 12시즌 |
| `star` | 03 무엇을 시킬지 찾아내는 도구 |
| `howto` | 04 한 회차를 어떻게 운영했나 |
| `trials` | 05 참여자들이 실제로 만든 것 |
| `blockers` | 06 회사 안에서 막힌 지점 |
| `automation` | 07 제 업무를 먼저 바꿨습니다 |
| `voices` | 08 회고 원문 |
| `numbers` | 09 숫자 |
| `fit` | 10 공고 요구사항 대조 |
| `beliefs` | 11 S-Beliefs와 제 기록 |
| `career` | 12 경력 |
| `closing` | 맨 아래 맺음말 |

## 쓸 수 있는 서식

| 쓰는 법 | 결과 |
|---|---|
| `**굵게**` | 진하게 |
| `*강조*` | 주황색 (제목에서만 쓸 것) |
| `` `작게` `` | 흐린 작은 글씨 |
| 줄바꿈 | 그대로 줄바꿈 |

그 외 마크다운(제목 `#`, 목록 `-`, 링크)은 **동작하지 않는다.** 글자만 고치는 도구다.

## 구조를 바꾸고 싶을 때

항목을 새로 추가하거나 순서를 바꾸는 것은 `content.md` 로는 안 된다. `index.html` 을 직접 고쳐야 한다.
고친 뒤에는 키가 밀리므로 `python3 tools/portfolio.py export` 로 `content.md` 를 다시 뽑는다.

## 명령어

```bash
python3 tools/portfolio.py export   # index.html → content.md 다시 뽑기 (고친 md는 덮어써짐)
python3 tools/portfolio.py apply    # content.md → index.html 반영
python3 tools/portfolio.py check    # 둘이 같은지 검사
./publish.sh "메시지"                # apply + 커밋 + 배포
```
