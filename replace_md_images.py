import os
import re
import argparse

def replace_image_links_in_md(md_path, url_prefix, root_folder):
    """
    替换md文件中所有图片引用为指定url前缀+文件名
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 匹配 ![](...) 形式的图片引用
    def replacer(match):
        img_name = match.group(1)
        # 获取相对子文件夹路径
        rel_dir = os.path.relpath(os.path.dirname(md_path), root_folder)
        # 拼接子文件夹和图片文件名
        img_url = '{}/{}/{}'.format(url_prefix.rstrip('/'), rel_dir.strip('.'), img_name.lstrip('./')) if rel_dir != '.' else '{}/{}'.format(url_prefix.rstrip('/'), img_name.lstrip('./'))
        return '![]({})'.format(img_url)
    new_content = re.sub(r'!\[]\(([^)]+)\)', replacer, content)
    if new_content != content:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已处理: {md_path}")
    else:
        print(f"无变化: {md_path}")

def batch_replace_md_images(root_folder, url_prefix):
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(subdir, file)
                replace_image_links_in_md(md_path, url_prefix, root_folder)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量替换md文件中的图片链接为指定url前缀')
    parser.add_argument('--root-folder', required=True, help='根目录，包含若干子文件夹，每个子文件夹下有md文件')
    parser.add_argument('--url-prefix', required=True, help='图片url前缀')
    args = parser.parse_args()
    batch_replace_md_images(args.root_folder, args.url_prefix)
