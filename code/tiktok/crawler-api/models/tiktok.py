from pydantic import BaseModel

class AdGroup(BaseModel):
    deep_funnel_optimization_status: str | None
    auto_targeting_enabled: bool
    dayparting: str
    adgroup_name: str
    interest_category_ids: list[str]
    comment_disabled: bool
    secondary_optimization_event: str | None
    excluded_audience_ids: list[str]
    placement_type: str
    purchased_impression: str | None
    actions: list[str]
    adgroup_id: str
    next_day_retention: str | None
    category_id: str
    rf_estimated_cpr: str | None
    keywords: str | None
    network_types: list[str]
    operating_systems: list[str]
    adgroup_app_profile_page_state: str | None
    conversion_window: str | None
    attribution_event_count: str
    audience_ids: list[str]
    operation_status: str
    scheduled_budget: int
    bid_price: int
    deep_bid_type: str | None
    conversion_bid_price: int
    is_hfss: bool
    search_result_enabled: bool
    smart_audience_enabled: str | None
    schedule_end_time: str
    feed_type: str | None
    purchased_reach: str | None
    app_id: str | None
    creative_material_mode: str
    purchase_intention_keyword_ids: list[str]
    pacing: str
    vbo_window: str | None
    delivery_mode: str | None
    optimization_event: str
    advertiser_id: str
    skip_learning_phase: bool
    secondary_status: str
    schedule_type: str
    brand_safety_type: str
    app_type: str | None
    location_ids: list[str]
    device_price_ranges: list[str]
    schedule_start_time: str
    promotion_website_type: str
    frequency: str | None
    deep_funnel_optimization_event: str | None
    smart_interest_behavior_enabled: str | None
    zipcode_ids: list[str]
    excluded_custom_actions: list[str]
    interest_keyword_ids: list[str]
    is_smart_performance_campaign: bool
    brand_safety_partner: str | None
    deep_cpa_bid: int
    billing_event: str
    isp_ids: list[str]
    rf_estimated_frequency: str | None
    is_new_structure: bool
    contextual_tag_ids: list[str]
    create_time: str
    budget: int
    bid_type: str
    share_disabled: bool
    ios14_quota_type: str
    budget_mode: str
    click_attribution_window: str
    schedule_infos: str | None
    statistic_type: str | None
    spending_power: str
    bid_display_mode: str
    placements: list[str]
    targeting_expansion: dict
    modify_time: str
    campaign_id: str
    age_groups: str | None
    languages: list[str]
    pixel_id: str
    household_income: list[str]
    deep_funnel_event_source: str | None
    included_custom_actions: list[str]
    device_model_ids: list[str]
    deep_funnel_event_source_id: str | None
    campaign_name: str
    inventory_filter_enabled: bool
    frequency_schedule: str | None
    category_exclusion_ids: list[str]
    video_download_disabled: bool
    rf_purchased_type: str | None
    view_attribution_window: str
    optimization_goal: str
    promotion_type: str
    app_download_url: str | None
    gender: str

class Ad(BaseModel):
    is_aco: bool
    adgroup_name: str
    secondary_status: str
    page_id: str | None
    avatar_icon_web_uri: str
    image_ids: list[str]
    advertiser_id: str
    optimization_event: str
    brand_safety_vast_url: str | None
    landing_page_urls: str | None
    tracking_pixel_id: int
    profile_image_url: str
    landing_page_url: str
    identity_type: str
    viewability_vast_url: str | None
    display_name: str
    ad_id: str
    campaign_name: str
    vast_moat_enabled: bool
    app_name: str
    ad_texts: str | None
    click_tracking_url: str | None
    call_to_action_id: str | None
    campaign_id: str
    create_time: str
    call_to_action: str
    music_id: str | None
    deeplink_type: str
    carousel_image_labels: str | None
    ad_name: str
    video_id: str
    identity_id: str
    ad_format: str
    is_new_structure: bool
    deeplink: str
    creative_authorized: bool
    adgroup_id: str
    ad_ref_pixel_id: int
    ad_text: str
    playable_url: str | None
    modify_time: str
    viewability_postbid_partner: str
    operation_status: str
    brand_safety_postbid_partner: str
    impression_tracking_url: str | None
    fallback_type: str
    card_id: str | None
    creative_type: str | None

class Advertiser(BaseModel):
  advertiser_id: str
  advertiser_name: str

class AdvertiserInfo(BaseModel):
  rejection_reason: str | None
  license_no: str
  timezone: str
  brand: str | None
  promotion_center_city: str | None
  contacter: str
  status: str
  industry: str
  currency: str
  country: str
  create_time: int
  telephone_number: str
  company: str
  address: str | None
  license_city: str | None
  language: str
  license_url: str | None
  advertiser_account_type: str
  license_province: str | None
  balance: int
  cellphone_number: str
  promotion_center_province: str | None
  role: str
  advertiser_id: str
  description: str
  name: str
  email: str
  promotion_area: str
  display_timezone: str

class Campaign(BaseModel):
    budget_mode: str
    rta_bid_enabled: bool
    objective: str
    campaign_name: str
    is_smart_performance_campaign: bool
    roas_bid: int
    modify_time: str
    disable_skan_campaign: str | None
    advertiser_id: str
    campaign_type: str
    objective_type: str
    is_search_campaign: bool
    app_promotion_type: str
    is_advanced_dedicated_campaign: bool
    budget: int
    rf_campaign_type: str
    secondary_status: str
    is_new_structure: bool
    rta_id: str | None
    operation_status: str
    create_time: str
    campaign_id: str
    deep_bid_type: str | None
    special_industries: list[str]
    rta_product_selection_enabled: bool

class PageInfo(BaseModel):
    page: int
    page_size: int
    total_page: int
    total_number: int

class Dimensions(BaseModel):
    stat_time_day: str
    ad_id: str

class Metrics(BaseModel):
    cost_per_result: str
    conversion_rate: str
    reach: str
    cpc: str
    clicks: str
    spend: str
    billed_cost: str
    secondary_goal_result_rate: str
    conversion_rate_v2: str
    cost_per_1000_reached: str
    impressions: str
    cash_spend: str
    real_time_result_rate: str
    cost_per_secondary_goal_result: str
    real_time_cost_per_result: str
    voucher_spend: str
    cost_per_conversion: str
    gross_impressions: str
    result: str
    real_time_result: str
    cpm: str
    real_time_conversion_rate_v2: str
    ctr: str
    secondary_goal_result: str
    frequency: str
    real_time_conversion_rate: str
    real_time_conversion: str
    conversion: str
    result_rate: str
    real_time_cost_per_conversion: str

class ReportIntegrated(BaseModel):
    metrics: Metrics
    dimensions: Dimensions

class DataPayload(BaseModel):
  list: list[Advertiser | AdvertiserInfo | ReportIntegrated | Campaign | Ad | AdGroup]
  page_info: PageInfo = None

class TiktokBusinessResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: DataPayload | None
