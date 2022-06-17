# sassyjson 

sassyjson is an automatic json objectmapper for python.

## Install

```
pip install 
```

## Usage

```python
@dataclass
class MyNestedClass:
    message: str = ""

@dataclass
class MyCustomClass:
    timestamp: datetime = None
    nested_message: MyNestedClass = None

 
my_instance = MyCustomClass(timestamp=datetime(2022,6,17),
                            nested_message=MyNestedClass("Hello World!"))

# Will generate the following string from the instance:
# '{"nested_message": {"message": "Hello World!"}, "timestamp": "2022-06-17T00:00:00.000000"}'
json_string = sassyjson.to_json(my_instance)

# Will generate a new MyCustomClass instance from the json string
new_instance = sassyjson.from_json(json_string, MyCustomClass)
```