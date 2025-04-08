from __future__ import annotations
import os
import time
import yaml
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pdfkit
import PyPDF2
import sys
import platform
import subprocess
import re
import urllib.request
import zipfile
import shutil

def download_wkhtmltopdf():
    """wkhtmltopdf 다운로드 및 설치"""
    try:
        # Windows용 wkhtmltopdf 다운로드 URL
        wkhtmltopdf_url = "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe"
        installer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wkhtmltopdf_installer.exe")
        
        print("wkhtmltopdf 다운로드 중...")
        urllib.request.urlretrieve(wkhtmltopdf_url, installer_path)
        
        print("wkhtmltopdf 설치 중...")
        # 자동 설치 실행 (/S는 자동 설치 옵션)
        subprocess.run([installer_path, '/S'], check=True)
        
        # 설치 파일 삭제
        os.remove(installer_path)
        
        # 환경 변수 PATH에 wkhtmltopdf 경로 추가
        wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin"
        if wkhtmltopdf_path not in os.environ['PATH']:
            os.environ['PATH'] = wkhtmltopdf_path + os.pathsep + os.environ['PATH']
        
        return True
    except Exception as e:
        print(f"wkhtmltopdf 설치 중 오류 발생: {str(e)}")
        return False

def check_wkhtmltopdf():
    """wkhtmltopdf가 설치되어 있는지 확인하고 설치"""
    try:
        # wkhtmltopdf 실행 파일 경로 확인
        if platform.system() == 'Windows':
            wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            if not os.path.exists(wkhtmltopdf_path):
                print("wkhtmltopdf가 설치되어 있지 않습니다. 설치를 시작합니다...")
                if not download_wkhtmltopdf():
                    raise Exception("wkhtmltopdf 설치 실패")
            return {'wkhtmltopdf': wkhtmltopdf_path}
        else:
            # Linux/Mac의 경우 시스템에 설치된 wkhtmltopdf 사용
            return None
    except Exception as e:
        print(f"wkhtmltopdf 확인 중 오류 발생: {str(e)}")
        return None

def get_chrome_version():
    """현재 설치된 Chrome 버전을 확인"""
    try:
        if platform.system() == 'Windows':
            # Windows에서 Chrome 버전 확인
            try:
                # 레지스트리에서 버전 확인 시도
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version = winreg.QueryValueEx(key, "version")[0]
                winreg.CloseKey(key)
                return version
            except:
                # 실행 파일에서 버전 확인
                paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                for path in paths:
                    if os.path.exists(path):
                        version = subprocess.check_output(f'wmic datafile where name="{path}" get Version /value', shell=True)
                        version = re.search(r"Version=(.+)", version.decode()).group(1).strip()
                        return version
        return None
    except Exception as e:
        print(f"Chrome 버전 확인 중 오류 발생: {str(e)}")
        return None

def download_chromedriver(version):
    """Chrome 버전에 맞는 WebDriver 다운로드"""
    try:
        # Chrome 버전의 주 버전 번호 추출 (예: 120.0.6099.109 -> 120)
        major_version = version.split('.')[0]
        
        # 운영체제에 맞는 드라이버 선택
        if platform.system() == 'Windows':
            platform_name = 'win32'
        elif platform.system() == 'Darwin':
            platform_name = 'mac64'
        else:
            platform_name = 'linux64'
        
        # 드라이버를 저장할 디렉토리 생성
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')
        os.makedirs(driver_dir, exist_ok=True)
        
        # zip 파일 경로
        zip_path = os.path.join(driver_dir, 'chromedriver.zip')
        
        # Chrome for Testing 다운로드 URL
        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win32/chromedriver-win32.zip"
        
        try:
            print(f"ChromeDriver 다운로드 중... 버전: {version}")
            urllib.request.urlretrieve(download_url, zip_path)
            
            # zip 파일 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
            # zip 파일 삭제
            os.remove(zip_path)
            
            # 드라이버 실행 파일 경로
            if platform.system() == 'Windows':
                driver_path = os.path.join(driver_dir, 'chromedriver-win32', 'chromedriver.exe')
            else:
                driver_path = os.path.join(driver_dir, f'chromedriver-{platform_name}', 'chromedriver')
                os.chmod(driver_path, 0o755)
            
            if not os.path.exists(driver_path):
                raise Exception(f"ChromeDriver 실행 파일을 찾을 수 없습니다: {driver_path}")
            
            return driver_path
            
        except Exception as e:
            print(f"ChromeDriver 다운로드 실패: {str(e)}")
            
            # 대체 URL 시도
            try:
                # 대체 URL 형식으로 시도
                alt_download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/{platform_name}/chromedriver-{platform_name}.zip"
                print("대체 URL에서 다운로드 시도...")
                urllib.request.urlretrieve(alt_download_url, zip_path)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(driver_dir)
                
                os.remove(zip_path)
                
                if platform.system() == 'Windows':
                    driver_path = os.path.join(driver_dir, 'chromedriver-win32', 'chromedriver.exe')
                else:
                    driver_path = os.path.join(driver_dir, f'chromedriver-{platform_name}', 'chromedriver')
                    os.chmod(driver_path, 0o755)
                
                if not os.path.exists(driver_path):
                    raise Exception(f"ChromeDriver 실행 파일을 찾을 수 없습니다: {driver_path}")
                
                return driver_path
                
            except Exception as e2:
                print(f"대체 URL에서도 다운로드 실패: {str(e2)}")
                
                # 세 번째 URL 형식 시도
                try:
                    third_download_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
                    response = urllib.request.urlopen(third_download_url)
                    driver_version = response.read().decode('utf-8').strip()
                    final_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_{platform_name}.zip"
                    
                    print("세 번째 URL에서 다운로드 시도...")
                    urllib.request.urlretrieve(final_url, zip_path)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(driver_dir)
                    
                    os.remove(zip_path)
                    
                    if platform.system() == 'Windows':
                        driver_path = os.path.join(driver_dir, 'chromedriver.exe')
                    else:
                        driver_path = os.path.join(driver_dir, 'chromedriver')
                        os.chmod(driver_path, 0o755)
                    
                    if not os.path.exists(driver_path):
                        raise Exception(f"ChromeDriver 실행 파일을 찾을 수 없습니다: {driver_path}")
                    
                    return driver_path
                    
                except Exception as e3:
                    print(f"모든 다운로드 시도 실패: {str(e3)}")
                    return None
                
    except Exception as e:
        print(f"ChromeDriver 다운로드 중 오류 발생: {str(e)}")
        return None

def setup_driver():
    """웹드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    try:
        # Chrome 버전 확인
        chrome_version = get_chrome_version()
        if not chrome_version:
            raise Exception("Chrome 브라우저를 찾을 수 없습니다.")
        
        # ChromeDriver 다운로드
        driver_path = download_chromedriver(chrome_version)
        if not driver_path:
            raise Exception("ChromeDriver 다운로드에 실패했습니다.")
        
        # Windows 환경에서 추가 설정
        if platform.system() == 'Windows':
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            if not os.path.exists(chrome_options.binary_location):
                chrome_options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        
        # WebDriver 서비스 생성 및 드라이버 초기화
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
        
    except Exception as e:
        print(f"Chrome 드라이버 설정 중 오류 발생: {str(e)}")
        print("\n문제 해결 방법:")
        print("1. Chrome 브라우저가 설치되어 있는지 확인해주세요.")
        print("2. Chrome 브라우저를 최신 버전으로 업데이트해주세요.")
        print("3. 관리자 권한으로 프로그램을 실행해보세요.")
        print("4. 안티바이러스 프로그램이 Chrome WebDriver를 차단하고 있는지 확인해주세요.")
        sys.exit(1)

def get_article_content(url, driver):
    """URL에서 article 태그 내용 추출"""
    try:
        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기 시간 증가
        
        # article 태그가 로드될 때까지 대기
        article = WebDriverWait(driver, 20).until(  # 대기 시간 증가
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # article 내용 가져오기
        html_content = article.get_attribute('outerHTML')
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 스타일 추가
        style = """
        <style>
            body { font-family: Arial, sans-serif; }
            article { max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #333; }
            p { line-height: 1.6; }
            code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background-color: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
            img { max-width: 100%; height: auto; }
        </style>
        """
        
        return f"<html><head>{style}</head><body>{str(soup)}</body></html>"
    except Exception as e:
        print(f"페이지 내용 추출 중 에러 발생: {str(e)}")
        return None

def save_as_pdf(html_content, output_path):
    """HTML 내용을 PDF로 저장"""
    try:
        # wkhtmltopdf 설정 확인
        config = check_wkhtmltopdf()
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'quiet': ''
        }
        
        # Windows에서는 설정된 경로 사용
        if config:
            pdfkit.from_string(html_content, output_path, options=options, configuration=pdfkit.configuration(**config))
        else:
            pdfkit.from_string(html_content, output_path, options=options)
        
        return True
    except Exception as e:
        print(f"PDF 저장 중 에러 발생: {str(e)}")
        print("문제 해결 방법:")
        print("1. wkhtmltopdf를 수동으로 설치: https://wkhtmltopdf.org/downloads.html")
        print("2. 설치 후 시스템 환경 변수 PATH에 설치 경로 추가")
        print("3. 프로그램을 다시 실행")
        return False

def merge_pdfs(pdf_files, output_path):
    """여러 PDF 파일을 하나로 병합"""
    merger = PyPDF2.PdfMerger()
    
    for pdf in pdf_files:
        if os.path.exists(pdf):
            merger.append(pdf)
    
    merger.write(output_path)
    merger.close()

def load_config(config_file='pages.yml'):
    """YAML 설정 파일 로드"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"설정 파일 로드 중 에러 발생: {str(e)}")
        return None

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='웹사이트의 article 태그 내용을 PDF로 변환합니다.'
    )
    parser.add_argument(
        '-c', '--config',
        default='pages.yml',
        help='YAML 설정 파일 경로 (기본값: pages.yml)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='output_pdfs',
        help='PDF 파일이 저장될 디렉토리 (기본값: output_pdfs)'
    )
    parser.add_argument(
        '--merged-filename',
        default='merged_nextjs_docs.pdf',
        help='병합된 PDF 파일 이름 (기본값: merged_nextjs_docs.pdf)'
    )
    return parser.parse_args()

def main():
    # 명령줄 인자 파싱
    args = parse_arguments()
    
    # YAML 설정 파일 로드
    config = load_config(args.config)
    if not config:
        print(f"설정 파일을 로드할 수 없습니다: {args.config}")
        return
    
    base_url = config['base_url']
    pages = config['pages']
    
    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 웹드라이버 설정
    driver = setup_driver()
    pdf_files = []
    
    try:
        for page in pages:
            url = base_url + page
            page_name = page.replace("/", "_") if page else "main"
            output_path = os.path.join(args.output_dir, f"{page_name}.pdf")
            
            print(f"처리 중: {url}")
            
            # 페이지 내용 가져오기
            html_content = get_article_content(url, driver)
            
            if html_content:
                # PDF로 저장
                if save_as_pdf(html_content, output_path):
                    pdf_files.append(output_path)
                    print(f"PDF 저장 완료: {output_path}")
                else:
                    print(f"PDF 저장 실패: {url}")
        
        # PDF 파일들 병합
        if pdf_files:
            merged_pdf_path = os.path.join(args.output_dir, args.merged_filename)
            merge_pdfs(pdf_files, merged_pdf_path)
            print(f"PDF 병합 완료: {merged_pdf_path}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 