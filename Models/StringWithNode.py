from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, List
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

# Type alias for ObjectId with a before validator to ensure it is a string
PyObjectId = Annotated[str, BeforeValidator(str)]

class StringWithNode(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)  # Unique identifier for the node
    finalString: Optional[str] = Field(default=None)  # Optional final string associated with the node
    node_id: Optional[PyObjectId] = Field(default=None)  # Optional reference to another node ID
    name: Optional[str] = Field(default=None)  # Optional name for the node

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow arbitrary types for fields
        json_encoders={ObjectId: str}  # Encoder to convert ObjectId to string for JSON serialization
    )

class StringWithNodeCollection(BaseModel):
    nodes: List[StringWithNode]  # Collection of StringWithNode instances
