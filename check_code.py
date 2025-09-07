import os
import re

def find_chinese_identifiers(base_path="."):
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]+")
    results = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        # 跳过注释行
                        if line.strip().startswith("#"):
                            continue
                        # 跳过字符串中的中文（UI 文案允许）
                        if re.search(r"['\"].*[\u4e00-\u9fff].*['\"]", line):
                            continue
                        # 检查剩余部分是否有中文
                        if chinese_pattern.search(line):
                            results.append((file_path, i, line.strip()))

    return results


if __name__ == "__main__":
    base_dirs = ["apps", "data_io"]
    all_results = []
    for d in base_dirs:
        if os.path.exists(d):
            all_results.extend(find_chinese_identifiers(d))

    if not all_results:
        print("✅ 未发现中文命名，命名清理已完成！")
    else:
        print("⚠️ 发现可能的中文命名：")
        for file, line_no, content in all_results:
            print(f"{file}:{line_no} → {content}")
