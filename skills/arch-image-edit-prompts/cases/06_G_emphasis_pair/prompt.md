# 케이스 06. 유형 G 대상 강조: 구조 프롬프트 vs 한 줄 프롬프트

같은 목표(**중앙 동을 눈에 띄게**)를 두 프롬프트로 실행해 나란히 비교한다. 대상 강조는 톤·채도 조정만 허용되고 매스·층수·카메라는 바뀌면 안 되는 편집이라, 구조 목록의 효과가 케이스 01/03보다 크게 드러날 가능성이 있는 유형이다.

- 도구: ChatGPT 웹 편집 화면, 기준 이미지 버전에서 각각 분기.
- 마스크: `mask_center_building.png` (중앙 동 전체). 이 케이스에서는 **마스크 밖의 구조 변경**(다른 동 매스·층수)과 **마스크 안의 구조 변경**(중앙 동 층수·형태)을 모두 확인한다. 톤 변화는 허용.

## 06a. 구조 프롬프트

```text
Goal: make the CENTER building (the one with the glass curtain-wall strip) read as the main subject, using tone and saturation only.

Keep all geometry fixed: the three building masses, their floor counts, the tilted right tower, the pilotis, balconies and windows, the roads, trees, surrounding houses, mountains and the camera position and framing.

Change only: the center building becomes slightly brighter and more saturated, with a touch more contrast so its facade reads crisply. Everything else, including the left slab block and the right tower, becomes about 30 percent less saturated and slightly softer, like a shallow depth-of-field falloff, but stays fully recognizable. The sky and lighting direction stay the same.

Do not enlarge, move or reshape any building. Do not blur the center building. Do not add people, cars, signs or text.
```

## 06b. 한 줄 프롬프트

```text
Make the center building stand out.
```

## 확인할 것

- 매스·층수·카메라 유지 (양쪽)
- 한 줄 프롬프트가 건물을 키우거나 색을 바꾸거나 조명을 극단적으로 바꾸는지
- 주변 채도 감소가 적용됐는지, 중앙 동이 흐려지지 않았는지
- report.jpg의 구조 윤곽 일치와 마스크 밖 구조 변경을 나란히 비교
