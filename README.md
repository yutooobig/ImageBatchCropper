# ImageBatchCropper - 图片批量裁剪工具

一个图片批量裁剪工具，支持多种裁剪方式和输出格式。

## 功能特点

- 🔄 **批量处理**：支持一次性裁剪多张图片
- 📐 **灵活裁剪**：支持按百分比或像素进行裁剪
- 🎨 **多种格式**：支持多种输出图片格式（JPG、PNG等）
- 💾 **质量控制**：可调整输出图片质量
- ⚡ **高效处理**：使用多线程加速图片处理

## 安装和依赖

### 系统要求

- Python 3.8+
- Windows/Linux/macOS

### 安装方法

1. 克隆或下载本仓库到本地

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：

```bash
python main_optimized.py
```

2. 选择要裁剪的图片文件夹

3. 设置裁剪参数：
   - 选择裁剪单位（百分比/像素）
   - 设置上、下、左、右裁剪值
   - 选择输出格式和质量

4. 选择输出文件夹

5. 点击「开始裁剪」按钮开始处理

6. 等待处理完成，查看结果

## 项目结构

```
ImageBatchCropper/
├── main_optimized.py       # 主程序文件
├── cropper_config.json     # 配置文件
├── requirements.txt        # 依赖文件
├── .gitignore              # Git忽略文件
└── README.md               # 项目说明文档
```

## 配置说明

配置文件 `cropper_config.json` 会自动保存用户的设置，包括：

```json
{
  "output_dir": "~/Pictures/Cropped",  // 默认输出目录
  "crop_unit": "%",                    // 裁剪单位（%或px）
  "crop_settings": {
    "top": 0,                           // 顶部裁剪值
    "bottom": 0,                        // 底部裁剪值
    "left": 0,                          // 左侧裁剪值
    "right": 0                          // 右侧裁剪值
  },
  "output_format": "JPG",              // 输出格式
  "quality": 90                         // 输出质量
}
```

## 技术栈

- **Python 3.8+**：主要开发语言
- **Tkinter**：图形用户界面
- **Pillow (PIL)**：图片处理库
- **JSON**：配置文件处理
- **多线程**：并发图片处理

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request，共同改进这个工具！

## 联系方式

如有问题或建议，欢迎通过 GitHub Issues 反馈。

---

**Enjoy using ImageBatchCropper!** 🎉