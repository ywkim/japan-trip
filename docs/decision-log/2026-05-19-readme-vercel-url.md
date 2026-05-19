# 2026-05-19 — README에 Vercel 배포 URL 명시

- 합의: 모바일·웹 배포 URL `https://nihon-trip.vercel.app`를 README 사용법 §1 상단에 명시
- 변경: `README.md` "확정 정보 보기" 섹션 첫 줄에 배포 URL 1줄 추가
- 산출물: `README.md`
- 핵심 관찰:
  - Vercel 프로젝트(`alola/japan-trip`)에 4개 production alias가 붙어 있음 — `nihon-trip.vercel.app`, `japan-trip-alola.vercel.app`, `japan-trip-git-main-alola.vercel.app`, `japan-trip-rust.vercel.app`
  - 그 중 가장 짧고 기억하기 쉬운 `nihon-trip.vercel.app`을 정규 URL로 채택
  - 기존 README·CLAUDE.md에 "Vercel 호스팅" 언급은 있었으나 실제 URL은 미기재 상태였음
- 다음 단계: 커스텀 도메인 부착 시 README·CLAUDE.md 동기화
- META: 본 PR은 단일 메타 갱신(README) — `CLAUDE.md` 디렉토리 트리·작업 패턴 변경 없음
