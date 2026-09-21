# 케이스 05. 케이스 01 재실행 (재현성)

입력은 `00_capture/capture.png`(가상 매스 뷰포트 캡처). 목표는 이 매스의 형태·층수·카메라를 그대로 둔 사실적 외관 렌더. 참고 렌더 없이 재질과 분위기를 글로 지정한다.

- 도구: ChatGPT 웹, 새 대화, `00_capture/capture.png` 첨부. 프롬프트는 케이스 01과 글자 하나 다르지 않다. 층수 오차의 방향(판상형 감소, 타워 증가)과 C 이음선이 반복되는지 본다.
- 정답(spec.json): A 15층 판상형, B 12층 판상형(필로티 2층), C 10층 L자형, D 20층 타워. 층고 3.1m. 카메라 남서쪽 상공.

## 프롬프트

```text
The attached image is a 3D massing capture from a modeling viewport: grey boxes with black outlines, one horizontal line per floor, a grid ground, a site boundary line and two grey road strips. It is the geometric reference. Produce a photorealistic architectural rendering of exactly this scene.

Keep fixed, exactly as in the capture:
- The camera position, height, angle and framing. Every building corner and the site boundary stay where they are in the frame.
- Four buildings and their proportions. Floor counts are the number of horizontal lines: front long slab 15 floors; rear right slab 12 floors standing on a 2-storey open pilotis with columns; left L-shaped block 10 floors (its two wings are one building); rear tower 20 floors.
- The site boundary and the two roads (south edge and east edge).

Render as:
- Residential buildings. Facades: light grey-beige stone panels with regular window bands and slim balconies; the tower gets a slightly darker tone with vertical mullions. No curtain walls unless implied by the massing.
- Flat roofs with low parapets and a few small rooftop units; no roof gardens.
- Ground: paved courtyards between buildings, low planting and street trees along the roads, asphalt roads with lane markings. Beyond the site: low-rise city fabric and distant hills.
- Late afternoon sun from the upper left, clear sky, soft shadows.

Do not add or remove buildings. Do not change any floor count. Do not tilt, taper or reshape a mass. Do not add text, signs, logos, people in the foreground or vehicles on the site.
```

## 확인할 것

- 층수: 렌더에서 동별 창 띠를 세어 15 / 12 / 10 / 20과 대조 (count_floors + 육안)
- 카메라: 캡처 윤곽(capture_edges.png)을 렌더 위에 겹쳐 모서리 일치 확인
- 필로티: B 동 하부 2층 개방 유지
- L자형 C가 한 동으로 표현됐는가, 두 동으로 갈라졌는가
- 추가·삭제된 매스, 글자·간판·차량
