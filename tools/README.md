# 프로필 이미지 다시 만들기

`assets/`의 `*-light.svg`, `*-dark.svg`는 `editorial.py`가 만듭니다.
글자를 도형(path)으로 바꿔 넣기 때문에, 문구를 고치려면 스크립트를 수정하고 다시 실행해야 합니다.

## 1. 준비 (처음 한 번)

```bash
pip install fonttools
mkdir -p tools/fonts
for w in Light Regular Medium; do
  curl -sSfL -o tools/fonts/IBMPlexSansKR-$w.ttf \
    "https://github.com/google/fonts/raw/main/ofl/ibmplexsanskr/IBMPlexSansKR-$w.ttf"
done
```

글꼴 파일은 용량이 커서 저장소에 넣지 않습니다(`.gitignore`).
IBM Plex Sans KR은 SIL Open Font License 1.1로 배포됩니다.

## 2. 문구 수정

`editorial.py`에서 고칩니다.

- 이름·소개 문장·기술 스택: `hero()`
- 프로젝트 목록: `row(...)` 호출 (제목, 오른쪽 태그, 설명)
- 작업 흐름: `flow()`
- 색: 맨 위 `THEMES`

프로젝트를 추가하면 `README.md`에도 같은 이름의 `<picture>` 묶음을 추가합니다.

## 3. 생성

```bash
python tools/editorial.py tools/fonts assets
```
