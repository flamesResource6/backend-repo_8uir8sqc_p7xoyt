"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

class ShoeProduct(BaseModel):
    """
    Sneakers product schema focused on shoes
    Collection name: "shoeproduct"
    """
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-friendly unique identifier")
    brand: str = Field(..., description="Brand name")
    description: str = Field(..., description="Detailed description")
    price: float = Field(..., ge=0, description="Price in USD")
    rating: float = Field(4.5, ge=0, le=5, description="Average rating")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    colors: List[Dict[str, str]] = Field(default_factory=list, description="List of colors with name and hex")
    sizes: List[float] = Field(default_factory=list, description="Available sizes US scale")
    stock: Dict[str, int] = Field(default_factory=dict, description="Stock per size (key is size as string)")
    tags: List[str] = Field(default_factory=list, description="Search tags")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
