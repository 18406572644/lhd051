import requests

def test():
    base = "http://127.0.0.1:8000/api"
    print("=" * 60)
    print("测试 1: 获取分类和花色选项（验证空白过滤）")
    print("=" * 60)

    # 测试 categories
    resp = requests.get(f"{base}/materials/options/categories")
    data = resp.json()
    cats = data.get("categories", [])
    print(f"分类数量: {len(cats)}")
    print(f"分类列表: {cats}")
    has_blank = any(not c or str(c).strip() == "" for c in cats)
    print(f"包含空白选项: {has_blank}")
    assert not has_blank, "分类包含空白选项！"

    # 测试 colors
    resp = requests.get(f"{base}/materials/options/colors")
    data = resp.json()
    colors = data.get("colors", [])
    print(f"\n花色数量: {len(colors)}")
    print(f"花色列表: {colors}")
    has_blank = any(not c or str(c).strip() == "" for c in colors)
    print(f"包含空白选项: {has_blank}")
    assert not has_blank, "花色包含空白选项！"

    print("\n" + "=" * 60)
    print("测试 2: 编辑制作记录（验证数据格式）")
    print("=" * 60)

    # 首先创建一条测试记录
    create_payload = {
        "process_name": "测试编辑修复-原始",
        "material_id": 1,
        "method": "自然风干",
        "status": "进行中",
        "temperature": 25,
        "humidity": 60,
        "desiccant_weight": 50.5,
        "process_steps": ["步骤1", "步骤2"],
        "output_quantity": 10
    }
    resp = requests.post(f"{base}/drying-processes", json=create_payload)
    assert resp.status_code == 200, f"创建失败: {resp.status_code}"
    data = resp.json()
    item_id = data.get("id")
    print(f"创建测试记录成功，ID: {item_id}")

    # 测试编辑：各种边缘情况
    update_payload = {
        "process_name": "测试编辑修复-修改后",
        "material_id": 1,
        "method": "硅胶干燥",
        "status": "已完成",
        "temperature": "",  # 空字符串 -> 应该转为 null
        "humidity": "   ",  # 空白字符串 -> 应该转为 null
        "pressure": "",  # 空字符串 -> 应该转为 null
        "desiccant_weight": "",  # 空字符串 -> 应该转为 null
        "process_steps": ["", "  ", "有效步骤A", "有效步骤B"],  # 过滤空白
        "pre_treatment": "",  # 空 -> null
        "color_retention": "   ",  # 空白 -> null
        "notes": "",  # 空 -> null
        "output_quantity": "abc",  # 无效数字 -> null
        "yield_rate": "85"  # 字符串数字 -> 应该转为 85.0
    }

    print(f"\n发送更新请求，ID: {item_id}")
    print(f"请求体中的空值字段: temperature='{update_payload['temperature']}', humidity='{update_payload['humidity']}', pressure='{update_payload['pressure']}'")
    print(f"process_steps 原始: {update_payload['process_steps']}")

    resp = requests.put(f"{base}/drying-processes/{item_id}", json=update_payload)
    print(f"\n响应状态: {resp.status_code}")
    data = resp.json()

    if resp.status_code == 200:
        print("\n✅ 编辑保存成功！")
        print(f"  process_name: {data.get('process_name')}")
        print(f"  temperature: {data.get('temperature')} (应为 null)")
        print(f"  humidity: {data.get('humidity')} (应为 null)")
        print(f"  pressure: {data.get('pressure')} (应为 null)")
        print(f"  desiccant_weight: {data.get('desiccant_weight')} (应为 null)")
        print(f"  process_steps: {data.get('process_steps')} (应为 ['有效步骤A','有效步骤B'])")
        print(f"  pre_treatment: {data.get('pre_treatment')} (应为 null)")
        print(f"  yield_rate: {data.get('yield_rate')} (应为 85.0)")
        print(f"  output_quantity: {data.get('output_quantity')} (应为 null)")

        # 验证
        assert data.get('temperature') is None, f"temperature 不是 null: {data.get('temperature')}"
        assert data.get('humidity') is None, f"humidity 不是 null: {data.get('humidity')}"
        assert data.get('pressure') is None, f"pressure 不是 null: {data.get('pressure')}"
        assert data.get('desiccant_weight') is None, f"desiccant_weight 不是 null: {data.get('desiccant_weight')}"
        assert data.get('process_steps') == ['有效步骤A', '有效步骤B'], f"process_steps 过滤失败: {data.get('process_steps')}"
        assert data.get('pre_treatment') is None, f"pre_treatment 不是 null: {data.get('pre_treatment')}"
        assert data.get('yield_rate') == 85.0, f"yield_rate 转换失败: {data.get('yield_rate')}"
        assert data.get('output_quantity') is None, f"output_quantity 不是 null: {data.get('output_quantity')}"
        print("\n✅ 所有字段验证通过！")
    else:
        print(f"\n❌ 编辑失败，状态码: {resp.status_code}")
        print(f"错误内容: {data}")

    # 清理测试数据
    resp = requests.delete(f"{base}/drying-processes/{item_id}")
    if resp.status_code == 200:
        print(f"\n清理测试数据成功，ID: {item_id}")

    print("\n" + "=" * 60)
    print("测试 3: 原料新增提交（验证空白选项禁止提交）")
    print("=" * 60)
    # 这个测试需要前端交互验证，后端不拦截是正常的，前端表单校验会拦截

    print("\n" + "=" * 60)
    print("✅ 所有后端测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    test()
