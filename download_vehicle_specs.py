import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import validators
import re

def is_valid_url(url):
    """Check if the URL is valid"""
    return validators.url(url)

def get_filename_from_url(url):
    """Extract filename from URL"""
    parsed = urlparse(url)
    return os.path.basename(parsed.path) or 'downloaded_file.pdf'

def download_pdf(url, output_dir='downloads'):
    """
    Download a PDF file from a given URL and save it to the specified directory
    Only download if the file does not already exist.

    Args:
        url (str): URL of the PDF file to download
        output_dir (str): Directory to save the downloaded file
        
    Returns:
        str: Path to the downloaded file if successful, None otherwise
    """
    if not is_valid_url(url):
        print(f"Error: Invalid URL: {url}")
        return None
        
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the filename from URL
        filename = get_filename_from_url(url)
        filepath = os.path.join(output_dir, filename)
        # 新增：如果文件已存在则跳过下载
        if os.path.exists(filepath):
            print(f"File already exists, skip: {filepath}")
            return filepath

        # Download the file
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check if the response is a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type:
            print(f"Warning: URL {url} doesn't point to a PDF file")
            return None
        
        # Save the file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"Successfully downloaded: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def parse_vehicle_specs_from_html(html, base_url, output_dir='downloads'):
    """
    解析HTML，提取车辆名和PDF链接并下载PDF。
    Args:
        html (str): 包含车辆信息的HTML内容
        base_url (str): 用于拼接PDF完整URL的基础URL
        output_dir (str): PDF保存目录
    Returns:
        list: [(car_name, pdf_url, saved_path), ...]
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for li in soup.find_all('li'):
        name_div = li.find('div', class_='name')
        if not name_div:
            continue
        car_name = name_div.get_text(strip=True)
        pdf_a = li.find('a', href=True, class_='thumb_cell')
        if not pdf_a:
            # 兼容catalog_link下的主链接
            pdf_a = li.select_one('div.catalog_link a.main[href$=".pdf"]')
        if not pdf_a:
            continue
        pdf_url = urljoin(base_url, pdf_a['href'])
        # 下载PDF，文件名用“车辆名_原始文件名”
        filename = f"{car_name}_{get_filename_from_url(pdf_url)}"
        filepath = os.path.join(output_dir, filename)
        saved_path = download_pdf(pdf_url, output_dir)
        results.append((car_name, pdf_url, saved_path))
    return results

def download_pdfs_by_pattern_from_url(page_url, pattern, output_dir='downloads'):
    """
    从指定网页下载所有匹配pattern的PDF文件，并提取对应的车辆名。
    Args:
        page_url (str): 网页URL
        pattern (str): PDF链接的正则表达式
        output_dir (str): 保存目录
    Returns:
        list: [(car_name, pdf_url, saved_path), ...]
    """
    resp = requests.get(page_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for li in soup.find_all('li'):
        name_div = li.find('div', class_='name')
        car_name = name_div.get_text(strip=True) if name_div else 'unknown'
        for a in li.find_all('a', href=True):
            href = a['href']
            if re.match(pattern, href):
                pdf_url = urljoin(page_url, href)
                # 保存到以车辆名为名的子目录
                car_dir = os.path.join(output_dir, car_name)
                saved_path = download_pdf(pdf_url, car_dir)
                results.append((car_name, pdf_url, saved_path))
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Download vehicle specification PDFs')
    parser.add_argument('--url', help='PDF或HTML页面的URL')
    parser.add_argument('--html-file', help='本地HTML文件路径')
    parser.add_argument('--base-url', help='拼接PDF链接的基础URL')
    parser.add_argument('--pattern', help='PDF链接的正则表达式')
    parser.add_argument('--output-dir', default='downloads', help='保存目录')
    args = parser.parse_args()

    ##args.url = 'https://toyota.jp/request/webcatalog/welcab/'
    ##args.pattern = '^/pages/contents/request/webcatalog/.+\\.pdf$'
    ##args.output_dir = '/Volumes/Seagate/work/robot/webcatalog/catalogs'
    if args.pattern and args.url:
        results = download_pdfs_by_pattern_from_url(args.url, args.pattern, args.output_dir)
        for car_name, pdf_url, saved_path in results:
            print(f"{car_name}: {pdf_url} => {saved_path}")
        return
    if args.html_file:
        with open(args.html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        if not args.base_url:
            print('Error: 解析HTML时必须提供--base-url')
            return
        results = parse_vehicle_specs_from_html(html, args.base_url, args.output_dir)
        for car_name, pdf_url, saved_path in results:
            print(f"{car_name}: {pdf_url} => {saved_path}")
    elif args.url:
        download_pdf(args.url, args.output_dir)
    else:
        print('请提供--url或--html-file参数')

if __name__ == "__main__":
    '''
    python download_vehicle_specs.py --url https://xxxx/request/webcatalog/welcab/ --output-dir /home/webcatalog/catalogs'''
    main()
