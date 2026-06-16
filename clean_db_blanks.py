import sqlite3

db_path = r"D:\lhd051\backend\app\dried_flowers.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 清理 flower_materials 表中的空字符串
print("清理 flower_materials 表中的空字符串...")
cursor.execute("UPDATE flower_materials SET category = NULL WHERE category = '' OR TRIM(category) = ''")
print(f"  清理 category: {cursor.rowcount} 行")
cursor.execute("UPDATE flower_materials SET color = NULL WHERE color = '' OR TRIM(color) = ''")
print(f"  清理 color: {cursor.rowcount} 行")
cursor.execute("UPDATE flower_materials SET fresh_level = NULL WHERE fresh_level = '' OR TRIM(fresh_level) = ''")
print(f"  清理 fresh_level: {cursor.rowcount} 行")

# 查询当前去重的颜色值
cursor.execute("SELECT DISTINCT color FROM flower_materials WHERE color IS NOT NULL AND TRIM(color) != '' ORDER BY color")
colors = [r[0] for r in cursor.fetchall()]
print(f"\n清理后去重的颜色值 ({len(colors)} 个): {colors}")

cursor.execute("SELECT DISTINCT category FROM flower_materials WHERE category IS NOT NULL AND TRIM(category) != '' ORDER BY category")
cats = [r[0] for r in cursor.fetchall()]
print(f"清理后去重的分类值 ({len(cats)} 个): {cats}")

conn.commit()
conn.close()
print("\n✅ 数据库清理完成！")
