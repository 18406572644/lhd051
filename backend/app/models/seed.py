from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from app.database import AsyncSessionLocal
from app.models import (
    FlowerMaterial, DryingProcess, Specimen, TechniqueNote,
    DesignPlan, ProductImage, SharePost, MaterialConsumption
)
import random


async def seed_demo_data():
    async with AsyncSessionLocal() as db:
        material_count = await db.scalar(select(func.count(FlowerMaterial.id)))
        if material_count > 0:
            return

        materials = [
            {"name": "玫瑰·戴安娜", "scientific_name": "Rosa Diana", "category": "玫瑰", "color": "豆沙粉",
             "origin": "云南昆明", "quantity": 50, "unit": "枝", "fresh_level": "A",
             "storage_method": "冷藏2-4℃，斜剪根部浸水", "supplier": "花语花坊",
             "purchase_date": date.today() - timedelta(days=2),
             "image_url": "https://images.unsplash.com/photo-1518882605630-8eb515896b8f?w=400",
             "notes": "花瓣厚实，适合压花和倒挂风干"},
            {"name": "满天星·百万星", "scientific_name": "Gypsophila paniculata", "category": "满天星", "color": "奶白",
             "origin": "云南斗南", "quantity": 3, "unit": "扎", "fresh_level": "A",
             "storage_method": "深水养护，避免阳光直射", "supplier": "云南花农直供",
             "purchase_date": date.today() - timedelta(days=3),
             "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400",
             "notes": "花型细小，适合做配花和干燥剂法"},
            {"name": "尤加利叶·圆叶", "scientific_name": "Eucalyptus polyanthemos", "category": "尤加利", "color": "银绿",
             "origin": "澳洲进口", "quantity": 10, "unit": "枝", "fresh_level": "B",
             "storage_method": "倒挂阴干，无需浸水", "supplier": "进口花材商行",
             "purchase_date": date.today() - timedelta(days=5),
             "image_url": "https://images.unsplash.com/photo-1612098437313-e52a35c500b2?w=400",
             "notes": "香气浓郁，风干后可做香薰搭配"},
            {"name": "绣球·无尽夏", "scientific_name": "Hydrangea macrophylla", "category": "绣球", "color": "浅蓝",
             "origin": "浙江海宁", "quantity": 8, "unit": "枝", "fresh_level": "A",
             "storage_method": "深水养护，叶面喷水", "supplier": "绣球花园",
             "purchase_date": date.today() - timedelta(days=1),
             "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400",
             "notes": "花朵饱满，建议干燥剂法保型"},
            {"name": "薰衣草·英国", "scientific_name": "Lavandula angustifolia", "category": "薰衣草", "color": "浅紫",
             "origin": "新疆伊犁", "quantity": 2, "unit": "扎", "fresh_level": "A",
             "storage_method": "倒挂通风处阴干", "supplier": "伊犁花田",
             "purchase_date": date.today() - timedelta(days=7),
             "image_url": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=400",
             "notes": "香气怡人，适合香薰包和花束"},
            {"name": "小雏菊", "scientific_name": "Bellis perennis", "category": "其他", "color": "浅黄白",
             "origin": "本地花市", "quantity": 20, "unit": "枝", "fresh_level": "B",
             "storage_method": "浅水养护", "supplier": "街角花店",
             "purchase_date": date.today() - timedelta(days=4),
             "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400",
             "notes": "小巧可爱，适合压花相框"},
        ]

        created_materials = []
        for m in materials:
            item = FlowerMaterial(**m)
            db.add(item)
            created_materials.append(item)
        await db.flush()

        drying_methods = ["自然风干", "倒挂", "干燥剂", "微波炉", "压花"]
        statuses = ["进行中", "已完成", "已完成", "已完成", "失败"]
        qualities = ["优", "良", "中", "差"]

        processes = []
        for i, mat in enumerate(created_materials):
            method = drying_methods[i % len(drying_methods)]
            status = statuses[i % len(statuses)]
            duration = random.uniform(2, 168)
            start = datetime.now() - timedelta(hours=duration)
            end = start + timedelta(hours=duration) if status != "进行中" else None

            proc = DryingProcess(
                material_id=mat.id,
                process_name=f"{mat.name} · {method}",
                method=method,
                start_date=start,
                end_date=end,
                duration_hours=duration,
                temperature=random.uniform(18, 60) if method in ["干燥剂", "微波炉"] else random.uniform(18, 28),
                humidity=random.uniform(30, 70),
                pressure=f"{random.randint(500, 2000)}g" if method == "压花" else None,
                pre_treatment="选取半开状态花材，斜剪根部，去除多余叶片，用吸水纸轻擦花头露水",
                process_steps=[
                    {"step": 1, "desc": "选材：挑选形态完好、半开的花朵"},
                    {"step": 2, "desc": "预处理：清洁花材，整理造型"},
                    {"step": 3, "desc": "制作：按所选方法进行脱水处理"},
                    {"step": 4, "desc": "检查：定时观察干燥状态"},
                    {"step": 5, "desc": "完成：确认完全干燥后取出保存"}
                ],
                status=status,
                color_retention=qualities[i % len(qualities)],
                shape_retention=qualities[(i + 1) % len(qualities)],
                yield_rate=random.uniform(60, 95),
                output_quantity=mat.quantity * random.uniform(0.7, 0.95),
                output_unit=mat.unit,
                notes=f"第{i+1}次制作记录，整体效果{'满意' if i%3==0 else '有待改进'}"
            )
            db.add(proc)
            processes.append(proc)
        await db.flush()

        specimen_categories = ["单枝", "花束", "压花", "香薰", "摆件", "礼盒"]
        frame_styles = ["原木", "复古金", "极简白", "黑色", "透明亚克力"]
        statuses_s = ["完好", "完好", "完好", "微损", "已赠出"]

        specimens = []
        for i, proc in enumerate(processes):
            if proc.status != "已完成":
                continue
            cat = specimen_categories[i % len(specimen_categories)]
            specimen = Specimen(
                drying_process_id=proc.id,
                name=f"{proc.process_name} · {cat}",
                category=cat,
                display_code=f"SP{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                production_date=proc.end_date.date() if proc.end_date else date.today(),
                shelf_life_months=random.randint(6, 36),
                preservation_method="密封盒+干燥剂包，避免阳光直射，定期用软毛刷除尘",
                frame_size=f"{random.choice(['A4', 'A5', '8寸', '10寸', '12寸'])}",
                frame_style=frame_styles[i % len(frame_styles)],
                description=f"精心制作的{cat}作品，采用{proc.method}工艺，保留了{proc.material.name if proc.material else '花材'}最美的姿态。花瓣层次分明，色彩自然过渡，是家居装饰和收藏的绝佳选择。",
                tags=["花艺", "干花", cat, proc.method, "手工制作"],
                image_url=proc.material.image_url if proc.material else None,
                gallery_images=[
                    "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=600",
                    "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=600",
                    "https://images.unsplash.com/photo-1469521669194-babb45599def?w=600"
                ],
                is_featured=(i % 3 == 0),
                is_shared=(i % 2 == 0),
                location=f"陈列架A-{i+1}",
                status=statuses_s[i % len(statuses_s)],
                like_count=random.randint(0, 128),
                view_count=random.randint(10, 500)
            )
            db.add(specimen)
            specimens.append(specimen)
        await db.flush()

        note_categories = ["采花", "预处理", "风干", "保色", "装裱", "搭配"]
        difficulties = ["入门", "进阶", "精通"]

        notes_data = [
            {"title": "最佳采花时间指南", "category": "采花", "difficulty": "入门",
             "content": "选择晴天上午9-11点采集，此时花朵露水已干但仍保持饱满状态。避免在雨天或正午烈日下采花。挑选半开状态的花朵，这样的花材在干燥过程中能继续微张，形态最佳。"},
            {"title": "玫瑰倒挂风干全攻略", "category": "风干", "difficulty": "入门",
             "content": "1. 选择半开的玫瑰，去除下部叶片；2. 每5-7枝用橡皮筋扎成一束；3. 倒挂在通风干燥、避免阳光直射的地方；4. 温度20-25℃，湿度40-50%最佳；5. 2-4周完全干燥后即可取下。注意：干燥过程中不要触碰花瓣，以免损伤。"},
            {"title": "硅胶干燥剂保色技巧", "category": "保色", "difficulty": "进阶",
             "content": "使用食品级硅胶干燥剂，可重复使用。先在密封盒底部铺2-3cm干燥剂，放入整理好造型的花材，再缓缓倒入干燥剂覆盖每片花瓣，盖紧密封。玫瑰约3-5天，绣球约5-7天。完成后用软毛刷轻轻去除残留干燥剂。"},
            {"title": "压花相框装裱教程", "category": "装裱", "difficulty": "进阶",
             "content": "1. 准备无酸卡纸、热熔胶、镊子、相框；2. 先在卡纸上设计好构图；3. 用少量热熔胶点在花材背面固定；4. 先大花后小花、先主花后配叶；5. 完成后密封保存。建议选用带悬浮效果的相框，立体感更强。"},
            {"title": "干花色彩搭配美学", "category": "搭配", "difficulty": "精通",
             "content": "推荐配色方案：①豆沙粉+奶白+浅黄：温柔浪漫系；②莫兰迪蓝+灰紫+银绿：高级冷调；③焦糖+橘棕+米白：复古温暖；④全白+银色：纯净优雅。搭配原则：主色60%+辅助色30%+点缀色10%。"}
        ]

        created_notes = []
        for nd in notes_data:
            note = TechniqueNote(**nd,
                tips=["选择品质好的花材是成功的基础", "耐心等待，不要急于查看干燥进度", "做好记录，便于下次改进"],
                warnings=["干燥剂不可食用，远离儿童", "微波炉法需严格控制时间，避免焦糊", "压花时花材不可重叠"]
            )
            db.add(note)
            created_notes.append(note)

        plan_styles = ["复古", "清新", "森系", "极简", "浪漫", "田园"]
        plan_scenes = ["家居", "婚礼", "办公", "礼品", "展览"]

        plans_data = [
            {"name": "豆沙粉浪漫花束·客厅装饰", "style": "浪漫", "scene": "家居",
             "color_theme": "豆沙粉+奶白+浅黄+银绿",
             "materials_needed": [
                 {"name": "豆沙粉玫瑰", "qty": 15, "unit": "枝"},
                 {"name": "奶白满天星", "qty": 1, "unit": "扎"},
                 {"name": "圆叶尤加利", "qty": 8, "unit": "枝"},
                 {"name": "浅黄雏菊", "qty": 5, "unit": "枝"},
                 {"name": "丝带", "qty": 2, "unit": "米"}
             ],
             "tools_needed": ["花艺剪刀", "胶带", "包装纸", "热熔胶枪"],
             "estimated_hours": 3, "estimated_cost": 168, "priority": 1,
             "design_sketch_url": "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=600",
             "steps": [
                 {"step": 1, "desc": "准备所有花材，整理造型"},
                 {"step": 2, "desc": "以玫瑰为中心，螺旋手法依次加入配花配叶"},
                 {"step": 3, "desc": "调整花束层次和高度"},
                 {"step": 4, "desc": "绑扎固定，裁剪根部"},
                 {"step": 5, "desc": "包装装饰，系上丝带"}
             ],
             "layout_description": "以圆形构图，玫瑰居中，满天星填充空隙，尤加利和雏菊向外延伸，营造蓬松浪漫的视觉效果。整体高度约35cm，适合放在客厅茶几或玄关处。",
             "collocation_advice": "搭配原木色或奶白色花器最佳，避免过于花哨的容器抢了花束的风头。客厅建议选择暖光灯照射，色彩更温馨。",
             "status": "已完成"
            },
            {"name": "森系干花相框·餐厅背景墙", "style": "森系", "scene": "家居",
             "color_theme": "自然绿+焦糖+原木色+奶白",
             "materials_needed": [
                 {"name": "尤加利叶", "qty": 12, "unit": "枝"},
                 {"name": "迷你玫瑰", "qty": 8, "unit": "朵"},
                 {"name": "满天星", "qty": "适量", "unit": "少许"},
                 {"name": "干苔藓", "qty": 1, "unit": "袋"},
                 {"name": "松果", "qty": 3, "unit": "个"}
             ],
             "tools_needed": ["原木相框A3", "热熔胶", "镊子", "剪刀"],
             "estimated_hours": 4, "estimated_cost": 98, "priority": 2,
             "steps": [
                 {"step": 1, "desc": "设计草稿，确定构图位置"},
                 {"step": 2, "desc": "背景铺一层干苔藓打底"},
                 {"step": 3, "desc": "按设计图摆放主花材"},
                 {"step": 4, "desc": "添加配材和装饰元素"},
                 {"step": 5, "desc": "固定装裱，密封保存"}
             ],
             "layout_description": "不对称构图，左上集中花材，右下留白，视觉重心稳定又不失灵动。",
             "collocation_advice": "一组3个不同大小的相框组合悬挂效果更佳，搭配同风格装饰画。",
             "status": "进行中"
            },
            {"name": "极简风桌面摆件·办公桌", "style": "极简", "scene": "办公",
             "color_theme": "纯白+透明+浅灰",
             "materials_needed": [
                 {"name": "单支白玫瑰干花", "qty": 1, "unit": "枝"},
                 {"name": "透明玻璃花瓶", "qty": 1, "unit": "个"},
                 {"name": "白色细砂", "qty": 1, "unit": "袋"}
             ],
             "tools_needed": ["镊子"],
             "estimated_hours": 0.5, "estimated_cost": 45, "priority": 3,
             "layout_description": "一枝独秀，白砂垫底，纯粹极简。",
             "collocation_advice": "放置在显示器旁或文件柜上，不占空间。",
             "status": "草稿"
            }
        ]

        created_plans = []
        for pd in plans_data:
            plan = DesignPlan(**pd)
            db.add(plan)
            created_plans.append(plan)

        angles = ["正面", "侧面", "俯视", "特写"]
        lightings = ["自然光", "暖光", "冷光", "柔光"]
        backgrounds = ["纯色", "花艺", "木质", "布艺"]

        for i, spec in enumerate(specimens[:5]):
            img = ProductImage(
                specimen_id=spec.id,
                title=f"{spec.name} - 主图",
                image_url=spec.image_url,
                shot_angle=angles[i % len(angles)],
                lighting=lightings[i % len(lightings)],
                background=backgrounds[i % len(backgrounds)],
                description=f"成品实拍，展示{spec.category}细节之美。光线{lightings[i % len(lightings)]}更能凸显花材纹理。",
                file_size=random.randint(500000, 3000000),
                resolution=f"{random.choice([1920, 2560, 3840])}x{random.choice([1080, 1440, 2160])}",
                is_cover=True,
                sort_order=0,
                shot_date=spec.production_date,
                photographer="花语摄影师"
            )
            db.add(img)

            for j, gal in enumerate(spec.gallery_images or []):
                img2 = ProductImage(
                    specimen_id=spec.id,
                    title=f"{spec.name} - 细节图{j+1}",
                    image_url=gal,
                    shot_angle=angles[(i + j + 1) % len(angles)],
                    lighting=lightings[(i + j + 1) % len(lightings)],
                    background=backgrounds[(i + j + 1) % len(backgrounds)],
                    is_cover=False,
                    sort_order=j + 1,
                    shot_date=spec.production_date,
                    photographer="花语摄影师"
                )
                db.add(img2)

        for spec in specimens:
            if spec.is_shared and random.random() > 0.3:
                post = SharePost(
                    specimen_id=spec.id,
                    title=f"【{spec.category}新作】{spec.name}",
                    content=f"终于完成了这件{spec.category}作品！\n\n用了{spec.drying_process.method if spec.drying_process else '传统'}的制作方法，经历了漫长的等待，结果真的很惊喜～\n\n花瓣的颜色和形状都保留得很好，装裱好之后放在家里整个角落都温柔起来了。干花的魅力就在于此吧，把美好永远定格✨\n\n大家喜欢这种风格吗？",
                    author="花艺小姐姐",
                    is_published=True,
                    published_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    like_count=spec.like_count or random.randint(5, 200),
                    share_count=random.randint(0, 50),
                    comment_count=random.randint(0, 30),
                    view_count=spec.view_count or random.randint(50, 1000),
                    tags=["手作", "干花", "家居装饰", "慢生活", "治愈"]
                )
                db.add(post)

        cons_cats = ["花材", "干燥剂", "容器", "工具", "辅料"]
        cons_items = [
            ("硅胶干燥剂", "干燥剂", 500, "g", 0.05),
            ("密封保鲜盒", "容器", 2, "个", 15),
            ("白乳胶", "辅料", 1, "瓶", 8),
            ("花艺剪刀", "工具", 1, "把", 25),
            ("丝带", "辅料", 5, "米", 2),
            ("相框", "容器", 1, "个", 35),
            ("包装纸", "辅料", 3, "张", 5),
        ]

        for proc in processes[:4]:
            for ci in cons_items[:random.randint(2, 5)]:
                qty = random.uniform(1, ci[2]) if ci[2] > 10 else ci[2] * random.uniform(0.5, 1.5)
                consumption = MaterialConsumption(
                    drying_process_id=proc.id,
                    item_name=ci[0],
                    category=ci[1],
                    quantity=round(qty, 2),
                    unit=ci[3],
                    unit_price=ci[4],
                    total_cost=round(qty * ci[4], 2),
                    notes=f"用于{proc.process_name}"
                )
                db.add(consumption)

        await db.commit()
