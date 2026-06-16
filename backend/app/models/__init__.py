from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, Date, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FlowerMaterial(Base):
    __tablename__ = "flower_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="花材名称")
    scientific_name = Column(String(200), comment="学名")
    category = Column(String(50), comment="分类：玫瑰/满天星/尤加利/绣球/薰衣草/其他")
    color = Column(String(50), comment="花色")
    origin = Column(String(100), comment="产地")
    quantity = Column(Float, default=0, comment="数量(枝/克)")
    unit = Column(String(20), default="枝", comment="单位")
    purchase_date = Column(Date, comment="采购日期")
    supplier = Column(String(100), comment="供应商")
    fresh_level = Column(String(20), comment="新鲜度：A/B/C")
    storage_method = Column(String(200), comment="储存方式")
    image_url = Column(String(500), comment="原料图片")
    notes = Column(Text, comment="备注")
    is_available = Column(Boolean, default=True, comment="是否可用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    consumptions = relationship("MaterialConsumption", back_populates="material")
    drying_processes = relationship("DryingProcess", back_populates="material")


class DryingProcess(Base):
    __tablename__ = "drying_processes"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("flower_materials.id"))
    process_name = Column(String(100), nullable=False, comment="制作名称")
    method = Column(String(50), comment="制作方法：自然风干/倒挂/干燥剂/微波炉/压花")
    start_date = Column(DateTime, comment="开始时间")
    end_date = Column(DateTime, comment="结束时间")
    duration_hours = Column(Float, comment="制作时长(小时)")
    temperature = Column(Float, comment="温度(℃)")
    humidity = Column(Float, comment="湿度(%)")
    pressure = Column(String(50), comment="压力/干燥剂重量")
    desiccant_weight = Column(Float, comment="干燥剂重量(克)")
    pre_treatment = Column(Text, comment="预处理步骤")
    process_steps = Column(JSON, comment="制作步骤JSON")
    status = Column(String(20), default="进行中", comment="状态：进行中/已完成/失败")
    color_retention = Column(String(20), comment="保色效果：优/良/中/差")
    shape_retention = Column(String(20), comment="保型效果：优/良/中/差")
    yield_rate = Column(Float, comment="成品率(%)")
    output_quantity = Column(Float, comment="产出数量")
    output_unit = Column(String(20), default="枝", comment="产出单位")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    material = relationship("FlowerMaterial", back_populates="drying_processes")
    specimens = relationship("Specimen", back_populates="drying_process")
    consumptions = relationship("MaterialConsumption", back_populates="drying_process")


class Specimen(Base):
    __tablename__ = "specimens"

    id = Column(Integer, primary_key=True, index=True)
    drying_process_id = Column(Integer, ForeignKey("drying_processes.id"))
    name = Column(String(100), nullable=False, comment="标本名称")
    category = Column(String(50), comment="分类：单枝/花束/压花/香薰/摆件/礼盒")
    display_code = Column(String(50), unique=True, comment="陈列编号")
    production_date = Column(Date, comment="制作日期")
    shelf_life_months = Column(Integer, comment="保存期限(月)")
    preservation_method = Column(String(200), comment="保存方式")
    frame_size = Column(String(50), comment="装裱尺寸")
    frame_style = Column(String(50), comment="装裱风格")
    description = Column(Text, comment="作品描述")
    tags = Column(JSON, comment="标签JSON")
    image_url = Column(String(500), comment="主图URL")
    gallery_images = Column(JSON, comment="图集JSON")
    is_featured = Column(Boolean, default=False, comment="是否精选")
    is_shared = Column(Boolean, default=False, comment="是否分享")
    like_count = Column(Integer, default=0, comment="点赞数")
    view_count = Column(Integer, default=0, comment="浏览数")
    location = Column(String(100), comment="存放位置")
    status = Column(String(20), default="完好", comment="状态：完好/微损/已赠出/售出")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    drying_process = relationship("DryingProcess", back_populates="specimens")
    images = relationship("ProductImage", back_populates="specimen")
    share_post = relationship("SharePost", uselist=False, back_populates="specimen")
    favorites = relationship("Favorite", back_populates="specimen")


class TechniqueNote(Base):
    __tablename__ = "technique_notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="笔记标题")
    category = Column(String(50), comment="分类：采花/预处理/风干/保色/装裱/搭配/其他")
    difficulty = Column(String(20), comment="难度：入门/进阶/精通")
    content = Column(Text, nullable=False, comment="笔记内容")
    tips = Column(JSON, comment="技巧提示JSON")
    warnings = Column(JSON, comment="注意事项JSON")
    reference_links = Column(JSON, comment="参考链接JSON")
    image_url = Column(String(500), comment="配图")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    favorites = relationship("Favorite", back_populates="note")


class DesignPlan(Base):
    __tablename__ = "design_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="方案名称")
    style = Column(String(50), comment="风格：复古/清新/森系/极简/浪漫/田园")
    scene = Column(String(50), comment="适用场景：家居/婚礼/办公/礼品/展览")
    color_theme = Column(String(100), comment="色彩主题")
    materials_needed = Column(JSON, comment="所需材料JSON")
    tools_needed = Column(JSON, comment="所需工具JSON")
    estimated_hours = Column(Float, comment="预估工时(小时)")
    estimated_cost = Column(Float, comment="预估成本(元)")
    design_sketch_url = Column(String(500), comment="设计草图")
    steps = Column(JSON, comment="制作步骤JSON")
    layout_description = Column(Text, comment="布局说明")
    collocation_advice = Column(Text, comment="搭配建议")
    status = Column(String(20), default="草稿", comment="状态：草稿/进行中/已完成")
    priority = Column(Integer, default=0, comment="优先级")
    reference_images = Column(JSON, comment="参考图JSON")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    favorites = relationship("Favorite", back_populates="plan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    specimen_id = Column(Integer, ForeignKey("specimens.id"), nullable=True)
    design_plan_id = Column(Integer, ForeignKey("design_plans.id"), nullable=True)
    title = Column(String(200), comment="图片标题")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    thumbnail_url = Column(String(500), comment="缩略图")
    shot_angle = Column(String(50), comment="拍摄角度：正面/侧面/俯视/特写")
    lighting = Column(String(50), comment="光线：自然光/暖光/冷光/柔光")
    background = Column(String(50), comment="背景：纯色/花艺/木质/布艺")
    description = Column(Text, comment="图片描述")
    file_size = Column(Integer, comment="文件大小(字节)")
    resolution = Column(String(50), comment="分辨率")
    is_cover = Column(Boolean, default=False, comment="是否封面")
    sort_order = Column(Integer, default=0, comment="排序")
    shot_date = Column(Date, comment="拍摄日期")
    photographer = Column(String(50), comment="拍摄者")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    specimen = relationship("Specimen", back_populates="images")
    favorites = relationship("Favorite", back_populates="image")


class SharePost(Base):
    __tablename__ = "share_posts"

    id = Column(Integer, primary_key=True, index=True)
    specimen_id = Column(Integer, ForeignKey("specimens.id"), unique=True)
    title = Column(String(200), nullable=False, comment="分享标题")
    content = Column(Text, comment="分享内容")
    author = Column(String(50), default="花艺爱好者", comment="作者")
    is_published = Column(Boolean, default=True, comment="是否发布")
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    like_count = Column(Integer, default=0, comment="点赞数")
    share_count = Column(Integer, default=0, comment="转发数")
    comment_count = Column(Integer, default=0, comment="评论数")
    view_count = Column(Integer, default=0, comment="浏览数")
    tags = Column(JSON, comment="标签JSON")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    specimen = relationship("Specimen", back_populates="share_post")
    likes = relationship("Like", back_populates="post")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("share_posts.id"))
    user_identifier = Column(String(100), default="anonymous", comment="用户标识")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("post_id", "user_identifier", name="uq_post_user"),
    )

    post = relationship("SharePost", back_populates="likes")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    favorite_type = Column(String(20), comment="类型：specimen/note/plan/image")
    specimen_id = Column(Integer, ForeignKey("specimens.id"), nullable=True)
    note_id = Column(Integer, ForeignKey("technique_notes.id"), nullable=True)
    plan_id = Column(Integer, ForeignKey("design_plans.id"), nullable=True)
    image_id = Column(Integer, ForeignKey("product_images.id"), nullable=True)
    folder = Column(String(50), default="默认收藏夹", comment="收藏夹名称")
    remark = Column(String(200), comment="收藏备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    specimen = relationship("Specimen", back_populates="favorites")
    note = relationship("TechniqueNote", back_populates="favorites")
    plan = relationship("DesignPlan", back_populates="favorites")
    image = relationship("ProductImage", back_populates="favorites")


class MaterialConsumption(Base):
    __tablename__ = "material_consumptions"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("flower_materials.id"))
    drying_process_id = Column(Integer, ForeignKey("drying_processes.id"))
    item_name = Column(String(100), nullable=False, comment="耗材名称")
    category = Column(String(50), comment="分类：花材/干燥剂/容器/工具/辅料/其他")
    quantity = Column(Float, comment="消耗数量")
    unit = Column(String(20), comment="单位")
    unit_price = Column(Float, default=0, comment="单价(元)")
    total_cost = Column(Float, default=0, comment="总成本(元)")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    material = relationship("FlowerMaterial", back_populates="consumptions")
    drying_process = relationship("DryingProcess", back_populates="consumptions")
