# 影片場景分割工具

這是一個基於 Python 的工具，使用 PySceneDetect 自動偵測並分割影片場景。

[English Ver.](docs/README.md)

## 功能特色

- **處理選項**：
  - 單一影片檔案處理
  - 批次處理多個檔案
  - 資料夾影片選擇
  - 進度追蹤與視覺化指示

- **場景偵測**：
  - 自適應偵測與可調整閾值
  - 支援多種影片格式（mp4、mov、mkv、avi、wmv）
  - 最小場景長度控制
  - 即時進度顯示

## 系統需求

- Python 3.x
- PySceneDetect 函式庫
- FFmpeg（4.0 版或更高）

## 設定檔

工具使用設定檔（`scenedetect.cfg`）包含以下主要設定：

- 場景偵測閾值：17（預設值）
- 最小場景長度：0.6 秒
- 輸出目錄設定
- 處理參數設定

## 使用方式

### 單一檔案處理
```bash
python video_scene_detector.py -f video.mp4
```

### 批次處理
```bash
python video_scene_detector.py -d /path/to/videos
```

## 輸出格式

檔案會依照以下命名規則儲存：
```
原始檔名-scene-01.mp4
原始檔名-scene-02.mp4
...
```

## 效能特色

- 支援平行處理
- 記憶體最佳化操作
- CPU 多核心處理
- 執行緒安全操作

## 錯誤處理

- 全面性錯誤檢查
- 詳細記錄系統
- 操作狀態追蹤
- 失敗操作復原選項

## 授權條款

本工具採用 MIT 授權條款。