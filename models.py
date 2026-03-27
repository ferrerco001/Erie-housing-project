from pydantic import BaseModel, Field
from typing import Optional

class PropertyModel(BaseModel):

    #Id
    zillow_id : str

    #Address info
    address : str
    zip_code : str = Field(min_length=5, max_length=10)

    #Optional info
    sqft : Optional[int] = 0
    bedrooms : Optional[float] = 0.0
    bathrooms : Optional[float] = 0.0
    property_type : Optional[str]

    #Financial info
    price : int = Field(gt=0)
    listing_type : str

    class Config:
        from_attributes = True
