# 케이스 05. 유형 F 반복 모듈 서술

기준 이미지의 **좌측 판상형 동 정면**에 기울어진 수직 프레임 모듈을 추가한다. 모델이 자주 틀리는 반복 규칙(교대로 기울어진 삼각형·역삼각형 프레임)을 그림 없이 **왼쪽 첫 단위부터 순서대로 말로** 지시한다. 시험 대상: 모듈 규칙 준수, 다른 동으로 번짐, 층수·매스 유지.

- 도구: ChatGPT 웹 편집 화면, 기준 이미지 버전에서 분기. 첨부·마크업 없음.
- 마스크: `mask_left_front.png` (좌측 동 정면 상부)

## 프롬프트

```text
Edit only the front facade of the LEFT slab block (the 12-storey building on the left). Add dark bronze vertical fins in front of the facade, running the full height of the upper floors above the pilotis. Do not touch the pilotis, the roof line, the side facade, or the other two buildings.

The fins follow one repeating module, described from the leftmost fin to the right:
1. Fin 1 leans outward at the top: it projects about 60 cm from the wall at the top and touches the wall at the bottom. Seen from the side it is a tall thin triangle.
2. After a gap of about 1.8 m, fin 2 is the mirror: it projects at the bottom and touches the wall at the top. An inverted triangle.
3. Fins 1 and 2 alternate across the whole facade with the same 1.8 m gap. The last fin ends at the facade corner; do not cut a fin in half.
All fins have the same dark bronze color and the same thickness of about 15 cm. Balconies and windows behind the fins stay visible between them.

Keep the camera, floor count, massing, materials of all other surfaces, trees, roads, mountains and sky exactly as they are. Do not add signs, text, people or cars.
```

## 확인할 것

- 프레임이 교대로 기울어졌는가, 아니면 모두 같은 방향이거나 수직인가
- 프레임 간격이 일정한가, 끝단에 잘린 프레임이 있는가
- 필로티·옥상·측면·다른 동으로 번졌는가
- 층수·매스·카메라 유지
