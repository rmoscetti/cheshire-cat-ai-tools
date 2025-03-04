import datetime
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigCreate")


@_attrs_define
class ConfigCreate:
    """
    Attributes:
        start_time (Union[None, Unset, datetime.datetime]):  Default: isoparse('2025-03-04T10:50:23.844161').
        time_speed (Union[None, Unset, float]):  Default: 10.0.
    """

    start_time: Union[None, Unset, datetime.datetime] = isoparse("2025-03-04T10:50:23.844161")
    time_speed: Union[None, Unset, float] = 10.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_time: Union[None, Unset, str]
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        elif isinstance(self.start_time, datetime.datetime):
            start_time = self.start_time.isoformat()
        else:
            start_time = self.start_time

        time_speed: Union[None, Unset, float]
        if isinstance(self.time_speed, Unset):
            time_speed = UNSET
        else:
            time_speed = self.time_speed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if time_speed is not UNSET:
            field_dict["time_speed"] = time_speed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_start_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_time_type_0 = isoparse(data)

                return start_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        start_time = _parse_start_time(d.pop("start_time", UNSET))

        def _parse_time_speed(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        time_speed = _parse_time_speed(d.pop("time_speed", UNSET))

        config_create = cls(
            start_time=start_time,
            time_speed=time_speed,
        )

        config_create.additional_properties = d
        return config_create

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
