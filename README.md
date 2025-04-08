# Site to PDF 변환기

이 프로그램은 Next.js 한글 문서 웹사이트의 article 태그 내용을 PDF로 변환하는 도구입니다.

## 필수 요구사항

1. Python 3.7 이상
2. Chrome 브라우저 (최신 버전 권장)
3. wkhtmltopdf (PDF 변환을 위해 필요)

## Chrome 브라우저 설치

1. [Chrome 다운로드 페이지](https://www.google.com/chrome/)에서 Chrome 브라우저를 다운로드하여 설치합니다.
2. 설치 후 Chrome 브라우저를 실행하여 최신 버전으로 업데이트합니다.

## wkhtmltopdf 설치 방법

### Windows
1. [wkhtmltopdf 다운로드 페이지](https://wkhtmltopdf.org/downloads.html)에서 Windows 버전을 다운로드
2. 설치 파일을 실행하여 설치
3. 설치 후 시스템 환경 변수 Path에 설치 경로 추가 (일반적으로 `C:\Program Files\wkhtmltopdf\bin`)

### macOS
```bash
brew install wkhtmltopdf
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install wkhtmltopdf
```

## 설치 방법

1. 필요한 Python 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

1. `pages.yml` 파일에서 변환하고 싶은 페이지 목록을 설정합니다:
```yaml
base_url: https://nextjs-ko.org/docs
pages:
  - ""  # 메인 페이지
  - /app/building-your-application/routing
  - /your/additional/page/path  # 추가 페이지
```

2. 프로그램 실행:

기본 설정으로 실행:
```bash
python site_to_pdf.py
```

다른 YAML 파일 사용:
```bash
python site_to_pdf.py -c other_pages.yml
```

출력 디렉토리 변경:
```bash
python site_to_pdf.py -o my_pdfs
```

병합된 PDF 파일 이름 변경:
```bash
python site_to_pdf.py --merged-filename nextjs_documentation.pdf
```

모든 옵션 사용:
```bash
python site_to_pdf.py -c other_pages.yml -o my_pdfs --merged-filename nextjs_documentation.pdf
```

### 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-c, --config` | YAML 설정 파일 경로 | `pages.yml` |
| `-o, --output-dir` | PDF 파일이 저장될 디렉토리 | `output_pdfs` |
| `--merged-filename` | 병합된 PDF 파일 이름 | `merged_nextjs_docs.pdf` |

## 작동 방식

1. 프로그램이 실행되면 다음 작업을 수행합니다:
   - 설치된 Chrome 브라우저 버전을 확인
   - 해당 버전에 맞는 ChromeDriver를 자동으로 다운로드
   - 지정된 URL의 페이지들을 방문
   - 각 페이지의 article 태그 내용을 추출
   - 내용을 PDF로 변환
   - 모든 PDF를 하나의 파일로 병합

2. 변환된 PDF 파일은 지정된 출력 디렉토리에 저장됩니다:
   - 개별 페이지: `[출력 디렉토리]/[페이지명].pdf`
   - 병합된 파일: `[출력 디렉토리]/[병합된 파일 이름]`

## 문제 해결

프로그램 실행 시 오류가 발생하는 경우:

1. Chrome 브라우저가 설치되어 있고 최신 버전인지 확인
2. 관리자 권한으로 프로그램 실행
3. 안티바이러스 프로그램이 ChromeDriver를 차단하고 있는지 확인
4. 시스템을 재시작한 후 다시 시도

## 페이지 목록 설정

`pages.yml` 파일을 수정하여 원하는 페이지를 추가하거나 제거할 수 있습니다. 파일 형식은 다음과 같습니다:

```yaml
base_url: https://nextjs-ko.org/docs  # 기본 URL
pages:  # 변환할 페이지 목록
  - ""  # 메인 페이지 (빈 문자열은 기본 URL만 사용)
  - /app/building-your-application/routing
  - /app/building-your-application/data-fetching
  - /app/building-your-application/rendering
  # 원하는 만큼 페이지 추가 가능
```