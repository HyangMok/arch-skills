# 케이스 00. 기준 이미지 생성

모든 편집 케이스의 원본이 되는 가상 건물 이미지. 특정 프로젝트를 닮지 않게 설계했고, 이후 케이스가 시험할 실패 유형(매스 변형, 층수 변화, 기울기 소실, 필로티 변경, 시점 이동)을 모두 담고 있다.

## 고정 사양 (이후 케이스의 보존 기준)

| 항목 | 값 |
|---|---|
| 동 구성 | 좌측 판상형 12층, 중앙 판상형 12층, 우측 타워형 9층 |
| 저층부 | 세 동 모두 필로티 2개층, 기둥 노출 |
| 특징 1 | 중앙 동 정면 가운데에 전층 커튼월 띠, 폭은 정면의 약 1/3 |
| 특징 2 | 우측 타워의 남측(화면 좌측을 향한) 입면이 위로 갈수록 안쪽으로 약 8도 기울어짐 |
| 외장 | 밝은 회백색 석재 패널, 창호는 짙은 회색 프레임 |
| 주변 | 저층 주거지, 가로수, 2차선 도로, 멀리 낮은 산 능선 |
| 카메라 | 눈높이보다 약간 높은 3/4 정면, 좌측 45도, 세 동이 모두 보임 |
| 조명 | 오후 늦은 시간, 좌측 상단 태양, 맑은 하늘 |
| 글자 | 없음 |
| 비율 | 3:2 가로 |

## 프롬프트 (ChatGPT 웹에 그대로 입력)

```text
Photorealistic architectural rendering of a fictional residential complex. Three buildings in one view, 3:2 landscape.

Left: a 12-storey slab block. Center: a 12-storey slab block with a full-height glass curtain-wall strip in the middle of its front facade, about one third of the facade width. Right: a 9-storey tower whose left-facing (south) facade tilts inward about 8 degrees toward the top.

All three buildings stand on a 2-storey open pilotis with exposed columns. Facades are light grey-white stone panels with dark grey window frames. No text, signs or logos anywhere.

Camera slightly above eye level, three-quarter front view from the left at about 45 degrees, all three buildings fully visible with sky above and street in front. Surroundings: low-rise housing, street trees, a two-lane road, low mountain ridge far in the background. Late afternoon sunlight from the upper left, clear sky. Clean, realistic CG rendering style, no people in the foreground.
```

## 생성 후 확인

- 동별 층수 12 / 12 / 9를 분절선으로 센다. 다르면 재생성.
- 우측 타워의 기울기가 보이는지, 커튼월 띠가 중앙 동에만 있는지.
- 글자·간판이 없는지.
- 통과하면 `base.jpg`로 저장하고 층수·모서리 위치를 `preservation.md`에 기록한다.
