# carmodel

这是一套提取特定网站车型说明书信息，并转化为PDF的工具集。
按照以下顺序执行，可以拿到所有的车型说明书，并且提取Markdown格式的信息。
1.下载：python download_vehicle_specs.py --url https://xxxx/request/webcatalog/welcab/ --output-dir /home/webcatalog/catalogs
2.提取Markdown：
run_marker_batch.py --scan-folder /home/webcatalog/catalogs --file-pattern '^.+welcab.+\\.pdf$' --output-dir /home/webcatalog/markdown
3.检查是不是所有的PDF都已经下载：python scan_and_match_pdfs.py --url https://xxxx/welcab/ --cartype '福祉車両' --scan-folder /Volumes/Seagate/work/robot/webcatalog/catalogs --file-pattern '^.+welcab.+\\.pdf$'
3.替换Markdown中引用的图片路径：python replace_md_images.py --root-folder /Volumes/Seagate/work/robot/webcatalog/workspace --url-prefix http://xxxx/site2507/ 