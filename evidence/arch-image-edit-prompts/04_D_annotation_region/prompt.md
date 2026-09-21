# 케이스 04. 유형 D 주석 이미지 국소 수정

기준 이미지에서 **우측 기울어진 타워의 상부 3개층 외장만** 짙은 차콜색 금속 패널로 바꾼다. 수정 영역은 별도 주석 이미지(빨간 윤곽 + 라벨)로 지정한다. 주석 색을 실제 색으로 칠하는 실패, 영역 밖으로 재질이 번지는 실패, 층수·기울기 변형을 시험한다.

- 도구: ChatGPT 웹 편집 화면. 기준 이미지 버전 선택 → **마크업 도구로 빨간 사각형을 직접 그림** → 지침 입력.
- 원래 계획은 별도 주석 이미지(`annotation.jpg`) 첨부였으나, 파일 첨부를 쓸 수 없는 환경이어서 편집기 내장 마크업으로 대체했다. `annotation.jpg`는 별도 첨부 방식으로 재시험할 때 쓴다.
- 마스크: `mask_top3.png` (마크업 사각형과 같은 영역)

## 프롬프트 (마크업 사각형과 함께 입력)

```text
The red rectangle I drew marks the EDIT REGION only: the top 3 floors of the right-hand tilted tower. Red is not a color to apply anywhere, and the rectangle itself must not appear in the result.

Inside the region only: replace the light grey stone cladding with dark charcoal metal panels, matte, with thin horizontal panel joints. Windows, balconies and railings inside the region stay as they are.

Everything outside the region stays identical: the lower floors of the same tower keep light grey stone, the tower keeps its tilt and its floor count, the other two buildings, pilotis, trees, roads, mountains, sky and the camera do not change. Do not add signs, text, people or cars.
```

## 별도 주석 이미지를 첨부할 때의 프롬프트 (미실행)

```text
Two images. Image 1 is the ORIGINAL to edit. Image 2 is an ANNOTATION copy of the same view: the red outline and label mark the edit region only. Red is not a color to apply anywhere. Do not draw the outline or the label in the result.
Edit region: the top 3 floors of the right-hand tilted tower, exactly the area inside the red outline.
(이하 동일)
```

## 확인할 것

- 결과에 빨간 윤곽·라벨이 그려졌는가 (주석 색 오해)
- 차콜 패널이 상부 3개층에만 있는가, 아래층으로 번졌는가 (마스크 밖 구조 변경)
- 타워 기울기·층수 유지
- 다른 두 동 변화 없음
