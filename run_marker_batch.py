import os
import re
import subprocess
import argparse

def run_marker_on_matched_pdfs(scan_folder, file_pattern, output_dir):
    """
    扫描scan_folder下所有子文件夹，匹配PDF文件，依次运行marker_single命令。
    Args:
        scan_folder (str): 根目录
        file_pattern (str): 文件名正则表达式
        output_dir (str): marker_single输出目录
    """
    for root, dirs, files in os.walk(scan_folder):
        for f in files:
            if re.search(file_pattern, f):
                pdf_path = os.path.join(root, f)
                cmd = [
                    'marker_single',
                    pdf_path,
                    '--output_format', 'markdown',
                    '--output_dir', output_dir,
                    '--paginate_output',
                    '--format_lines'
                ]
                print(f"运行: {' '.join(cmd)}")
                subprocess.run(cmd, check=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量处理PDF并运行marker_single命令')
    parser.add_argument('--scan-folder', required=False, help='待扫描的PDF根目录')
    parser.add_argument('--file-pattern', required=False, help='PDF文件名正则表达式')
    parser.add_argument('--output-dir', required=False, help='marker_single输出目录')
    args = parser.parse_args()
    args.scan_folder = '/Volumes/Seagate/work/robot/webcatalog/catalogs'
    args.file_pattern = '^.+main.+\\.pdf$'
    args.output_dir = '/Volumes/Seagate/work/robot/webcatalog/output'
    run_marker_on_matched_pdfs(args.scan_folder, args.file_pattern, args.output_dir)

