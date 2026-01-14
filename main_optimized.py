#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import json
import subprocess
import sys
from PIL import Image, ImageTk
import time

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
            "output_format": "JPG",
            "quality": 90
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
                 output_dir, output_format='JPG', quality=90, crop_unit='%',
                 progress_callback=None, file_callback=None, finish_callback=None):
        self.files = files
        self.top_value = top_value
        self.bottom_value = bottom_value
        self.left_value = left_value
        self.right_value = right_value
        self.output_dir = output_dir
        self.output_format = output_format
        self.quality = quality
        self.crop_unit = crop_unit
        self.progress_callback = progress_callback
        self.file_callback = file_callback
        self.finish_callback = finish_callback
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
                output_filename = f"{base_name}_cropped.{self.output_format.lower()}"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # 确保文件名唯一
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_cropped_{counter}.{self.output_format.lower()}"
                    output_path = os.path.join(self.output_dir, output_filename)
                    counter += 1
                
                # 根据单位选择裁剪方法
                if self.crop_unit == '%':
                    self.crop_image_by_percentage(file_path, output_path)
                else:
                    self.crop_image_by_pixels(file_path, output_path)
                
                results['success'] += 1
                results['output_files'].append(output_path)
                
                if self.file_callback:
                    self.file_callback(file_path, True, "")
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
                
                if self.file_callback:
                    self.file_callback(file_path, False, str(e))
            
            # 更新进度
            if self.progress_callback:
                progress = int((i + 1) / total_files * 100)
                self.progress_callback(progress)
        
        if self.finish_callback:
            self.finish_callback(results)
    
    def crop_image_by_percentage(self, input_path, output_path):
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
            if self.output_format.upper() == 'JPG':
                cropped_img.save(output_path, 'JPEG', quality=self.quality)
            else:
                cropped_img.save(output_path, self.output_format.upper())
    
    def crop_image_by_pixels(self, input_path, output_path):
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
            if self.output_format.upper() == 'JPG':
                cropped_img.save(output_path, 'JPEG', quality=self.quality)
            else:
                cropped_img.save(output_path, self.output_format.upper())
    
    def stop(self):
        """停止处理"""
        self.running = False

class ImageCropperGUI:
    """图片批量裁剪工具GUI"""
    
    def __init__(self, root):
        self.root = root
        self.processor = None
        self.processing_thread = None
        
        # 加载设置
        self.settings = ConfigManager.load_settings()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.root.title("图片批量裁剪工具 v3.0 (增强版)")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 裁剪参数框架
        self.crop_frame = ttk.LabelFrame(main_frame, text="裁剪参数", padding="10")
        self.crop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.crop_frame.columnconfigure(1, weight=1)
        self.crop_frame.columnconfigure(3, weight=1)
        self.crop_frame.columnconfigure(5, weight=1)
        
        # 裁剪单位选择
        ttk.Label(self.crop_frame, text="裁剪单位:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.unit_var = tk.StringVar(value=self.settings.get("crop_unit", "%"))
        self.unit_combo = ttk.Combobox(self.crop_frame, textvariable=self.unit_var, 
                                      values=["%", "px"], state="readonly", width=5)
        self.unit_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.unit_combo.bind("<<ComboboxSelected>>", self.on_unit_change)
        
        # 上下左右裁剪参数
        self.top_label = ttk.Label(self.crop_frame, text=f"上边裁剪({self.unit_var.get()}):")
        self.top_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.top_var = tk.IntVar(value=self.settings.get("crop_settings", {}).get("top", 0))
        self.top_spin = ttk.Spinbox(self.crop_frame, from_=0, to=100, textvariable=self.top_var, width=10)
        self.top_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        self.bottom_label = ttk.Label(self.crop_frame, text=f"下边裁剪({self.unit_var.get()}):")
        self.bottom_label.grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        self.bottom_var = tk.IntVar(value=self.settings.get("crop_settings", {}).get("bottom", 0))
        self.bottom_spin = ttk.Spinbox(self.crop_frame, from_=0, to=100, textvariable=self.bottom_var, width=10)
        self.bottom_spin.grid(row=1, column=3, sticky=(tk.W, tk.E))
        
        self.left_label = ttk.Label(self.crop_frame, text=f"左边裁剪({self.unit_var.get()}):")
        self.left_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.left_var = tk.IntVar(value=self.settings.get("crop_settings", {}).get("left", 0))
        self.left_spin = ttk.Spinbox(self.crop_frame, from_=0, to=100, textvariable=self.left_var, width=10)
        self.left_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        self.right_label = ttk.Label(self.crop_frame, text=f"右边裁剪({self.unit_var.get()}):")
        self.right_label.grid(row=2, column=2, sticky=tk.W, padx=(0, 5))
        self.right_var = tk.IntVar(value=self.settings.get("crop_settings", {}).get("right", 0))
        self.right_spin = ttk.Spinbox(self.crop_frame, from_=0, to=100, textvariable=self.right_var, width=10)
        self.right_spin.grid(row=2, column=3, sticky=(tk.W, tk.E))
        
        # 根据当前单位设置spinbox范围
        self.update_spinbox_ranges()
        
        # 输出设置框架
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(3, weight=1)
        
        ttk.Label(output_frame, text="输出格式:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.format_var = tk.StringVar(value=self.settings.get("output_format", "JPG"))
        self.format_combo = ttk.Combobox(output_frame, textvariable=self.format_var, 
                                        values=["JPG", "PNG", "BMP", "TIFF"], state="readonly", width=8)
        self.format_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(output_frame, text="质量:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.quality_var = tk.IntVar(value=self.settings.get("quality", 90))
        self.quality_spin = ttk.Spinbox(output_frame, from_=1, to=100, textvariable=self.quality_var, width=8)
        self.quality_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(output_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.output_dir_var = tk.StringVar(value=self.settings.get("output_dir", os.path.expanduser("~/Pictures/Cropped")))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)
        self.output_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(output_frame, text="浏览", command=self.browse_output_dir)
        self.browse_btn.grid(row=1, column=3, sticky=tk.W)
        
        # 文件列表框架
        file_frame = ttk.LabelFrame(main_frame, text="待处理列表 (双击添加文件，点击预览)", padding="10")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(2, weight=1)
        
        # 按钮框架
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.add_files_btn = ttk.Button(btn_frame, text="添加文件", command=self.add_files)
        self.add_files_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_folder_btn = ttk.Button(btn_frame, text="添加文件夹", command=self.add_folder)
        self.add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(btn_frame, text="清空列表", command=self.clear_files)
        self.clear_btn.pack(side=tk.LEFT)
        
        # 显示选项框架
        self.view_options_frame = ttk.LabelFrame(file_frame, text="显示选项")
        self.view_options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 显示模式选择
        mode_frame = ttk.Frame(self.view_options_frame)
        mode_frame.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(mode_frame, text="显示模式:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 列表模式按钮
        self.list_mode_btn = ttk.Button(mode_frame, text="列表", command=lambda: self.set_view_mode("list"))
        self.list_mode_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 平铺模式按钮
        self.tile_mode_btn = ttk.Button(mode_frame, text="平铺", command=lambda: self.set_view_mode("tile"))
        self.tile_mode_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 显示文件名复选框
        self.show_filename_var = tk.BooleanVar(value=True)
        self.show_filename_check = ttk.Checkbutton(self.view_options_frame, text="显示文件名", 
                                                   variable=self.show_filename_var, command=self.toggle_filename_display)
        self.show_filename_check.pack(side=tk.LEFT, padx=(5, 15))
        
        # 存储当前显示模式
        self.current_view_mode = "list"
        
        # 缩略图列表
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 滚动区域
        self.canvas = tk.Canvas(list_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 创建用于放置缩略图的框架
        self.thumbnail_frame = ttk.Frame(self.canvas)
        # 保存创建的窗口项ID
        self.thumbnail_window_id = self.canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")
        
        # 配置网格
        self.thumbnail_frame.columnconfigure(0, weight=1)
        
        # 绑定滚动事件
        self.thumbnail_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # 绑定窗口大小变化事件，重新排列缩略图
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # 绑定鼠标滚轮事件到多个元素，确保在任何位置都能滚动
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        self.thumbnail_frame.bind("<MouseWheel>", self.on_canvas_scroll)
        self.scrollbar.bind("<MouseWheel>", self.on_canvas_scroll)
        list_frame.bind("<MouseWheel>", self.on_canvas_scroll)
        file_frame.bind("<MouseWheel>", self.on_canvas_scroll)
        
        # 布局
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 双击画布添加文件
        self.canvas.bind('<Double-Button-1>', lambda e: self.add_files())
        
        # 存储缩略图信息
        self.thumbnails = []
        
        # 预览窗口
        self.preview_window = None
        # 预览缩放相关
        self.current_zoom_scale = 1.0  # 当前缩放比例
        self.min_zoom = 0.1  # 最小缩放比例
        self.max_zoom = 5.0  # 最大缩放比例
        self.zoom_step = 0.1  # 缩放步长
        # 存储当前预览的图片信息，用于缩放
        self.current_preview_image = None
        self.current_preview_size = None
        
        # 进度条
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress_bar.grid_remove()  # 初始隐藏
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        self.start_btn = ttk.Button(control_frame, text="开始裁剪", command=self.start_processing)
        self.start_btn.grid(row=0, column=0, sticky=tk.E, padx=(0, 5))
        
        self.open_folder_btn = ttk.Button(control_frame, text="打开文件夹", command=self.open_output_folder)
        self.open_folder_btn.grid(row=0, column=1, padx=(5, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_processing, state="disabled")
        self.stop_btn.grid(row=0, column=2, sticky=tk.W)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, sticky=tk.W)
        
        # 配置权重
        main_frame.rowconfigure(2, weight=1)
    
    def add_files(self, files=None):
        """添加文件到列表"""
        if files is None:
            files = filedialog.askopenfilenames(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("所有文件", "*.*")
                ]
            )
        
        if files:
            for file_path in files:
                if os.path.isfile(file_path):
                    self.add_thumbnail(file_path)
            
            self.update_status(f"已添加 {len(files)} 个文件")
    
    def add_folder(self):
        """添加文件夹中的所有图片文件"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
            files = []
            
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if os.path.splitext(filename)[1].lower() in image_extensions:
                        files.append(os.path.join(root, filename))
            
            if files:
                for file_path in files:
                    self.add_thumbnail(file_path)
                
                self.update_status(f"从文件夹添加了 {len(files)} 个文件")
            else:
                messagebox.showinfo("提示", "该文件夹中没有找到图片文件")
    

    
    def preview_image(self, file_path):
        """预览图片和裁剪效果"""
        try:
            # 获取当前图片在列表中的索引
            file_index = -1
            for i, thumb in enumerate(self.thumbnails):
                if thumb["file_path"] == file_path:
                    file_index = i
                    break
            
            if file_index == -1:
                messagebox.showerror("预览错误", "图片不在列表中")
                return
            
            # 存储当前预览索引
            self.current_preview_index = file_index
            
            # 第一次预览时创建窗口，后续复用窗口
            if not self.preview_window or not self.preview_window.winfo_exists():
                self._create_preview_window()
            
            # 更新窗口内容
            self._update_preview_content(file_path, file_index)
            
        except Exception as e:
            messagebox.showerror("预览错误", f"无法预览图片: {e}")
    
    def _create_preview_window(self):
        """创建预览窗口"""
        self.preview_window = tk.Toplevel(self.root)
        # 增大窗口初始高度，确保信息区域有足够空间显示
        self.preview_window.geometry("1000x750")
        # 允许窗口调整大小
        self.preview_window.minsize(800, 600)
        
        # 创建主框架
        self.preview_frame = ttk.Frame(self.preview_window, padding="10")
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置主框架的行列权重
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)  # 中间内容区域权重最高
        
        # 导航按钮框架
        self.nav_frame = ttk.Frame(self.preview_frame)
        self.nav_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        # 上一张按钮
        self.prev_btn = ttk.Button(self.nav_frame, text="上一张 (←)", command=self.preview_prev_image)
        self.prev_btn.pack(side=tk.LEFT)
        
        # 缩放控制按钮组
        zoom_frame = ttk.Frame(self.nav_frame)
        zoom_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        # 放大按钮
        self.zoom_in_btn = ttk.Button(zoom_frame, text="放大 (+)", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 缩小按钮
        self.zoom_out_btn = ttk.Button(zoom_frame, text="缩小 (-)", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 重置按钮
        self.reset_zoom_btn = ttk.Button(zoom_frame, text="重置", command=self.reset_zoom)
        self.reset_zoom_btn.pack(side=tk.LEFT)
        
        # 下一张按钮
        self.next_btn = ttk.Button(self.nav_frame, text="下一张 (→)", command=self.preview_next_image)
        self.next_btn.pack(side=tk.RIGHT)
        
        # 左右分栏容器
        self.content_frame = ttk.Frame(self.preview_frame)
        self.content_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # 为左右分栏设置相同权重，确保平分
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # 原图框架
        self.left_frame = ttk.LabelFrame(self.content_frame, text="原图", padding="10")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 裁剪预览框架
        self.right_frame = ttk.LabelFrame(self.content_frame, text="裁剪预览", padding="10")
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 确保左右框架内的画布也能填充空间
        self.left_frame.rowconfigure(0, weight=1)
        self.left_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)
        
        # 信息框架
        self.info_frame = ttk.Frame(self.preview_frame)
        self.info_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(10, 0))
        
        # 创建空的信息标签，使用换行显示，避免过长文本
        self.original_size_label = ttk.Label(self.info_frame, wraplength=400)
        self.original_size_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.crop_params_label = ttk.Label(self.info_frame, wraplength=600)
        self.crop_params_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 绑定键盘快捷键
        self.preview_window.bind("<Left>", lambda e: self.preview_prev_image())
        self.preview_window.bind("<Right>", lambda e: self.preview_next_image())
    
    def _update_preview_content(self, file_path, file_index):
        """更新预览窗口内容"""
        # 更新窗口标题
        self.preview_window.title(f"图片预览 ({file_index + 1}/{len(self.thumbnails)}) - {os.path.basename(file_path)}")
        
        # 更新导航按钮状态
        self.prev_btn.config(state="normal" if file_index > 0 else "disabled")
        self.next_btn.config(state="normal" if file_index < len(self.thumbnails) - 1 else "disabled")
        
        # 清空之前的内容
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
        # 加载原图
        self.current_preview_image = Image.open(file_path)
        width, height = self.current_preview_image.size
        self.current_preview_size = (width, height)
        
        # 计算合适的初始缩放比例，确保图片完全显示在画布内
        
        # 尝试更新组件，确保获取到准确的尺寸
        self.preview_window.update_idletasks()
        self.preview_frame.update_idletasks()
        self.left_frame.update_idletasks()
        self.right_frame.update_idletasks()
        
        # 获取框架尺寸，使用默认值作为 fallback
        frame_width = self.left_frame.winfo_width()
        frame_height = self.left_frame.winfo_height()
        
        # 如果框架还没有渲染好，使用更大的默认值
        if frame_width <= 0 or frame_height <= 0:
            # 使用更大的默认画布大小，避免第一张图片显示过小
            default_canvas_width = 800
            default_canvas_height = 600
            canvas_available_width = default_canvas_width
            canvas_available_height = default_canvas_height
        else:
            # 画布可用宽度和高度（减去滚动条空间）
            canvas_available_width = max(1, frame_width - 20)  # 20px for scrollbar
            canvas_available_height = max(1, frame_height - 20)  # 20px for scrollbar
        
        # 确保可用空间有一个合理的最小值
        canvas_available_width = max(canvas_available_width, 400)
        canvas_available_height = max(canvas_available_height, 300)
        
        # 计算缩放比例，确保图片完全显示
        if width > canvas_available_width or height > canvas_available_height:
            # 计算宽度和高度的缩放比例
            width_scale = canvas_available_width / width
            height_scale = canvas_available_height / height
            # 取较小的缩放比例，确保图片完全显示
            self.current_zoom_scale = min(width_scale, height_scale, 1.0)  # 最大缩放比例为1.0
        else:
            # 图片较小，使用实际大小
            self.current_zoom_scale = 1.0
        
        # 确保缩放比例不会导致零或负尺寸，同时设置一个合理的最小缩放比例
        self.current_zoom_scale = max(self.current_zoom_scale, 0.3)  # 最小缩放比例为0.3，避免图片显示过小
        
        # 显示原图和裁剪预览
        self._show_preview_images()
        
        # 更新裁剪信息
        top = self.top_var.get()
        bottom = self.bottom_var.get()
        left_crop = self.left_var.get()
        right_crop = self.right_var.get()
        unit = self.unit_var.get()
        self.original_size_label.config(text=f"原图尺寸: {width}x{height}px")
        self.crop_params_label.config(text=f"裁剪参数: 上{top}{unit}, 下{bottom}{unit}, 左{left_crop}{unit}, 右{right_crop}{unit}")
    
    def _show_preview_images(self):
        """显示预览图片，支持缩放"""
        if not self.current_preview_image:
            return
        
        img = self.current_preview_image
        width, height = self.current_preview_size
        
        # 获取裁剪参数
        top = self.top_var.get()
        bottom = self.bottom_var.get()
        left_crop = self.left_var.get()
        right_crop = self.right_var.get()
        unit = self.unit_var.get()
        
        # 计算裁剪区域
        if unit == '%':
            top_px = int(height * top / 100)
            bottom_px = int(height * bottom / 100)
            left_px = int(width * left_crop / 100)
            right_px = int(width * right_crop / 100)
        else:
            top_px = top
            bottom_px = bottom
            left_px = left_crop
            right_px = right_crop
        
        # 确保裁剪区域有效
        new_width = width - left_px - right_px
        new_height = height - top_px - bottom_px
        
        # 计算缩放后的尺寸，确保大于0
        scaled_width = max(1, int(width * self.current_zoom_scale))
        scaled_height = max(1, int(height * self.current_zoom_scale))
        
        # 显示原图，确保尺寸有效
        img_preview = img.resize((scaled_width, scaled_height), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_preview)
        
        # 清空原有控件
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        
        # 水平滚动条
        left_hscroll = ttk.Scrollbar(self.left_frame, orient=tk.HORIZONTAL)
        left_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 垂直滚动条
        left_vscroll = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL)
        left_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 画布大小固定，图片在内部滚动
        left_canvas = tk.Canvas(self.left_frame, width=800, height=600, bg="white",
                               xscrollcommand=left_hscroll.set, yscrollcommand=left_vscroll.set)
        left_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定滚动条
        left_hscroll.config(command=left_canvas.xview)
        left_vscroll.config(command=left_canvas.yview)
        
        # 绑定鼠标滚轮事件
        left_canvas.bind("<MouseWheel>", lambda e: left_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        left_canvas.bind("<Shift-MouseWheel>", lambda e: left_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 居中显示图片
        left_canvas.create_image(scaled_width//2, scaled_height//2, image=img_tk, anchor=tk.CENTER)
        left_canvas.image = img_tk
        
        # 设置滚动区域
        left_canvas.config(scrollregion=(0, 0, scaled_width, scaled_height))
        
        # 显示裁剪预览
        if new_width > 0 and new_height > 0:
            # 执行裁剪
            crop_box = (left_px, top_px, width - right_px, height - bottom_px)
            cropped_img = img.crop(crop_box)
            
            # 调整预览尺寸，确保大于0
            crop_scaled_width = max(1, int(new_width * self.current_zoom_scale))
            crop_scaled_height = max(1, int(new_height * self.current_zoom_scale))
            
            cropped_preview = cropped_img.resize((crop_scaled_width, crop_scaled_height), Image.LANCZOS)
            cropped_tk = ImageTk.PhotoImage(cropped_preview)
            
            # 清空原有控件
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            
            # 水平滚动条
            right_hscroll = ttk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL)
            right_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
            
            # 垂直滚动条
            right_vscroll = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL)
            right_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 画布大小固定，图片在内部滚动
            right_canvas = tk.Canvas(self.right_frame, width=800, height=600, bg="white",
                                   xscrollcommand=right_hscroll.set, yscrollcommand=right_vscroll.set)
            right_canvas.pack(fill=tk.BOTH, expand=True)
            
            # 绑定滚动条
            right_hscroll.config(command=right_canvas.xview)
            right_vscroll.config(command=right_canvas.yview)
            
            # 绑定鼠标滚轮事件
            right_canvas.bind("<MouseWheel>", lambda e: right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            right_canvas.bind("<Shift-MouseWheel>", lambda e: right_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
            
            # 居中显示图片
            right_canvas.create_image(crop_scaled_width//2, crop_scaled_height//2, image=cropped_tk, anchor=tk.CENTER)
            right_canvas.image = cropped_tk
            
            # 设置滚动区域
            right_canvas.config(scrollregion=(0, 0, crop_scaled_width, crop_scaled_height))
        else:
            # 显示错误信息
            ttk.Label(self.right_frame, text="裁剪参数无效，裁剪后的图片尺寸为0", foreground="red").pack(expand=True)
    
    def zoom_in(self):
        """放大图片"""
        if self.current_zoom_scale < self.max_zoom:
            self.current_zoom_scale += self.zoom_step
            self._show_preview_images()
    
    def zoom_out(self):
        """缩小图片"""
        if self.current_zoom_scale > self.min_zoom:
            self.current_zoom_scale -= self.zoom_step
            self._show_preview_images()
    
    def reset_zoom(self):
        """重置缩放比例"""
        self.current_zoom_scale = 1.0
        self._show_preview_images()
    
    def preview_prev_image(self):
        """预览上一张图片"""
        if self.current_preview_index > 0:
            self.current_preview_index -= 1
            file_path = self.thumbnails[self.current_preview_index]["file_path"]
            self.preview_image(file_path)
    
    def preview_next_image(self):
        """预览下一张图片"""
        if self.current_preview_index < len(self.thumbnails) - 1:
            self.current_preview_index += 1
            file_path = self.thumbnails[self.current_preview_index]["file_path"]
            self.preview_image(file_path)
    
    def on_canvas_scroll(self, event):
        """处理画布滚动事件"""
        # 将鼠标滚轮事件转发给主画布
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # 阻止事件冒泡
        return "break"
    
    def on_canvas_configure(self, event):
        """处理画布大小变化事件"""
        # 仅处理实际的大小变化事件，忽略其他配置事件
        if event.width > 0:
            # 更新画布宽度，确保缩略图框架始终填满画布
            self.canvas.itemconfig(self.thumbnail_window_id, width=self.canvas.winfo_width())
            
            # 避免无限循环调用和频繁重绘
            if not hasattr(self, '_last_canvas_width'):
                self._last_canvas_width = 0
            
            current_width = self.canvas.winfo_width()
            
            # 只有当画布宽度变化超过100像素时才重新绘制
            if abs(current_width - self._last_canvas_width) > 100:
                self._last_canvas_width = current_width
                
                # 如果当前是平铺模式，重新排列缩略图
                if self.current_view_mode == "tile" and self.thumbnails:
                    # 只在平铺模式下重新排列，避免列表模式下的不必要重绘
                    self._rearrange_tile_thumbnails()
    
    def set_view_mode(self, mode):
        """设置显示模式"""
        if self.current_view_mode == mode:
            return
        
        self.current_view_mode = mode
        # 更新按钮状态
        if mode == "list":
            self.list_mode_btn.config(style="Accent.TButton")
            self.tile_mode_btn.config(style="TButton")
        else:
            self.list_mode_btn.config(style="TButton")
            self.tile_mode_btn.config(style="Accent.TButton")
        
        # 重新渲染缩略图
        self._redraw_thumbnails()
    
    def toggle_filename_display(self):
        """切换是否显示文件名"""
        # 重新渲染缩略图
        self._redraw_thumbnails()
    
    def _rearrange_tile_thumbnails(self):
        """仅重新排列平铺模式下的缩略图，避免完全重绘"""
        if self.current_view_mode != "tile" or not self.thumbnails:
            return
        
        try:
            # 计算新的列数
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 0:
                # 根据画布宽度计算列数，每个缩略图宽度约为120px（含padding）
                cols = max(1, canvas_width // 120)
            else:
                cols = 4  # 默认4列
            
            # 确保所有列都有相同的权重
            for i in range(cols):
                self.thumbnail_frame.columnconfigure(i, weight=1)
            
            # 重新排列所有缩略图容器
            for index, thumb in enumerate(self.thumbnails):
                col = index % cols
                row = index // cols
                # 更新grid布局
                thumb["container"].grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # 更新滚动区域
            self.thumbnail_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            print(f"重新排列缩略图失败: {e}")
    
    def _redraw_thumbnails(self):
        """重新渲染缩略图"""
        # 保存当前文件列表
        files = [thumb["file_path"] for thumb in self.thumbnails]
        
        # 清空当前缩略图
        self.clear_files()
        
        # 重新添加所有文件
        for file_path in files:
            self.add_thumbnail(file_path)
    
    def add_thumbnail(self, file_path):
        """添加缩略图到列表"""
        try:
            # 获取当前索引
            current_index = len(self.thumbnails)
            
            if self.current_view_mode == "list":
                # 列表模式布局
                thumb_container = ttk.Frame(self.thumbnail_frame, padding="5")
                thumb_container.grid(row=current_index * 2, sticky=(tk.W, tk.E))
                thumb_container.columnconfigure(1, weight=1)
                
                # 缩略图画布
                thumb_canvas = tk.Canvas(thumb_container, width=80, height=80, bg="lightgray")
                thumb_canvas.grid(row=0, column=0, sticky=tk.NW, padx=(0, 10))
                
                # 直接在内存中生成并显示缩略图
                try:
                    with Image.open(file_path) as img:
                        # 计算缩放比例
                        img.thumbnail((80, 80), Image.LANCZOS)
                        
                        # 转换为PhotoImage
                        img_tk = ImageTk.PhotoImage(img)
                        
                        # 居中显示
                        thumb_canvas.create_image(40, 40, image=img_tk)
                        thumb_canvas.image = img_tk  # 保持引用
                except Exception as e:
                    # 如果生成缩略图失败，显示错误信息
                    thumb_canvas.create_text(40, 40, text="无法显示", fill="red")
                    img_tk = None
                    print(f"生成缩略图失败 {file_path}: {e}")
                
                if self.show_filename_var.get():
                    # 文件名和信息
                    info_frame = ttk.Frame(thumb_container)
                    info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
                    info_frame.columnconfigure(0, weight=1)
                    
                    # 文件名
                    filename = os.path.basename(file_path)
                    file_label = ttk.Label(info_frame, text=filename, anchor=tk.W, wraplength=400)
                    file_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    
                    # 文件路径（截断显示）
                    short_path = file_path if len(file_path) < 50 else "..." + file_path[-50:]
                    path_label = ttk.Label(info_frame, text=short_path, anchor=tk.W, foreground="gray", wraplength=400)
                    path_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
                    
                    # 绑定点击事件
                    file_label.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                    path_label.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                    info_frame.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                    info_frame.bind("<MouseWheel>", self.on_canvas_scroll)
                    file_label.bind("<MouseWheel>", self.on_canvas_scroll)
                    path_label.bind("<MouseWheel>", self.on_canvas_scroll)
                
                # 绑定点击事件
                thumb_container.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                thumb_canvas.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                
                # 绑定鼠标滚轮事件到所有控件，确保在任何位置都能滚动
                thumb_container.bind("<MouseWheel>", self.on_canvas_scroll)
                thumb_canvas.bind("<MouseWheel>", self.on_canvas_scroll)
                
                # 添加分隔线，设置正确的行号
                separator = None
                if current_index > 0:  # 不要在第一个缩略图前添加分隔线
                    separator = ttk.Separator(self.thumbnail_frame, orient=tk.HORIZONTAL)
                    separator.grid(row=current_index * 2 - 1, column=0, sticky=(tk.W, tk.E), pady=5)
                    separator.bind("<MouseWheel>", self.on_canvas_scroll)
            else:
                # 平铺模式布局，平铺模式不使用分隔线
                separator = None
                
                # 计算列和行，根据可用宽度动态调整列数
                canvas_width = self.canvas.winfo_width()
                if canvas_width > 0:
                    # 根据画布宽度计算列数，每个缩略图宽度约为120px（含padding）
                    cols = max(1, canvas_width // 120)
                else:
                    cols = 4  # 默认4列
                
                col = current_index % cols
                row = current_index // cols
                
                # 确保所有列都有相同的权重
                for i in range(cols):
                    self.thumbnail_frame.columnconfigure(i, weight=1)
                
                thumb_container = ttk.Frame(self.thumbnail_frame, padding="5")
                thumb_container.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
                thumb_container.columnconfigure(0, weight=1)
                
                # 缩略图画布
                # 动态调整缩略图大小，填充可用空间
                thumb_width = 100
                thumb_height = 100
                
                thumb_canvas = tk.Canvas(thumb_container, width=thumb_width, height=thumb_height, bg="lightgray")
                thumb_canvas.grid(row=0, column=0, sticky=tk.NW)
                
                # 直接在内存中生成并显示缩略图
                try:
                    with Image.open(file_path) as img:
                        # 计算缩放比例
                        img.thumbnail((thumb_width, thumb_height), Image.LANCZOS)
                        
                        # 转换为PhotoImage
                        img_tk = ImageTk.PhotoImage(img)
                        
                        # 居中显示
                        thumb_canvas.create_image(thumb_width//2, thumb_height//2, image=img_tk)
                        thumb_canvas.image = img_tk  # 保持引用
                except Exception as e:
                    # 如果生成缩略图失败，显示错误信息
                    thumb_canvas.create_text(thumb_width//2, thumb_height//2, text="无法显示", fill="red")
                    img_tk = None
                    print(f"生成缩略图失败 {file_path}: {e}")
                
                if self.show_filename_var.get():
                    # 文件名
                    filename = os.path.basename(file_path)
                    file_label = ttk.Label(thumb_container, text=filename, anchor=tk.CENTER, wraplength=thumb_width)
                    file_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
                    
                    # 绑定点击事件
                    file_label.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                    file_label.bind("<MouseWheel>", self.on_canvas_scroll)
                
                # 绑定点击事件
                thumb_container.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                thumb_canvas.bind("<Button-1>", lambda e, fp=file_path: self.preview_image(fp))
                
                # 绑定鼠标滚轮事件到所有控件，确保在任何位置都能滚动
                thumb_container.bind("<MouseWheel>", self.on_canvas_scroll)
                thumb_canvas.bind("<MouseWheel>", self.on_canvas_scroll)
            
            # 存储缩略图信息
            self.thumbnails.append({
                "file_path": file_path,
                "container": thumb_container,
                "canvas": thumb_canvas,
                "image": img_tk,
                "separator": separator
            })
            
            # 更新滚动区域
            self.thumbnail_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            print(f"添加缩略图失败: {e}")
    
    def clear_files(self):
        """清空文件列表"""
        # 清除所有缩略图和分隔线
        for thumb in self.thumbnails:
            thumb["container"].destroy()
            # 销毁分隔线
            if thumb.get("separator"):
                thumb["separator"].destroy()
        self.thumbnails.clear()
        
        # 更新滚动区域
        self.thumbnail_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.update_status("文件列表已清空")
    
    def browse_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def start_processing(self):
        """开始处理"""
        # 验证文件列表
        if self.file_listbox.size() == 0:
            messagebox.showwarning("警告", "请先添加要处理的图片文件")
            return
        
        # 验证裁剪参数
        top = self.top_var.get()
        bottom = self.bottom_var.get()
        left = self.left_var.get()
        right = self.right_var.get()
        
        if top + bottom >= 100 or left + right >= 100:
            messagebox.showwarning("警告", "裁剪百分比总和不能超过100%")
            return
        
        # 验证输出目录
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {e}")
            return
        
        # 获取文件列表
        files = [thumb["file_path"] for thumb in self.thumbnails]
        
        # 更新界面状态
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_bar.grid()
        self.progress_var.set(0)
        self.update_status("开始处理...")
        
        # 创建处理对象
        self.processor = ImageProcessor(
            files, top, bottom, left, right,
            output_dir, self.format_var.get(), self.quality_var.get(),
            progress_callback=self.update_progress,
            file_callback=self.on_file_processed,
            finish_callback=self.on_processing_finished
        )
        
        # 在新线程中处理
        self.processing_thread = threading.Thread(target=self.processor.process_all)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """停止处理"""
        if self.processor:
            self.processor.stop()
        
        self.reset_ui()
        self.update_status("处理已停止")
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def on_file_processed(self, file_path, success, error_msg):
        """单个文件处理完成"""
        filename = os.path.basename(file_path)
        if success:
            self.update_status(f"已完成: {filename}")
        else:
            self.update_status(f"失败: {filename} - {error_msg}")
    
    def on_processing_finished(self, results):
        """所有文件处理完成"""
        self.reset_ui()
        
        msg = f"处理完成！\n成功: {results['success']} 个\n失败: {results['failed']} 个"
        if results['failed'] > 0:
            messagebox.showwarning("处理完成", msg)
        else:
            messagebox.showinfo("处理完成", msg)
        
        self.update_status("处理完成")
    
    def reset_ui(self):
        """重置界面状态"""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_bar.grid_remove()
    
    def on_unit_change(self, event):
        """处理裁剪单位切换"""
        unit = self.unit_var.get()
        
        # 更新标签文本
        self.top_label.config(text=f"上边裁剪({unit}):")
        self.bottom_label.config(text=f"下边裁剪({unit}):")
        self.left_label.config(text=f"左边裁剪({unit}):")
        self.right_label.config(text=f"右边裁剪({unit}):")
        
        # 更新Spinbox范围
        self.update_spinbox_ranges()
        
        # 保存设置
        self.save_settings()
    
    def update_spinbox_ranges(self):
        """根据裁剪单位更新Spinbox的取值范围"""
        unit = self.unit_var.get()
        if unit == '%':
            # 百分比模式，范围0-100
            self.top_spin.config(from_=0, to=100)
            self.bottom_spin.config(from_=0, to=100)
            self.left_spin.config(from_=0, to=100)
            self.right_spin.config(from_=0, to=100)
        else:
            # 像素模式，范围0-10000
            self.top_spin.config(from_=0, to=10000)
            self.bottom_spin.config(from_=0, to=10000)
            self.left_spin.config(from_=0, to=10000)
            self.right_spin.config(from_=0, to=10000)
    
    def open_output_folder(self):
        """打开输出文件夹"""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_dir)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(['open', output_dir] if sys.platform == 'darwin' else ['xdg-open', output_dir])
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件夹: {e}")
        else:
            messagebox.showwarning("警告", "输出文件夹不存在")
    
    def browse_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
            self.save_settings()
    
    def save_settings(self):
        """保存设置"""
        self.settings = {
            "output_dir": self.output_dir_var.get(),
            "crop_unit": self.unit_var.get(),
            "crop_settings": {
                "top": self.top_var.get(),
                "bottom": self.bottom_var.get(),
                "left": self.left_var.get(),
                "right": self.right_var.get()
            },
            "output_format": self.format_var.get(),
            "quality": self.quality_var.get()
        }
        ConfigManager.save_settings(self.settings)
    
    def start_processing(self):
        """开始处理"""
        # 验证文件列表
        if len(self.thumbnails) == 0:
            messagebox.showwarning("警告", "请先添加要处理的图片文件")
            return
        
        # 验证裁剪参数
        top = self.top_var.get()
        bottom = self.bottom_var.get()
        left = self.left_var.get()
        right = self.right_var.get()
        unit = self.unit_var.get()
        
        if unit == '%':
            if top + bottom >= 100 or left + right >= 100:
                messagebox.showwarning("警告", "裁剪百分比总和不能超过100%")
                return
        
        # 验证输出目录
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {e}")
            return
        
        # 获取文件列表
        files = [thumb["file_path"] for thumb in self.thumbnails]
        
        # 更新界面状态
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_bar.grid()
        self.progress_var.set(0)
        self.update_status("开始处理...")
        
        # 保存设置
        self.save_settings()
        
        # 创建处理对象
        self.processor = ImageProcessor(
            files, top, bottom, left, right,
            output_dir, self.format_var.get(), self.quality_var.get(),
            crop_unit=unit,
            progress_callback=self.update_progress,
            file_callback=self.on_file_processed,
            finish_callback=self.on_processing_finished
        )
        
        # 在新线程中处理
        self.processing_thread = threading.Thread(target=self.processor.process_all)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    """主函数"""
    root = tk.Tk()
    app = ImageCropperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()