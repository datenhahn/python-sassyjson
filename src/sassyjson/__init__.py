"""
   Copyright 2022 Ecodia GmbH & Co. KG

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import inspect

"""The module sassyjson contains functions to marshall python classes into json strings and to unmarshall json strings
   into python classes"""
import datetime
import json
from typing import TypeVar

SIMPLE_TYPES = ("str", "float", "int", "complex", "bool", "list", "dict", "NoneType")
"""SIMPLE_TYPES is a list of python simple types which can be deserialized automatically by python."""

SPECIAL_TYPES = ("datetime")
"""SPECIAL_TYPES is a list of python types which are handled individually with special code, but which are not simple types."""


def _prepare_serialization(object):
    """Returns a json representation for non simple python types (e.g. class instances).

    For objects: We use a trick and simply return the internal dictionary of the classes which is accessible via
                 instance.__dict__ . It contains all instance properties with their values.
    For datetime.datetime fields: we serialize the field as isodate.
    """
    if isinstance(object, datetime.datetime):
        return object.isoformat(timespec="microseconds")
    else:
        return object.__dict__


class SassyJsonNoDefaultConstructorError(Exception):
    """The SassyJsonNoDefaultConstructorError is thrown when a type without default constructor is given to the
        unmarshalling function.
    """
    pass


class SassyJsonMissingAttributeError(Exception):
    """The SassyJsonMissingAttributeError is thrown when a class attribute of the given type is not found in the
       json string.
    """
    pass


T = TypeVar("T")
"""T is a generic type capture for the return type"""


def has_default_constructor(my_type: T) -> bool:
    inspection_result = inspect.signature(my_type.__init__)
    return list(inspection_result.parameters.keys()) == ["self", "args", "kwargs"]


def result_from_default_constructor(input_dict: dict, my_type: T) -> T:
    result = my_type()

    for attribute, the_type in my_type.__annotations__.items():
        if the_type.__name__ in SIMPLE_TYPES:
            setattr(result, attribute, input_dict[attribute])
        elif the_type.__name__ == "datetime":
            setattr(result, attribute, datetime.datetime.fromisoformat(input_dict[attribute]))
        else:
            setattr(result, attribute, _object_from_dict(input_dict[attribute], the_type))
    return result


def result_from_parameterized_constructor(input_dict: dict, my_type: T) -> T:
    constructor_spec = inspect.signature(my_type.__init__)
    constructor_args = {}

    for parameter_spec in constructor_spec.parameters.values():
        if parameter_spec.name == "self":
            continue

        if parameter_spec.annotation.__name__ not in SIMPLE_TYPES and parameter_spec.annotation.__name__ not in SPECIAL_TYPES:
            constructor_args[parameter_spec.name] = _object_from_dict(input_dict[parameter_spec.name],
                                                                      parameter_spec.annotation)
        else:
            if parameter_spec.name in input_dict:
                constructor_args[parameter_spec.name] = input_dict[parameter_spec.name]
            else:
                if parameter_spec.default == parameter_spec.empty:
                    raise SassyJsonMissingAttributeError(f"All constructor parameters without default value must be set in the json, missing value for parameter {parameter_spec.name} when constructing class {my_type.__name__}")

    return my_type(**constructor_args)


def _object_from_dict(input_dict: dict, my_type: T) -> T:
    """
    Takes an input dictionary and a type, then goes through every attribute of the type and tries to set it from the
    dictionary.
    """
    try:

        if has_default_constructor(my_type):
            return result_from_default_constructor(input_dict, my_type)
        else:
            return result_from_parameterized_constructor(input_dict, my_type)
    except KeyError as k:
        raise SassyJsonMissingAttributeError(
            f"Attribute {k} of the target class type '{my_type.__name__}' is missing in the json.")


def to_json(object) -> str:
    """ Marshalls a python object into a json string.
    """
    return json.dumps(object, default=_prepare_serialization, sort_keys=True)


def from_json(json_string: str, object_type: T) -> T:
    """ Unmarshalls a json string into a python object of a given type
    """
    input_dict = json.loads(json_string)
    return _object_from_dict(input_dict, object_type)
