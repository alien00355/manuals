# 📝 开发日志

项目开发过程记录，按日期归档。

## 使用方式

### 自动创建今日日志
```bash
python devlog/log.py
```
每天首次运行时自动基于模板创建当天的日志文件。

### 查看待办汇总
```bash
python devlog/log.py --summary
```

### 查看最近日志
```bash
python devlog/log.py --recent 5
```

## 日志规范

- 每天一个文件，文件名格式：`YYYY-MM-DD.md`
- 按「已完成 / 进行中 / 待办 / 备注」四个分区记录
- 每项用 `- ` 开头，保持简洁明了
