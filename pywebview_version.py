#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webview
import os
import json
import threading
from PIL import Image

# 配置文件路径
CONFIG_FILE = "cropper_config.json"

class ConfigManager:
    """配置管理类"""
    
    @staticmethod
    def load_settings():
        """加载设置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return {
            "output_dir": os.path.expanduser("~/Pictures/Cropped"),
            "crop_unit": "%",
            "crop_settings": {
                "top": 0,
                "bottom": 0,
                "left": 0,
                "right": 0
            },
            "output_format": "JPG"
        }
    
    @staticmethod
    def save_settings(settings):
        """保存设置"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

class ImageProcessor:
    """图片处理类"""
    
    def __init__(self, files, top_value, bottom_value, left_value, right_value, 
                 output_dir, output_format='JPG', crop_unit='%'):
        self.files = files
        self.top_value = top_value
        self.bottom_value = bottom_value
        self.left_value = left_value
        self.right_value = right_value
        self.output_dir = output_dir
        self.output_format = output_format
        self.crop_unit = crop_unit
        self.running = True
    
    def process_all(self):
        """批量处理所有文件"""
        results = {
            'success': 0,
            'failed': 0,
            'output_files': [],
            'errors': []
        }
        
        total_files = len(self.files)
        for i, file_path in enumerate(self.files):
            if not self.running:
                break
                
            try:
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # 如果输出格式为"自动"，则使用原始文件格式
                if self.output_format == "自动":
                    # 提取原始文件格式
                    original_ext = os.path.splitext(file_path)[1].lower()
                    # 移除点号
                    if original_ext.startswith('.'):
                        original_ext = original_ext[1:]
                    # 处理常见的扩展名映射
                    format_mapping = {
                        'jpg': 'jpg',
                        'jpeg': 'jpg',
                        'png': 'png',
                        'bmp': 'bmp',
                        'tiff': 'tiff',
                        'tif': 'tiff'
                    }
                    # 获取输出格式
                    output_ext = format_mapping.get(original_ext, 'jpg')
                else:
                    # 使用指定的输出格式
                    output_ext = self.output_format.lower()
                
                # 生成输出文件名
                output_filename = f"{base_name}_cropped.{output_ext}"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # 确保文件名唯一
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_cropped_{counter}.{output_ext}"
                    output_path = os.path.join(self.output_dir, output_filename)
                    counter += 1
                
                # 根据单位选择裁剪方法
                if self.crop_unit == '%':
                    self.crop_image_by_percentage(file_path, output_path, output_ext)
                else:
                    self.crop_image_by_pixels(file_path, output_path, output_ext)
                
                results['success'] += 1
                results['output_files'].append(output_path)
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return results
    
    def crop_image_by_percentage(self, input_path, output_path, output_ext):
        """按百分比裁剪图片"""
        with Image.open(input_path) as img:
            width, height = img.size
            
            # 计算裁剪区域
            top_crop = int(height * self.top_value / 100)
            bottom_crop = int(height * self.bottom_value / 100)
            left_crop = int(width * self.left_value / 100)
            right_crop = int(width * self.right_value / 100)
            
            # 计算新的尺寸
            new_width = width - left_crop - right_crop
            new_height = height - top_crop - bottom_crop
            
            # 验证裁剪参数
            if new_width <= 0 or new_height <= 0:
                raise ValueError("裁剪参数无效，裁剪后的图片尺寸为0")
            
            # 执行裁剪
            crop_box = (left_crop, top_crop, width - right_crop, height - bottom_crop)
            cropped_img = img.crop(crop_box)
            
            # 保存图片
            if output_ext == 'jpg':
                cropped_img.save(output_path, 'JPEG')
            else:
                # 根据输出扩展名确定保存格式
                format_mapping = {
                    'png': 'PNG',
                    'bmp': 'BMP',
                    'tiff': 'TIFF'
                }
                save_format = format_mapping.get(output_ext, 'JPEG')
                cropped_img.save(output_path, save_format)
    
    def crop_image_by_pixels(self, input_path, output_path, output_ext):
        """按像素裁剪图片"""
        with Image.open(input_path) as img:
            width, height = img.size
            
            # 计算裁剪区域
            top_crop = self.top_value
            bottom_crop = self.bottom_value
            left_crop = self.left_value
            right_crop = self.right_value
            
            # 计算新的尺寸
            new_width = width - left_crop - right_crop
            new_height = height - top_crop - bottom_crop
            
            # 验证裁剪参数
            if new_width <= 0 or new_height <= 0:
                raise ValueError("裁剪参数无效，裁剪后的图片尺寸为0")
            
            # 执行裁剪
            crop_box = (left_crop, top_crop, width - right_crop, height - bottom_crop)
            cropped_img = img.crop(crop_box)
            
            # 保存图片
            if output_ext == 'jpg':
                cropped_img.save(output_path, 'JPEG')
            else:
                # 根据输出扩展名确定保存格式
                format_mapping = {
                    'png': 'PNG',
                    'bmp': 'BMP',
                    'tiff': 'TIFF'
                }
                save_format = format_mapping.get(output_ext, 'JPEG')
                cropped_img.save(output_path, save_format)
    
    def stop(self):
        """停止处理"""
        self.running = False

class ImageCropperWebView:
    """图片批量裁剪工具 - WebView版本"""
    
    def __init__(self):
        # 加载设置
        self.settings = ConfigManager.load_settings()
        self.files = []
        self.processor = None
        self.processing_thread = None
        self.results = None
    

    
    def start_processing(self, top, bottom, left, right, output_dir, output_format, crop_unit):
        """开始处理"""
        # 验证裁剪参数
        if crop_unit == '%':
            if top + bottom >= 100 or left + right >= 100:
                return {'success': False, 'error': '裁剪百分比总和不能超过100%'}
        
        # 创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return {'success': False, 'error': f'无法创建输出目录: {e}'}
        
        # 保存设置
        self.settings = {
            "output_dir": output_dir,
            "crop_unit": crop_unit,
            "crop_settings": {
                "top": top,
                "bottom": bottom,
                "left": left,
                "right": right
            },
            "output_format": output_format
        }
        ConfigManager.save_settings(self.settings)
        
        # 创建处理对象
        self.processor = ImageProcessor(
            self.files, top, bottom, left, right,
            output_dir, output_format, crop_unit
        )
        
        # 在新线程中处理
        def process_thread():
            self.results = self.processor.process_all()
        
        self.processing_thread = threading.Thread(target=process_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        return {'success': True}
    
    def get_results(self):
        """获取处理结果"""
        if self.results:
            return self.results
        return {'success': 0, 'failed': 0, 'output_files': [], 'errors': []}
    
    def stop_processing(self):
        """停止处理"""
        if self.processor:
            self.processor.stop()
        return {'success': True}
    
    def get_settings(self):
        """获取设置"""
        return self.settings
    
    def get_thumbnail(self, file_path, size=(120, 120)):
        """获取图片缩略图"""
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.LANCZOS)
                # 转换为Base64编码，这里简化处理，实际需要完整实现
                return {'success': True, 'filename': os.path.basename(file_path)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                size = os.path.getsize(file_path) / 1024  # KB
                return {
                    'success': True,
                    'width': width,
                    'height': height,
                    'size': round(size, 1),
                    'filename': os.path.basename(file_path)
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_list(self):
        """获取文件列表"""
        file_info_list = []
        for file_path in self.files:
            info = self.get_file_info(file_path)
            if info['success']:
                file_info_list.append(info)
        return file_info_list
    
    def clear_files(self):
        """清空文件列表"""
        self.files = []
        return {'success': True}
    
    def select_directory(self):
        """选择目录"""
        result = webview.windows[0].create_file_dialog(dialog_type=webview.FOLDER_DIALOG)
        if result:
            return result[0]
        return None
    
    def load_files(self):
        """加载图片文件"""
        # 不使用文件类型过滤器，允许选择所有文件
        result = webview.windows[0].create_file_dialog(
            dialog_type=webview.OPEN_DIALOG,
            allow_multiple=True
        )
        if result:
            self.files.extend(result)
            return len(result)
        return 0

# 创建HTML内容
HTML_CONTENT = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>图片批量裁剪工具 v3.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #2c3e50;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            color: white;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* 卡片样式 */
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            padding: 25px;
            margin-bottom: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        /* 标题样式 */
        .section-title {
            color: #3498db;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        /* 表单样式 */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .form-row-2 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
            font-size: 0.95em;
        }
        
        input[type="number"], select, input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        input[type="number"]:focus, select:focus, input[type="text"]:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        /* 按钮样式 */
        button {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            margin-right: 12px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        
        button:hover {
            background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        /* 特殊按钮样式 */
        .btn-secondary {
            background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        }
        
        .btn-secondary:hover {
            background: linear-gradient(135deg, #7f8c8d 0%, #6c7a89 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }
        
        .btn-danger:hover {
            background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
        }
        
        /* 浏览按钮 */
        .browse-btn {
            padding: 12px 16px;
            margin-left: 10px;
            font-size: 13px;
        }
        
        /* 文件列表样式 */
        .file-list-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .file-count {
            background: #3498db;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .thumbnails {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .thumbnail {
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .thumbnail:hover {
            border-color: #3498db;
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        }
        
        .thumbnail .filename {
            font-size: 13px;
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .thumbnail .file-info {
            font-size: 11px;
            color: #95a5a6;
        }
        
        /* 控制按钮区域 */
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        /* 状态消息 */
        .status {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #e8f4f8 0%, #d5e8f3 100%);
            border-radius: 8px;
            color: #2c3e50;
            font-weight: 600;
            margin: 20px 0;
            border-left: 5px solid #3498db;
        }
        
        /* 结果区域 */
        .results {
            padding: 20px;
            background: linear-gradient(135deg, #e8f9e9 0%, #d5f4e6 100%);
            border-radius: 8px;
            color: #2c3e50;
            margin: 20px 0;
            border-left: 5px solid #27ae60;
        }
        
        .results h3 {
            color: #27ae60;
            margin-bottom: 15px;
        }
        
        .results ul {
            list-style: none;
            padding-left: 0;
            margin: 15px 0;
        }
        
        .results li {
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        
        /* 响应式设计 */
        @media (max-width: 1024px) {
            .form-row-2 {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .card {
                padding: 20px;
            }
            
            .form-row,
            .form-row-2 {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .controls button {
                margin-right: 0;
                width: 100%;
            }
            
            .thumbnails {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
        }
        
        @media (max-width: 480px) {
            h1 {
                font-size: 1.8em;
            }
            
            .section-title {
                font-size: 1.3em;
            }
            
            .thumbnail {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>图片批量裁剪工具 v3.0</h1>
        
        <!-- 输出设置 -->
        <div class="card">
            <h2 class="section-title">输出设置</h2>
            <div class="form-row">
                <div class="form-group">
                    <label for="output_format">输出格式</label>
                    <select id="output_format">
                        <option value="自动">自动</option>
                        <option value="JPG">JPG</option>
                        <option value="PNG">PNG</option>
                        <option value="BMP">BMP</option>
                        <option value="TIFF">TIFF</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="output_dir">输出目录</label>
                    <div style="display: flex;">
                        <input type="text" id="output_dir" readonly>
                        <button class="browse-btn" onclick="selectDirectory()">浏览</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 裁剪参数 -->
        <div class="card">
            <h2 class="section-title">裁剪参数</h2>
            <div class="form-row">
                <div class="form-group">
                    <label for="crop_unit">裁剪单位</label>
                    <select id="crop_unit">
                        <option value="%">%</option>
                        <option value="px">px</option>
                    </select>
                </div>
            </div>
            <div class="form-row-2">
                <div class="form-group">
                    <label for="top">上边裁剪</label>
                    <input type="number" id="top" min="0" max="100" value="0">
                </div>
                <div class="form-group">
                    <label for="bottom">下边裁剪</label>
                    <input type="number" id="bottom" min="0" max="100" value="0">
                </div>
                <div class="form-group">
                    <label for="left">左边裁剪</label>
                    <input type="number" id="left" min="0" max="100" value="0">
                </div>
                <div class="form-group">
                    <label for="right">右边裁剪</label>
                    <input type="number" id="right" min="0" max="100" value="0">
                </div>
            </div>
        </div>
        
        <!-- 待处理列表 -->
        <div class="card">
            <div class="file-list-header">
                <h2 class="section-title">待处理列表</h2>
                <div>
                    <button onclick="selectFiles()">添加文件</button>
                    <button class="btn-danger" onclick="clearList()">清空列表</button>
                </div>
            </div>
            <div class="thumbnails" id="thumbnails"></div>
        </div>
        
        <!-- 控制按钮 -->
        <div class="controls">
            <button onclick="startProcessing()">开始裁剪</button>
            <button class="btn-secondary" onclick="stopProcessing()">停止</button>
        </div>
        
        <!-- 状态和结果 -->
        <div class="status" id="status">准备就绪</div>
        <div class="results" id="results" style="display: none;"></div>
    </div>
    
    <script>
        // 初始化设置
        function initSettings() {
            window.pywebview.api.get_settings().then(function(settings) {
                document.getElementById('output_format').value = settings.output_format;
                document.getElementById('output_dir').value = settings.output_dir;
                document.getElementById('crop_unit').value = settings.crop_unit;
                document.getElementById('top').value = settings.crop_settings.top;
                document.getElementById('bottom').value = settings.crop_settings.bottom;
                document.getElementById('left').value = settings.crop_settings.left;
                document.getElementById('right').value = settings.crop_settings.right;
            });
        }
        
        // 选择文件
        function selectFiles() {
            window.pywebview.api.load_files().then(function(count) {
                updateFileList();
                document.getElementById('status').textContent = `已添加 ${count} 个文件`;
            });
        }
        
        // 选择目录
        function selectDirectory() {
            window.pywebview.api.select_directory().then(function(dir) {
                if (dir) {
                    document.getElementById('output_dir').value = dir;
                }
            });
        }
        
        // 更新文件列表
        function updateFileList() {
            window.pywebview.api.get_file_list().then(function(files) {
                const thumbnails = document.getElementById('thumbnails');
                thumbnails.innerHTML = '';
                
                files.forEach(function(file) {
                    const thumbnailDiv = document.createElement('div');
                    thumbnailDiv.className = 'thumbnail';
                    thumbnailDiv.innerHTML = `
                        <div class="filename">${file.filename}</div>
                        <div>${file.width}x${file.height}px</div>
                        <div>${file.size} KB</div>
                    `;
                    thumbnails.appendChild(thumbnailDiv);
                });
            });
        }
        
        // 开始处理
        function startProcessing() {
            const settings = {
                top: parseInt(document.getElementById('top').value),
                bottom: parseInt(document.getElementById('bottom').value),
                left: parseInt(document.getElementById('left').value),
                right: parseInt(document.getElementById('right').value),
                output_dir: document.getElementById('output_dir').value,
                output_format: document.getElementById('output_format').value,
                crop_unit: document.getElementById('crop_unit').value
            };
            
            window.pywebview.api.start_processing(
                settings.top, settings.bottom, settings.left, settings.right,
                settings.output_dir, settings.output_format, settings.crop_unit
            ).then(function(result) {
                if (result.success) {
                    document.getElementById('status').textContent = '开始处理...';
                    document.getElementById('results').style.display = 'none';
                    // 定期检查结果
                    checkResults();
                } else {
                    document.getElementById('status').textContent = `错误: ${result.error}`;
                }
            });
        }
        
        // 检查结果
        function checkResults() {
            window.pywebview.api.get_results().then(function(results) {
                if (results.success + results.failed > 0) {
                    document.getElementById('status').textContent = `处理完成！成功: ${results.success} 个，失败: ${results.failed} 个`;
                    document.getElementById('results').innerHTML = `
                        <h3>处理结果</h3>
                        <p>成功: ${results.success} 个</p>
                        <p>失败: ${results.failed} 个</p>
                        <h4>输出文件:</h4>
                        <ul>
                            ${results.output_files.map(file => `<li>${file}</li>`).join('')}
                        </ul>
                        ${results.errors.length > 0 ? `<h4>错误信息:</h4><ul>${results.errors.map(error => `<li>${error.file}: ${error.error}</li>`).join('')}</ul>` : ''}
                    `;
                    document.getElementById('results').style.display = 'block';
                } else {
                    // 继续检查
                    setTimeout(checkResults, 1000);
                }
            });
        }
        
        // 停止处理
        function stopProcessing() {
            window.pywebview.api.stop_processing().then(function() {
                document.getElementById('status').textContent = '处理已停止';
            });
        }
        
        // 清空列表
        function clearList() {
            window.pywebview.api.clear_files().then(function() {
                updateFileList();
                document.getElementById('status').textContent = '文件列表已清空';
            });
        }
        
        // 初始化
        window.onload = function() {
            initSettings();
            updateFileList();
        };
    </script>
</body>
</html>"""


if __name__ == '__main__':
    # 创建应用实例
    app = ImageCropperWebView()
    
    # 创建窗口
    webview.create_window(
        title='图片批量裁剪工具 v3.0',
        html=HTML_CONTENT,
        js_api=app,
        width=1000,
        height=800,
        resizable=True,
        confirm_close=True
    )
    
    # 运行应用
    webview.start()

