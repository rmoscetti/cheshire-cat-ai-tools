from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StatePublic")


@_attrs_define
class StatePublic:
    """
    Attributes:
        time_seconds (int):
        fraction_initial (float):
        weight (float):
    """

    time_seconds: int
    fraction_initial: float
    weight: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time_seconds = self.time_seconds

        fraction_initial = self.fraction_initial

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_seconds": time_seconds,
                "fraction_initial": fraction_initial,
                "weight": weight,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        time_seconds = d.pop("time_seconds")

        fraction_initial = d.pop("fraction_initial")

        weight = d.pop("weight")

        state_public = cls(
            time_seconds=time_seconds,
            fraction_initial=fraction_initial,
            weight=weight,
        )

        state_public.additional_properties = d
        return state_public

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
