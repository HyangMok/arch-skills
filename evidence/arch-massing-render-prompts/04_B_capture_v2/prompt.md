# 케이스 04. 캡처 v2 + 구조 프롬프트 v2 (캡처 대책 시험)

케이스 01·02에서 층수 지시가 지켜지지 않았고(A −1~2, D +2~5), L자 한 동이 두 동처럼 그려졌다. 캡처 쪽 대책 네 가지를 `00_capture/capture_v2.png`에 넣고 프롬프트에 대응 문장을 더한다. 대책이 동마다 다르므로 결과를 동별로 가른다.

| 대책 | 대상 | 보는 것 |
|---|---|---|
| 층 분절선 3px 진회색 | 전 동 | 판상형 A·B 층수 부족이 줄어드는가 |
| 지붕 위 층수 라벨 "15F" 등 | 전 동 | 층수 정확도. 라벨이 렌더에 글자로 남는가 |
| C를 L자 한 덩어리로 | C | 이음선 없이 한 동으로 그려지는가 |
| 타워 지붕에 옥탑 박스 | D | 지붕선이 윤곽에 붙는가(층수 초과 감소) |

- 도구: ChatGPT 웹, 새 대화, 첨부 1장(capture_v2.png). 정답은 v1과 같다: A 15, B 12(필로티 2), C 10 L자 한 동, D 20 + 옥탑.

## 프롬프트

```text
The attached image is a 3D massing capture from a modeling viewport: grey volumes with black outlines, one dark horizontal line per floor, a grid ground, a site boundary line and two grey road strips. The white boxes with text like "15F" are floor-count labels for you to read; they are instructions, not objects, and must not appear in the rendering. Produce a photorealistic architectural rendering of exactly this scene.

Keep fixed, exactly as in the capture:
- The camera position, height, angle and framing. Every building corner, roof line and the site boundary stay where they are in the frame.
- Four buildings. Each building has exactly as many floors as its label says and as many window rows as drawn horizontal lines: one window row per drawn line, no more, no fewer. Front long slab 15 floors; rear right slab 12 floors standing on a 2-storey open pilotis with columns; left L-shaped building 10 floors, one continuous building with one continuous facade; rear tower 20 floors, with the small box on its roof being a rooftop machine room, not a floor. The tower roof parapet is at the top drawn line.
- The site boundary and the two roads (south edge and east edge).

Render as:
- Residential buildings. Facades: light grey-beige stone panels with regular window bands and slim balconies; the tower gets a slightly darker tone with vertical mullions. No curtain walls.
- Flat roofs with low parapets and a few small rooftop units; no roof gardens.
- Ground: paved courtyards between buildings, low planting and street trees along the roads, asphalt roads with lane markings. Beyond the site: low-rise city fabric and distant hills.
- Late afternoon sun from the upper left, clear sky, soft shadows.

Do not add or remove buildings. Do not change any floor count or building height. Do not tilt, taper or reshape a mass. Do not render the labels or any text, signs, logos, people in the foreground or vehicles on the site.
```

## 확인할 것

- 동별 층수와 지붕 높이(윤곽 겹침): v1 결과(01/05)와 비교
- C 이음선 유무
- 라벨이 글자로 남았는가
- 카메라, 필로티, 추가·삭제 매스
