from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime, date


class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


class FlowerMaterialBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    origin: Optional[str] = None
    quantity: Optional[float] = 0
    unit: Optional[str] = "枝"
    purchase_date: Optional[date] = None
    supplier: Optional[str] = None
    fresh_level: Optional[str] = None
    storage_method: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    is_available: Optional[bool] = True


class FlowerMaterialCreate(FlowerMaterialBase):
    pass


class FlowerMaterialUpdate(BaseModel):
    name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    origin: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    purchase_date: Optional[date] = None
    supplier: Optional[str] = None
    fresh_level: Optional[str] = None
    storage_method: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    is_available: Optional[bool] = None


class FlowerMaterialResponse(FlowerMaterialBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FlowerMaterialFilter(BaseModel):
    category: Optional[str] = None
    color: Optional[str] = None
    is_available: Optional[bool] = None
    fresh_level: Optional[str] = None
    keyword: Optional[str] = None


class DryingProcessBase(BaseModel):
    material_id: Optional[int] = None
    process_name: str
    method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_hours: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[str] = None
    pre_treatment: Optional[str] = None
    process_steps: Optional[List[Dict]] = None
    status: Optional[str] = "进行中"
    color_retention: Optional[str] = None
    shape_retention: Optional[str] = None
    yield_rate: Optional[float] = None
    output_quantity: Optional[float] = None
    output_unit: Optional[str] = "枝"
    notes: Optional[str] = None


class DryingProcessCreate(DryingProcessBase):
    pass


class DryingProcessUpdate(BaseModel):
    material_id: Optional[int] = None
    process_name: Optional[str] = None
    method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_hours: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[str] = None
    pre_treatment: Optional[str] = None
    process_steps: Optional[List[Dict]] = None
    status: Optional[str] = None
    color_retention: Optional[str] = None
    shape_retention: Optional[str] = None
    yield_rate: Optional[float] = None
    output_quantity: Optional[float] = None
    output_unit: Optional[str] = None
    notes: Optional[str] = None


class DryingProcessResponse(DryingProcessBase):
    id: int
    material: Optional[FlowerMaterialResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DryingProcessFilter(BaseModel):
    method: Optional[str] = None
    status: Optional[str] = None
    material_id: Optional[int] = None
    color_retention: Optional[str] = None
    keyword: Optional[str] = None


class SpecimenBase(BaseModel):
    drying_process_id: Optional[int] = None
    name: str
    category: Optional[str] = None
    display_code: Optional[str] = None
    production_date: Optional[date] = None
    shelf_life_months: Optional[int] = None
    preservation_method: Optional[str] = None
    frame_size: Optional[str] = None
    frame_style: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    is_featured: Optional[bool] = False
    is_shared: Optional[bool] = False
    location: Optional[str] = None
    status: Optional[str] = "完好"


class SpecimenCreate(SpecimenBase):
    pass


class SpecimenUpdate(BaseModel):
    drying_process_id: Optional[int] = None
    name: Optional[str] = None
    category: Optional[str] = None
    display_code: Optional[str] = None
    production_date: Optional[date] = None
    shelf_life_months: Optional[int] = None
    preservation_method: Optional[str] = None
    frame_size: Optional[str] = None
    frame_style: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_shared: Optional[bool] = None
    location: Optional[str] = None
    status: Optional[str] = None
    like_count: Optional[int] = None
    view_count: Optional[int] = None


class SpecimenResponse(SpecimenBase):
    id: int
    like_count: int = 0
    view_count: int = 0
    drying_process: Optional[DryingProcessResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SpecimenFilter(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_shared: Optional[bool] = None
    frame_style: Optional[str] = None
    keyword: Optional[str] = None
    tag: Optional[str] = None


class TechniqueNoteBase(BaseModel):
    title: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    content: str
    tips: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    reference_links: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_favorite: Optional[bool] = False


class TechniqueNoteCreate(TechniqueNoteBase):
    pass


class TechniqueNoteUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    content: Optional[str] = None
    tips: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    reference_links: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_favorite: Optional[bool] = None


class TechniqueNoteResponse(TechniqueNoteBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TechniqueNoteFilter(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_favorite: Optional[bool] = None
    keyword: Optional[str] = None


class DesignPlanBase(BaseModel):
    name: str
    style: Optional[str] = None
    scene: Optional[str] = None
    color_theme: Optional[str] = None
    materials_needed: Optional[List[Dict]] = None
    tools_needed: Optional[List[str]] = None
    estimated_hours: Optional[float] = None
    estimated_cost: Optional[float] = None
    design_sketch_url: Optional[str] = None
    steps: Optional[List[Dict]] = None
    layout_description: Optional[str] = None
    collocation_advice: Optional[str] = None
    status: Optional[str] = "草稿"
    priority: Optional[int] = 0
    reference_images: Optional[List[str]] = None
    notes: Optional[str] = None


class DesignPlanCreate(DesignPlanBase):
    pass


class DesignPlanUpdate(BaseModel):
    name: Optional[str] = None
    style: Optional[str] = None
    scene: Optional[str] = None
    color_theme: Optional[str] = None
    materials_needed: Optional[List[Dict]] = None
    tools_needed: Optional[List[str]] = None
    estimated_hours: Optional[float] = None
    estimated_cost: Optional[float] = None
    design_sketch_url: Optional[str] = None
    steps: Optional[List[Dict]] = None
    layout_description: Optional[str] = None
    collocation_advice: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    reference_images: Optional[List[str]] = None
    notes: Optional[str] = None


class DesignPlanResponse(DesignPlanBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DesignPlanFilter(BaseModel):
    style: Optional[str] = None
    scene: Optional[str] = None
    status: Optional[str] = None
    keyword: Optional[str] = None


class ProductImageBase(BaseModel):
    specimen_id: Optional[int] = None
    design_plan_id: Optional[int] = None
    title: Optional[str] = None
    image_url: str
    thumbnail_url: Optional[str] = None
    shot_angle: Optional[str] = None
    lighting: Optional[str] = None
    background: Optional[str] = None
    description: Optional[str] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    is_cover: Optional[bool] = False
    sort_order: Optional[int] = 0
    shot_date: Optional[date] = None
    photographer: Optional[str] = None


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    specimen_id: Optional[int] = None
    design_plan_id: Optional[int] = None
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    shot_angle: Optional[str] = None
    lighting: Optional[str] = None
    background: Optional[str] = None
    description: Optional[str] = None
    is_cover: Optional[bool] = None
    sort_order: Optional[int] = None
    shot_date: Optional[date] = None
    photographer: Optional[str] = None


class ProductImageResponse(ProductImageBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductImageFilter(BaseModel):
    specimen_id: Optional[int] = None
    design_plan_id: Optional[int] = None
    shot_angle: Optional[str] = None
    is_cover: Optional[bool] = None
    keyword: Optional[str] = None


class SharePostBase(BaseModel):
    specimen_id: Optional[int] = None
    title: str
    content: Optional[str] = None
    author: Optional[str] = "花艺爱好者"
    is_published: Optional[bool] = True
    tags: Optional[List[str]] = None


class SharePostCreate(SharePostBase):
    pass


class SharePostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None


class SharePostResponse(SharePostBase):
    id: int
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    published_at: Optional[datetime] = None
    specimen: Optional[SpecimenResponse] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SharePostFilter(BaseModel):
    is_published: Optional[bool] = None
    keyword: Optional[str] = None
    tag: Optional[str] = None


class LikeCreate(BaseModel):
    post_id: int
    user_identifier: Optional[str] = "anonymous"


class FavoriteBase(BaseModel):
    favorite_type: str
    specimen_id: Optional[int] = None
    note_id: Optional[int] = None
    plan_id: Optional[int] = None
    image_id: Optional[int] = None
    folder: Optional[str] = "默认收藏夹"
    remark: Optional[str] = None


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialConsumptionBase(BaseModel):
    material_id: Optional[int] = None
    drying_process_id: Optional[int] = None
    item_name: str
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = 0
    total_cost: Optional[float] = 0
    notes: Optional[str] = None


class MaterialConsumptionCreate(MaterialConsumptionBase):
    pass


class MaterialConsumptionUpdate(BaseModel):
    material_id: Optional[int] = None
    drying_process_id: Optional[int] = None
    item_name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_cost: Optional[float] = None
    notes: Optional[str] = None


class MaterialConsumptionResponse(MaterialConsumptionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StatisticsResponse(BaseModel):
    total_materials: int = 0
    total_processes: int = 0
    total_specimens: int = 0
    total_notes: int = 0
    total_plans: int = 0
    total_images: int = 0
    total_posts: int = 0
    total_likes: int = 0
    total_duration_hours: float = 0
    total_cost: float = 0
    materials_by_category: List[Dict] = []
    specimens_by_category: List[Dict] = []
    methods_usage: List[Dict] = []
    monthly_processes: List[Dict] = []
    top_favorites: List[Dict] = []
