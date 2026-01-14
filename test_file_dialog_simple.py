#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import webview
    import threading
    import time
    
    print("pywebview imported successfully")
    
    # 创建一个简单的窗口
    window = webview.create_window("Test File Dialog", html="<h1>Test</h1>", width=400, height=200)
    
    def test_open_dialog():
        try:
            print("尝试打开文件对话框...")
            # 给窗口一点时间初始化
            time.sleep(1)
            
            # 使用简化的文件类型过滤器格式
            file_types = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            
            result = window.create_file_dialog(
                dialog_type=webview.OPEN_DIALOG,
                allow_multiple=True,
                file_types=file_types
            )
            
            print(f"文件对话框返回结果: {result}")
            
            # 关闭窗口
            window.destroy()
            
        except Exception as e:
            print(f"打开文件对话框时出错: {e}")
            import traceback
            traceback.print_exc()
            window.destroy()
    
    # 在新线程中测试，因为webview.start()会阻塞
    threading.Thread(target=test_open_dialog).start()
    
    # 运行webview
    webview.start()
    
    print("测试完成")
    
except Exception as e:
    print(f"测试过程中出错: {e}")
    import traceback
    traceback.print_exc()
