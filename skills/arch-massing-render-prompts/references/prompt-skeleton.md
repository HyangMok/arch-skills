# 프롬프트 뼈대

다섯 구획을 순서대로 쓴다. 최종본은 영어. 층수·필로티는 위치 말과 숫자를 묶어 한 문장씩.

## 1. 역할 선언

첨부가 무엇인지, 결과가 무엇인지 첫 문장에 쓴다.

```
The attached image is a 3D massing capture from a modeling viewport: grey boxes with black
outlines, one horizontal line per floor, a grid ground, a site boundary line and grey road strips.
It is the geometric reference. Produce a photorealistic architectural rendering of exactly this scene.
```

참고 렌더를 함께 붙이면: `Image 1 is the massing to render. Image 2 is a mood reference only: take its materials, light and sky, not its buildings or camera.`

## 2. 고정 목록

```
Keep fixed, exactly as in the capture:
- The camera position, height, angle and framing. Every building corner and the site boundary
  stay where they are in the frame.
- <N> buildings and their proportions. Floor counts are the number of horizontal lines:
  <position> <type> <n> floors; <position> <type> <n> floors standing on a <k>-storey open pilotis
  with columns; <position> L-shaped block <n> floors (its two wings are one building); ...
- The site boundary and the roads (<which edges>).
```

## 3. 렌더 지시

```
Render as:
- <Use>. Facades: <material, window pattern, balconies>; <which building> gets <variation>.
- <Roof: flat with low parapets and a few small rooftop units / ...>.
- Ground: <courtyards, planting, street trees>, asphalt roads with lane markings.
  Beyond the site: <low-rise city fabric / open fields / ...> and <hills / sea / ...>.
- <Time of day, sun direction, sky, shadow softness>.
```

## 4. 금지 목록

```
Do not add or remove buildings. Do not change any floor count. Do not tilt, taper or reshape a mass.
Do not add text, signs, logos, people in the foreground or vehicles on the site.
```

모델이 습관적으로 넣는 것(횡단보도, 가로등, 차량, 간판, 한글·영문 문구)을 알면 여기에 더한다.

## 5. 확인 문장 (선택)

`Before finishing, check that each building has the stated floor count and that no building corner moved.` 효과는 미시험이며 있어도 대조는 생략하지 않는다.

## 실행 기록의 프롬프트

`evidence/arch-massing-render-prompts/01_B_structured/prompt.md`에 위 뼈대를 채운 실제 프롬프트와 결과 대조가 있다. 카메라·배치·필로티·재질·금지 항목은 지켜졌고 층수는 지켜지지 않았다.
