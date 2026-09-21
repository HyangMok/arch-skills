---
name: arch-image-edit-prompts
description: Write and debug image-generation prompts that change only part of an existing architectural image (render, viewport capture, massing, photo) while preserving the rest, such as swapping facade material, rendering a massing capture in a reference mood, replacing context or time of day, editing a region marked in an annotation image, or describing repeating facade modules. Use for Korean requests like 입면 재질만 바꿔줘, 매스 유지하면서 렌더링, 시점 그대로 배경만, 표시한 부분만 수정, 프롬프트 다시 써줘, 왜 매스가 변형됐지. Not for generating a finished aerial or perspective from nothing, and not for running the image model itself.
---

# 건축 이미지 부분 편집 프롬프트

이미 있는 건축 이미지를 이미지 생성 모델에 넣어 **일부만 바꾸고 나머지는 지키게** 하는 프롬프트를 쓰고, 결과가 어긋났을 때 원인을 찾아 고친다. 결과물은 프롬프트 본문과 생성 후 확인 목록이다. 이미지 생성 자체는 사용자가 쓰는 도구(ChatGPT 이미지, gpt-image API, Codex 내장 생성 등)에서 실행한다.

## 먼저 정한다

프롬프트를 쓰기 전에 세 목록을 사용자와 확정한다. 모호하면 한 번만 묻는다.

- **고정**: 절대 바뀌면 안 되는 것. 카메라 시점과 높이, 매스 윤곽과 층수, 필로티 높이, 개구부 위치, 배경·사람·차량, 이미지 안 글자.
- **변경**: 이번에 바꿀 것. 재질, 패턴, 시간대, 특정 영역의 부재. 같은 건물 안에서 **제외할 부분**(필로티 기둥, 커튼월, 옥탑)도 함께 쓴다. "중앙 동 외장"이라고만 쓰면 기둥까지 바뀐다.
- **금지**: 모델이 습관적으로 덧붙이는 것. 요청하지 않은 소품·장식·물방울·영문 문구, 매스를 수직으로 펴는 것, 층수 변경, 시점 이동.

첨부 이미지가 둘 이상이면 **첫 줄에 이미지 번호별 역할**을 선언한다. "1번은 수정할 원본, 2번은 분위기만 참고, 3번은 수정 영역을 표시한 주석"처럼. 역할이 뒤바뀌는 실패가 가장 흔하다.

## 프롬프트 뼈대

[references/prompt-skeleton.md](references/prompt-skeleton.md)의 여섯 구획을 쓴다. 건축 부분 편집에서는 **역할 선언 → 고정 목록 → 변경 지시 → 금지 목록 → 카메라 → 조명 → 재질** 순서가 안정적이다. 짧은 편집이라도 고정과 금지는 생략하지 않는다. 템플릿은 읽기 쉽게 한국어로 적었지만, 실행 기록의 프롬프트는 모두 영어였다. 모델에 넣을 최종본은 영어로 쓰는 것을 기본으로 한다.

## 작업 유형별 템플릿

[references/task-templates.md](references/task-templates.md)에서 해당 유형을 골라 채운다.

| 유형 | 상황 |
|---|---|
| A 재질·입면 교체 | 매스·시점·배경 유지, 외장만 바꿈 |
| B 캡처를 렌더로 | 뷰포트 캡처의 형태·각도 유지, 참고 렌더 분위기 적용 |
| C 배경·시간대 교체 | 건물 고정, 주변·조명만 바꿈 |
| D 주석 이미지 국소 수정 | 표시한 영역만 바꿈. 표시 색은 지시 기호 |
| E 비율·구도 보정 | 참고 이미지의 비율·여백에 맞춤, 디자인 유지 |
| F 반복 모듈 서술 | 프레임 기울기·루버 간격 같은 반복 요소를 순서대로 말로 풀기 |
| G 대상 강조 | 조감도에서 대상 단지만 밝게, 주변은 채도·선명도 낮춤 |

## 생성 후 확인

[references/preservation-checklist.md](references/preservation-checklist.md)로 원본과 결과를 대조한다. 층수는 분절선을 세어 확인하고, 시점은 반투명으로 겹쳐 본다. `scripts/count_floors.py`는 정면 밝은 입면에서 층수를 어림하는 보조 도구이며 기울어진 동, 어두운 재질, 야간 이미지에서는 1~2층 어긋난다. 최종 층수는 눈으로 센다. `scripts/compare_edit.py`는 원본·결과·검사를 나란히 놓은 `report.png` 한 장을 만든다. 허용 영역 안 변경은 노란색, 밖으로 새어 나간 변경은 빨간색으로 채워지므로 층수 감소나 요청하지 않은 요소가 바로 보인다.

생성형 편집기는 이미지 전체를 다시 그리므로 나무·그림자·질감은 항상 미세하게 바뀐다. **보존은 픽셀이 아니라 구조(윤곽·층수·요소) 단위로 판정한다.** 스크립트의 기본 지표는 축소·블러 후 비교한 구조 단위 값이고, 픽셀 단위 값은 `_fine` 접미사로 따로 기록된다. 확대해서 뭉개짐이나 붓터치 같은 표현이 보이면 검토용으로만 쓰고 최종본으로 내지 않는다.

```bash
python scripts/compare_edit.py original.png result.png --mask region.png --out compare/
```

`assets/example/`에 가상 박스 건물로 만든 원본·결과·마스크·주석 이미지가 있다. 스크립트 사용법을 시험하거나 주석 이미지의 형식을 설명할 때 쓴다. 실제 프로젝트 이미지가 아니다.

## 어긋났을 때

[references/failure-diagnosis.md](references/failure-diagnosis.md)에서 증상을 찾는다. 시점이 틀어지거나 매스가 변형되면 같은 대화에서 재생성을 반복하지 말고 **새 대화에서 원본을 다시 첨부**하고 완결형 프롬프트로 시작한다. 같은 원본을 세 번 이상 연속 편집하면 질감이 드리프트하므로 원본에서 다시 시작한다.

## 모델 차이

[references/model-notes.md](references/model-notes.md)에 gpt-image 계열 관찰과 공식 문서 근거를 적어 두었다. 편집 정밀도가 높은 모델일수록 요청하지 않은 요소를 더 자주 덧붙이는 경향이 있으므로 금지 목록을 더 길게 쓴다. 관찰은 사례 단위이며 보편적 승률이 아니다.

## 실제 실행 기록

[cases/](cases/README.md)에 가상 건물로 ChatGPT 웹에서 실행한 기준 생성 1건과 편집 6건의 판정이 있다. 요지: 한 줄 프롬프트가 구조를 깨뜨린 사례는 두 쌍의 대조에서 없었고, 고정·금지 목록의 실질 효과는 변경 범위를 좁게 유지하는 것과, 같은 건물의 다른 부위로 번지는 것을 막는 "제외 부위" 문장(1회 관찰)에 있는 것으로 보인다. 실패한 것은 깊이 방향 형상 서술(입면 사선으로 해석)과 정량 지시(채도 30% 감소 무시)였다. 캡처→렌더(유형 B)처럼 매스가 걸린 편집은 아직 시험하지 않았다. 주장 수위는 이 기록에 맞춘다.

## 하지 않는 것

- 빈 화면에서 완성형 조감도·투시도를 만드는 프롬프트. 이 스킬은 기존 이미지의 부분 편집만 다룬다.
- 매스 보존을 보장하는 것. 프롬프트로 확률을 높이고 확인 목록으로 걸러낼 뿐이다.
- 타일로 나눠 업스케일한 뒤 재합성하는 방식. 이음매와 경계 불일치가 반복되어 권장하지 않는다.
