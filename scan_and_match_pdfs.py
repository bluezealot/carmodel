import os
import re
import csv
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def scan_and_match_pdfs(url, cartype, scan_folder, file_pattern, output_csv='output.csv'):
    """
    扫描本地PDF文件夹，匹配给定网页中的PDF链接，将匹配信息输出到CSV。
    Args:
        url (str): 需要解析的网页URL
        cartype (str): 车型
        scan_folder (str): 本地PDF文件夹
        file_pattern (str): 文件名正则表达式
        output_csv (str): 输出CSV文件名
    """
    # 获取网页内容
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 获取所有PDF链接及其所在<li>的车辆名
    pdf_info_list = []  # [(car_name, href)]
    for li in soup.find_all('li'):
        name_div = li.find('div', class_='name')
        car_name = name_div.get_text(strip=True) if name_div else ''
        for a in li.find_all('a', href=True):
            href = a['href']
            if re.search(file_pattern, href):
                pdf_info_list.append((car_name, href))
    # 扫描本地文件夹及其所有子目录（递归），并记录文件名和父文件夹（车型名）
    local_file_map = {}  # {(car_name, file_name): full_path}
    for root, dirs, files in os.walk(scan_folder):
        folder_car_name = os.path.basename(root)
        for f in files:
            if re.search(file_pattern, f):
                local_file_map[(folder_car_name, f)] = os.path.join(root, f)
    # 匹配并追加到CSV（追加模式）
    file_exists = os.path.exists(output_csv)
    written = set()  # 记录已写入的(web_pdf_path, car_name)避免重复
    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['cartype', 'car_name', 'web_pdf_path', 'local_pdf_path', 'matched'])
        for car_name, link in pdf_info_list:
            key = (link, car_name)
            if key in written:
                continue  # 跳过重复
            written.add(key)
            local_file_name = os.path.basename(link)
            matched_file = local_file_map.get((car_name, local_file_name))
            writer.writerow([cartype, car_name, link, matched_file or '', bool(matched_file)])
    print(f'CSV已追加: {output_csv}')

if __name__ == '__main__':
    """
    python scan_and_match_pdfs.py --url https://xxxx/welcab/ --cartype '福祉車両' --scan-folder /Volumes/Seagate/work/robot/webcatalog/catalogs --file-pattern '^.+welcab.+\\.pdf$'
    """
    import argparse
    parser = argparse.ArgumentParser(description='Scan PDF folder and match with web page, output to CSV')
    parser.add_argument('--url', required=True, help='网页URL')
    parser.add_argument('--cartype', required=True, help='车型')
    parser.add_argument('--scan-folder', required=True, help='本地PDF文件夹')
    parser.add_argument('--file-pattern', required=True, help='文件名正则表达式')
    parser.add_argument('--output-csv', default='output.csv', help='输出CSV文件名')
    args = parser.parse_args()
    # args.url = 'https://xxxx/welcab/'
    # args.cartype = 'ビジネスカー'
    # args.scan_folder = '/Volumes/Seagate/work/robot/webcatalog/catalogs'
    # args.file_pattern = '^.+welcab.+\\.pdf$'
    # args.output_csv = '/Volumes/Seagate/work/robot/webcatalog/output.csv'
    scan_and_match_pdfs(args.url, args.cartype, args.scan_folder, args.file_pattern, args.output_csv)
