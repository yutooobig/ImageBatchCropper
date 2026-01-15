# ImageBatchCropper - 图片批量裁剪工具

一个简单易用的图片批量裁剪工具，支持多种裁剪方式和输出格式。

## 功能特点

- 🔄 **批量处理**：一次性裁剪多张图片
- 📐 **灵活裁剪**：支持百分比或像素裁剪
- 🎨 **多种格式**：JPG、PNG等输出格式
- 💾 **配置保存**：自动保存用户设置
- ⚡ **高效处理**：多线程加速处理

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main_optimized.py
```

### 打包版本
已打包的可执行文件位于 `dist/` 目录：
- `ImageBatchCropper.exe` - 图形界面版本
- `ImageBatchCropperCmd.exe` - 命令行版本

## 使用方法

1. 选择图片文件夹
2. 设置裁剪参数（单位、裁剪值）
3. 选择输出文件夹
4. 点击开始裁剪

## 项目结构

```
ImageBatchCropper/
├── main_optimized.py           # 主程序
├── cropper_config.json         # 配置文件
├── requirements.txt            # 依赖文件
└── README.md                   # 说明文档
```

## 技术栈

- Python 3.8+
- Tkinter (图形界面)
- Pillow (图片处理)

## 许可证

MIT License