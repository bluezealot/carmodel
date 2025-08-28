import requests
from bs4 import BeautifulSoup
import re
import os

car_map = {
    'ランドクルーザー 300': 'landcruiser300',
    'コペン GR SPORT': 'copen',
}

def extract_vehicle_lineup(url):
    """
    访问指定网站，提取所有车辆名称和专属页面URL pattern（car_code），并下载车辆图片到以车名命名的文件夹。
    Args:
        url (str): 车辆列表页面的URL
    Returns:
        list of dict: [{"car_name": str, "car_code": str}]
    """
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for dt in soup.find_all('dt', class_='tjp-car-detail-link__car-name'):
        car_name = dt.get_text(strip=True)
        parent = dt.parent
        img = parent.find('img', alt=car_name)
        car_code = None
        img_url = None
        car_url = None
        if img and img.has_attr('src'):
            m = re.search(r'/car/(\w+)/', img['src'])
            if m:
                car_code = m.group(1)
            img_url = img['src']
            # 处理图片链接可能缺少协议的情况
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://toyota.jp' + img_url
            # 生成车辆页面 URL
            if car_code:
                car_url = f"https://toyota.jp/{car_code}"
            # 下载图片
            if img_url:
                folder = car_name
                os.makedirs(folder, exist_ok=True)
                img_filename = os.path.join(folder, f"{car_code or car_name}.jpg")
                try:
                    img_resp = requests.get(img_url, timeout=30)
                    img_resp.raise_for_status()
                    with open(img_filename, 'wb') as f:
                        f.write(img_resp.content)
                except Exception as e:
                    print(f"图片下载失败: {img_url}, 错误: {e}")
        results.append({
            'car_name': car_name,
            'car_code': car_code,
            'car_url': car_url
        })
    return results

def extract_vehicle_lineup_from_file(html_file_path):
    """
    从本地HTML文件读取内容，提取所有车辆名称和专属页面URL pattern（car_code），并下载车辆图片到以车名命名的文件夹。
    Args:
        html_file_path (str): HTML文件路径
    Returns:
        list of dict: [{"car_name": str, "car_code": str}]
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    # 查找所有车辆名称标签
    for dt in soup.find_all('dt', class_='tjp-car-detail-link__car-name'):
        car_name = dt.get_text(strip=True)
        parent = dt.parent
        img = parent.find('img', alt=car_name)
        car_code = None
        img_url = None
        car_url = None
        if img and img.has_attr('src'):
            m = re.search(r'/car/(\w+)/', img['src'])
            if m:
                car_code = m.group(1)
            img_url = img['src']
            # 处理图片链接可能缺少协议的情况
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://toyota.jp' + img_url
            # 生成车辆页面 URL
            if car_code:
                car_url = f"https://toyota.jp/{car_code}"
            # 下载图片
            if img_url:
                folder = 'output/' + car_name
                os.makedirs(folder, exist_ok=True)
                img_filename = os.path.join(folder, f"{car_code or car_name}.jpg")
                try:
                    img_resp = requests.get(img_url, timeout=30)
                    img_resp.raise_for_status()
                    with open(img_filename, 'wb') as f:
                        f.write(img_resp.content)
                except Exception as e:
                    print(f"图片下载失败: {img_url}, 错误: {e}")
        results.append({
            'car_name': car_name,
            'car_code': car_code,
            'car_url': car_url
        })
    return results

def get_car_description(car_code, car_name=None):
    """
    根据 car_code 拼接 URL，访问页面并提取车辆描述。
    Args:
        car_code (str): 车辆代码
        car_name (str): 车辆名称（用于 car_map 兜底）
    Returns:
        dict: {"description": str, "not_found": bool}
    """
    url = f"https://toyota.jp/{car_code}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 检查是否为错误页面
        if "大変申し訳ありませんが、該当ページがございません。" in resp.text:
            if car_name and car_name in car_map:
                mapped_code = car_map[car_name]
                if mapped_code != car_code:
                    return get_car_description(mapped_code, car_name)
            return {"description": None, "not_found": True, "video_url": None, "video_id": None, "video_not_found": True}
        p_tag = soup.find('p', class_='tjp-text tjp-text--size-m-s tjp-text--normal')
        description = p_tag.get_text(strip=True) if p_tag else None
        # 查找介绍视频链接
        video_url = None
        video_id = None
        video_not_found = 'NotExist'
        # 查找所有 a 和 iframe 标签
        for tag in soup.find_all(['a', 'iframe']):
            href = tag.get('href') or tag.get('src')
            if href and 'youtube.com/embed/' in href:
                m = re.search(r'youtube\.com/embed/([\w-]+)', href)
                if m:
                    video_id = m.group(1)
                    # 处理可能的 // 前缀
                    if href.startswith('//'):
                        video_url = 'https:' + href
                    elif href.startswith('http'):
                        video_url = href
                    else:
                        video_url = href
                    video_not_found = 'Exist'
                    break
        return {
            "description": description,
            "not_found": False,
            "video_url": video_url,
            "video_id": video_id,
            "video_not_found": video_not_found
        }
    except Exception as e:
        if car_name and car_name in car_map:
            mapped_code = car_map[car_name]
            if mapped_code != car_code:
                return get_car_description(mapped_code, car_name)
        return {"description": None, "not_found": True, "video_url": None, "video_id": None, "video_not_found": True}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extract vehicle lineup info from HTML file')
    parser.add_argument('--file', required=False, help='HTML文件路径')
    args = parser.parse_args()
    args.file = '/Volumes/Seagate/work/robot/webcatalog/toyota_lineup.txt'
    lineup = extract_vehicle_lineup_from_file(args.file)
    # 去重 car_name 和 car_code
    unique = []
    seen = set()
    for item in lineup:
        key = (item['car_name'], item['car_code'])
        if key not in seen:
            unique.append(item)
            seen.add(key)
    for idx, item in enumerate(unique, 1):
        print(f"{idx}. {item['car_name']}: {item['car_code']}")
        print(f"    页面: {item.get('car_url')}")
        desc_info = get_car_description(item['car_code'], item['car_name'])
        print(f"    描述: {desc_info['description']}")
        print(f"    页面不存在: {desc_info['not_found']}")
        print(f"    视频链接: {desc_info['video_url']}")
        print(f"    视频ID: {desc_info['video_id']}")
        print(f"    视频不存在: {desc_info['video_not_found']}")
