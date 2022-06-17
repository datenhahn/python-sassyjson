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
from dataclasses import dataclass
from datetime import datetime

import pytest

import sassyjson


@dataclass
class MyNestedClass:
    message: str = ""

@dataclass
class MyCustomClass:
    timestamp: datetime = None
    nested_message: MyNestedClass = None


def test_Should_convert_to_expected_json_When_example_class_is_given():
    # GIVEN: The example class from README file.
    my_instance = MyCustomClass(timestamp=datetime(2022,6,17), nested_message=MyNestedClass("Hello World!"))

    # WHEN: The class instance is converted to json string.
    output = sassyjson.to_json(my_instance)

    # THEN: It should match the expected string.
    expected = '{"nested_message": {"message": "Hello World!"}, "timestamp": "2022-06-17T00:00:00.000000"}'
    assert output == expected
