from pydantic import BaseModel
from typing import Any


def to_camel(string: str) -> str:
	parts = string.split("_")
	return parts[0] + ''.join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
	"""Base Pydantic model that uses camelCase aliases for JSON output/input."""

	class Config:
		alias_generator = to_camel
		allow_population_by_field_name = True
		orm_mode = True
		json_encoders = {Any: lambda v: v}
