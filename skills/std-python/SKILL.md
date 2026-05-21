---
name: std-python
description: 提供 Python 编码规范（基于 PEP 8 与 Google Python Style Guide）。当编写或 review Python 代码（.py 文件）时使用。
---

# Python 编码规范

> 基于 PEP 8 与 Google Python Style Guide，使用 Python 3.10+。

## 规范等级定义

| 等级 | 定义 |
|------|------|
| **必须（Mandatory）** | 代码扫描工具应视为错误，必须修复 |
| **推荐（Preferable）** | 理应采用，特殊情况可例外 |
| **可选（Optional）** | 可参考，自行决定 |

## 核心规则速查

| 类别 | 必须遵守 |
|------|----------|
| **版本** | Python 3.10+，合理使用 match-case、类型别名等新特性 |
| **格式化** | 4 空格缩进，禁止 Tab；行宽 79 字符（注释/文档字符串 72） |
| **命名** | 变量/函数 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE_CASE` |
| **导入** | 分组排列（标准库 / 第三方 / 本地），组间空行，禁止通配符导入 |
| **类型提示** | 函数参数和返回值必须添加类型提示，使用内置泛型（`list[str]` 而非 `List[str]`） |
| **错误处理** | 捕获具体异常，禁止裸 `except`；优先 EAFP 风格 |
| **资源管理** | 使用 `with` 语句（上下文管理器）管理文件、锁等资源 |
| **文档字符串** | 公共模块、类、函数必须有 docstring，使用 Sphinx/reStructuredText 格式 |
| **复杂度** | 嵌套不超过 3 层；单一函数关注点不超过 3 个；逻辑运算符链不超过 3 个 |
| **惯用法** | 优先使用推导式、`enumerate()`、`zip()`、`any()`/`all()`、`collections` 模块 |

## 详细规范

### 导入规范

```python
# 正确：分组 + 组间空行
import os
import sys

import requests

from myproject import utils
```

- 禁止 `from module import *`
- 优先绝对导入，避免相对导入
- 每行只导入一个库（标准库除外）

### 类型提示

```python
# 正确：使用内置泛型（Python 3.10+）
def process(items: list[str], limit: int = 10) -> dict[str, int]:
    ...

# 正确：使用 TypeAlias
type Point = tuple[float, float]

# 正确：使用 TypedDict
class UserInfo(TypedDict):
    name: str
    age: int
```

### 文档字符串

```python
def fetch_data(url: str, timeout: int = 30) -> dict[str, Any]:
    """
    从指定 URL 获取 JSON 数据。

    :param url: 请求的目标地址
    :param timeout: 请求超时时间（秒）
    :return: 解析后的 JSON 字典
    :raises RequestException: 网络请求失败时抛出
    """
```

### 错误处理

```python
# 正确：捕获具体异常
try:
    result = parse_json(raw)
except json.JSONDecodeError as e:
    logger.warning("JSON 解析失败: %s", e)
    result = {}

# 错误：裸 except
try:
    result = parse_json(raw)
except:  # 禁止
    result = {}
```

### Pythonic 惯用法

```python
# 推荐使用推导式（逻辑简单时）
active_names = [u.name for u in users if u.is_active]

# 推荐使用 enumerate
for idx, item in enumerate(items):
    ...

# 推荐使用 contextlib
with contextlib.suppress(FileNotFoundError):
    os.remove(temp_file)

# 推荐使用 collections
from collections import defaultdict, Counter
counts = Counter(items)
graph = defaultdict(list)
```

### 复杂度控制

```python
# 避免：超过 3 层嵌套
for item in items:
    if item.active:
        for sub in item.children:
            if sub.valid:
                process(sub)  # 3 层嵌套，已达上限

# 推荐：提前返回 / 提取函数减少嵌套
def process_valid_children(item: Item) -> None:
    for sub in item.children:
        if not sub.valid:
            continue
        _process_single(sub)

for item in items:
    if not item.active:
        continue
    process_valid_children(item)
```

### 上下文感知策略

| 代码类型 | 优化侧重 |
|----------|----------|
| **业务逻辑** | 强调可读性和可维护性，允许适当冗余 |
| **库/框架** | 适度追求性能和优雅，保持 API 清晰性 |
| **数据科学/脚本** | 可接受更高简洁性，保持基本可读性 |
