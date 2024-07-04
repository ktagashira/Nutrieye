from pydantic import BaseModel


from typing import List


class FoodItem(BaseModel):
    name: str
    calorie: float
    protein: float
    fat: float
    carbohydrate: float


class TotalNutrients(BaseModel):
    calorie: float
    protein: float
    fat: float
    carbohydrate: float


class NutritionData(BaseModel):
    food: List[FoodItem]
    total: TotalNutrients
