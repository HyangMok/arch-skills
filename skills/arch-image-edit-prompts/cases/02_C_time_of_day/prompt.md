# 케이스 02. 유형 C 배경·시간대 교체

기준 이미지에서 **건물은 그대로 두고 시간대만 일몰 직후(블루 아워)로** 바꾼다. 실내 조명 점등. 카메라·매스·재질·주변 배치 유지.

- 도구: ChatGPT 웹 편집 화면. 버전 썸네일에서 기준 이미지(첫 버전)를 선택한 뒤 편집 지시 입력. 업로드 없음.

## 프롬프트

```text
Keep the three buildings pixel-identical: same masses, same floor counts, same tilted right tower, same light grey stone panels and glass curtain-wall strip, same balconies, same pilotis columns. Keep the camera position, angle and framing exactly as they are. Keep the layout of roads, trees, surrounding houses and the mountain ridge.

Change only the time of day: it is now just after sunset (blue hour). Deep blue sky with a faint orange band low on the left horizon, no sun disc. Interior lights are on in most apartments and in the pilotis lobbies, warm white. Street lamps along the road are lit. Shadows are soft and the overall exposure is darker but the buildings remain clearly readable.

Do not add people, cars, signs or text. Do not change any building geometry or material. Do not move the camera.
```

## 확인할 것

- 윤곽 겹침으로 카메라·매스 유지 (report.jpg 윤곽 일치율을 케이스 A와 비교)
- 층수 12 / 12 / 8 유지, 타워 기울기 유지
- 재질이 바뀌지 않았는가 (조명 변화와 재질 변화의 구분)
- 요청하지 않은 요소(사람·차·간판) 추가 여부
