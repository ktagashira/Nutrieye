from pydantic import BaseModel
from typing import List, Optional, Union


class Text(BaseModel):
    type: str
    text: str
    weight: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    margin: Optional[str] = None
    position: Optional[str] = None
    align: Optional[str] = None
    wrap: Optional[bool] = None
    flex: Optional[int] = None


class Separator(BaseModel):
    type: str
    margin: Optional[str] = None


class Box(BaseModel):
    type: str
    layout: str
    contents: List[Union[Text, Separator, "Box"]]
    margin: Optional[str] = None
    spacing: Optional[str] = None


class Body(BaseModel):
    type: str
    layout: str
    contents: List[Union[Text, Separator, Box]]


class FooterStyles(BaseModel):
    separator: bool


class Styles(BaseModel):
    footer: FooterStyles


class Bubble(BaseModel):
    type: str
    body: Body
    styles: Styles


# To make recursive models work
Box.model_rebuild()
