# 2026-05-17 · 장소·메뉴 이미지 추가

## 산출물

- `data/itinerary.json` — 9개 항목에 `image_url` + `image_credit` 필드 추가
- `viz/itinerary.html` (카드 뷰) — 이미지 렌더링 추가
- `viz/itinerary-table.html` (시간표 뷰) — 이미지 렌더링 추가
- `scripts/build_index.py` — `place-img` CSS + 이미지 렌더링 로직

## 이미지 출처

모든 이미지: **Wikimedia Commons** (CC 라이선스, 안정적 CDN URL)

| 장소 | 파일명 |
|---|---|
| 키요미즈데라 | Kyoto-Kiyomizu_Temple-2.JPG |
| 기온 야경 | JP-Kyoto-Gion-Area-Traditional-House-Night-View.JPG |
| 아라시야마 죽림길 | Sagano_Bamboo_forest,_Arashiyama,_Kyoto.jpg |
| 텐류지 정원 | Tenryuji,_Kyoto-_DSC06041.JPG |
| 두부 요리 (두부 가이세키) | Japanese_SilkyTofu_(Kinugoshi_Tofu).JPG |
| 금각사 | Kinkaku-ji_the_Golden_Temple_in_Kyoto_overlooking_the_lake_-_high_rez.JPG |
| 료안지 석정원 | RyoanJi-Dry_garden.jpg |
| 니시키 시장 | Nishiki_ichiba_kyoto.jpg |
| 후시미 이나리 | Torii_gates—Fushimi_Inari_Shrine_(9977683204).jpg |
| 토후쿠지 | Sand_Garden_at_Tofukuji_Temple.jpg |

- URL 구조: `upload.wikimedia.org/wikipedia/commons/thumb/[MD5해시]/480px-...`
- MD5 해시는 파일명에서 계산 (Python hashlib 검증)
- Kinkakuji URL은 WebSearch에서 직접 확인하여 일치 검증

## 미포함 이유

- 시오 에어비앤비·카덴쇼 료칸: 공식 숙소 이미지 URL이 403 차단 또는 CDN 불안정 → 링크 제공으로 대체
- 라멘코지·교토역: 이미지 불필요

## 다음 단계

- 이미지 로드 확인 후 오류 발생 파일명은 교체
