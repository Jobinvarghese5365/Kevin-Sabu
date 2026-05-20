from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    brand_name: str = Field(min_length=1)
    region: str = Field(min_length=1)


class SocialLinks(BaseModel):
    facebook: str = ""
    instagram: str = ""
    youtube: str = ""


class ResearchResult(BaseModel):
    official_brand_name: str = ""
    parent_organisation: str = ""
    terms_conditions: str = ""
    privacy_policy: str = ""
    description: str = ""
    social_media: SocialLinks = SocialLinks()
    logo_url: str = ""

