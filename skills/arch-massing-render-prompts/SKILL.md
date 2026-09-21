---
name: arch-massing-render-prompts
description: Turn a 3D massing viewport capture (grey boxes from Rhino, SketchUp, Revit, or any modeler) into a photorealistic aerial or perspective rendering prompt while keeping camera, building layout, floor counts and pilotis, and check the result against the capture. Covers how to prepare the capture so the model reads it, how to write the fixed/render/forbidden lists, and how to verify with an outline overlay. Use for Korean requests like 매스 캡처 렌더링해줘, 조감도 뽑아줘, 뷰포트 캡처로 투시도, 층수 그대로 렌더, 매스 스터디 이미지 만들어줘, 렌더 결과 층수 확인. Not for editing part of an existing rendering (see arch-image-edit-prompts) and not for running the image model itself.
---

# 매스 캡처 → 렌더 프롬프트

모델링 뷰포트에서 찍은 **회색 매스 캡처**를 이미지 생성 모델에 넣어 카메라·배치·층수·필로티를 지킨 조감도나 투시도를 얻는 절차다. 결과물은 캡처 준비 지침, 프롬프트 본문, 생성 후 대조표다. 이미지 생성은 사용자가 쓰는 도구(ChatGPT 이미지, gpt-image API 등)에서 실행한다.

## 먼저 알아둘 것

실제 실행 기록([evidence](https://github.com/HyangMok/arch-skills/blob/main/evidence/arch-massing-render-prompts/README.md))에서 확인된 순서는 이렇다.

1. **카메라·배치·필로티는 캡처가 잡는다(5/5).** 한 줄 프롬프트로도 동 모서리·대지 경계·도로가 캡처 윤곽과 겹쳤고 필로티 기둥이 유지됐다. 텍스트로 시점을 길게 설명할 필요는 없고, 짧게 고정만 선언한다.
2. **형상은 캡처에서 고친다.** L자형 한 동을 두 박스로 그려 내부 모서리선이 남은 캡처에서는 "두 날개는 한 동"이라고 써도 4/4 두 동처럼 그려졌고, 한 덩어리로 그린 캡처에서는 1/1 한 동으로 나왔다. 텍스트는 형상을 이기지 못한다.
3. **층수는 어떤 방법으로도 정확히 맞지 않았다.** 판상형은 1~2층 줄고(A 13~15, B 10~12), 타워는 1~6층 늘었다. 방향은 재실행에서 재현됐다. 층수가 걸린 자료라면 생성 후 반드시 세고, 결과를 "층수 ±1~2" 자료로 취급한다.
4. **구조 프롬프트가 실제로 하는 일**: 재질·조명·주변·금지 항목을 지시대로 만들고(3/3), 타워가 늘어나는 정도를 줄인다(구조 +1~3, 한 줄 +4~6). 층수를 맞추는 것이 아니다.
5. **같은 대화의 이전 프롬프트가 다음 결과에 남는다.** 대조군이나 다른 안은 새 대화에서 만든다.

## 절차

### 1. 캡처 준비

[references/capture-prep.md](references/capture-prep.md)의 목록으로 캡처를 점검한다. 핵심: 면은 무채색, 윤곽선은 검게, **층마다 선 하나**, 필로티는 기둥 선까지, **한 동은 한 덩어리로**(내부 모서리선이 남으면 두 동으로 그려진다), 대지 경계와 도로는 캡처 안에, 배경은 비우고, 3:2 또는 16:9로 1536px 이상. 동별 층수 라벨("15F")을 지붕 위에 써 넣어도 렌더에 글자로 남지 않았다(1회, 지시 문장과 함께). 정답표(동별 층수·필로티·특이 형상)를 함께 적어 둔다. 이것이 생성 후 대조의 기준이다.

### 2. 프롬프트

[references/prompt-skeleton.md](references/prompt-skeleton.md)의 다섯 구획을 채운다. 순서는 **역할 선언 → 고정 목록(카메라·동 수·층수·필로티·대지) → 렌더 지시(용도·재질·지붕·지반·주변·조명) → 금지 목록 → 확인 문장**. 최종본은 영어로 쓴다. 층수는 "front long slab 15 floors"처럼 위치 말과 숫자를 묶고, 필로티는 "2-storey open pilotis with columns"처럼 높이와 요소를 함께 쓴다. 참고 렌더를 붙여 분위기를 옮기는 경우는 첫 줄에 이미지 번호별 역할을 선언한다.

한 줄 프롬프트로도 카메라는 유지되지만, 재질·조명·차량·글자가 모델 기본값으로 채워진다. 검토 자료로 쓸 렌더라면 금지 목록(글자·간판·로고·전경 인물·대지 안 차량)은 생략하지 않는다.

### 3. 생성 후 대조

[references/verification.md](references/verification.md)의 표를 채운다. `scripts/check_render.py`가 캡처 윤곽을 렌더 위에 빨갛게 겹친 `overlay.jpg`, 동별 확대 `overlay_zoom_*.jpg`, 캡처와 렌더의 입면 띠를 나란히 3배 확대한 `strip_*.jpg`를 만든다.

```bash
python scripts/check_render.py capture.png render.png --out check/ \
  --box A 540 340 960 820 --strip A 640 430 760 800
```

- 카메라: 겹침에서 동 모서리·지붕선·대지 경계가 빨간 선 위에 있으면 통과.
- 층수: `strip_*.jpg`에서 창 띠를 **눈으로** 센다. 사선 뷰에서 밝기 주기로 층수를 어림하는 스크립트는 캡처 자체에서도 어긋나므로 쓰지 않는다.
- 높이: 지붕선이 빨간 윤곽보다 위에 있으면 층수 초과(타워에서 흔함), 지붕은 맞는데 창 띠가 성기면 층수 부족(판상형에서 흔함).
- 필로티, 한 동 여부, 추가·삭제 매스, 글자·간판·차량.

### 4. 어긋났을 때

[references/failure-modes.md](references/failure-modes.md)에서 증상을 찾는다. 층수·형상 문제는 프롬프트를 고치기보다 캡처를 고쳐 **새 대화에서 다시 첨부**한다. 같은 대화에서 재생성을 반복하면 이전 지시가 문맥으로 남아 대조가 흐려진다.

## 실제 실행 기록

[evidence/arch-massing-render-prompts](https://github.com/HyangMok/arch-skills/blob/main/evidence/arch-massing-render-prompts/README.md): 가상 매스 4동(15/12+필로티/10 L자/20 타워)을 ChatGPT 웹에서 렌더 5건. 구조 프롬프트 2회(재현성), 한 줄 2회(같은 대화·새 대화), 캡처 대책 v2 1회. 전부 카메라·배치·필로티 통과. 층수는 판상형 −1~2, 타워 +1~6으로 어느 조건에서도 정확히 맞지 않았다. L자 한 동은 캡처를 한 덩어리로 그린 1회만 성공. 타워 옥탑 박스는 효과 없음(1회). 각 조건 1~2회이므로 승률이 아니라 경향이다. 주장 수위는 이 기록에 맞춘다.

## 관련 스킬

- `arch-image-edit-prompts`: 이미 있는 렌더의 일부만 바꾸는 편집. 렌더가 나온 뒤 재질·시간대·배경을 바꿀 때 그쪽으로 넘어간다.

## 하지 않는 것

- 매스 없이 글만으로 조감도를 만드는 프롬프트.
- 층수·형상 보존을 보장하는 것. 캡처와 프롬프트로 확률을 높이고 대조표로 걸러낼 뿐이다.
- 렌더 결과를 심의·협의 자료로 그대로 내는 것. 층수 대조를 통과한 뒤에도 치수 검증은 별도다.
