from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, List
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class StringWithNode(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    finalString: Optional[str] = Field(default=None)
    node_id: Optional[PyObjectId] = Field(default=None)
    name: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str})

class StringWithNodeCollection(BaseModel):
    nodes: List[StringWithNode]