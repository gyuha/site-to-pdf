from __future__ import annotations
import os
import re
import yaml
import argparse
from bs4 import BeautifulSoup

def parse_menu_file(menu_file):
    """menu.html 파일에서 href 속성을 추출"""
    try:
        with open(menu_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(content, 'html.parser')
        
        # 모든 href 속성을 가진 a 태그 찾기
        links = soup.find_all('a', href=True)
        
        # href 값 추출 (중복 제거하되 순서 유지)
        hrefs = []
        seen = set()  # 중복 체크를 위한 set
        for link in links:
            href = link['href']
            # 외부 링크 제외
            if not href.startswith(('http://', 'https://', '#', 'mailto:')):
                # 앞에 /docs가 있으면 제거
                href = href.replace('/docs', '')
                if href and href not in seen:
                    hrefs.append(href)
                    seen.add(href)
        
        return hrefs  # 원래 순서 유지
        
    except Exception as e:
        print(f"메뉴 파일 파싱 중 오류 발생: {str(e)}")
        return None

def save_yaml_file(hrefs, output_file):
    """추출된 href 목록을 YAML 파일로 저장"""
    try:
        yaml_content = {
            'base_url': 'https://nextjs-ko.org/docs',
            'pages': hrefs
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True, sort_keys=False)
        
        return True
    except Exception as e:
        print(f"YAML 파일 저장 중 오류 발생: {str(e)}")
        return False

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='menu.html 파일에서 href 속성을 추출하여 YAML 파일을 생성합니다.'
    )
    parser.add_argument(
        '-i', '--input',
        default='menu.html',
        help='입력 HTML 파일 경로 (기본값: menu.html)'
    )
    parser.add_argument(
        '-o', '--output',
        default='nextjs15ko.yml',
        help='출력 YAML 파일 경로 (기본값: nextjs15ko.yml)'
    )
    return parser.parse_args()

def main():
    # 명령줄 인자 파싱
    args = parse_arguments()
    
    # 입력 파일 존재 확인
    if not os.path.exists(args.input):
        print(f"입력 파일을 찾을 수 없습니다: {args.input}")
        return
    
    # href 속성 추출
    hrefs = parse_menu_file(args.input)
    if not hrefs:
        print("href 속성을 추출할 수 없습니다.")
        return
    
    # YAML 파일 저장
    if save_yaml_file(hrefs, args.output):
        print(f"YAML 파일이 생성되었습니다: {args.output}")
        print(f"총 {len(hrefs)}개의 페이지가 추가되었습니다.")
    else:
        print("YAML 파일 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
