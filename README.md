# Tempit

Tempit is a Python package designed to simplify the process of measuring the execution time of your functions through a straightforward decorator.

## Installation

You can install Tempit using pip:

```bash
pip install tempit
```

## Usage

Below are some examples demonstrating Tempit's usage:

### Basic Usage

```python
from tempit import tempit

@tempit
def my_function():
    # Normal code of your function
    pass

my_function()
```

This will output something like:

```text
Function my_function took 10.5908ms.
```

### Advanced Usage

```python
from tempit import tempit
@tempit(run_times=20, concurrent_execution=True, verbose=True)
def my_function_with_args(a:int = 1, b:int = 2):
    return a + b

result = my_function_with_args(1, b=2)
```

This will provide detailed output:

```text
***** tempit data for function my_function_with_args: *****
Function name: my_function_with_args
        Funcion object: <function my_function_with_args at 0x0000000000000000>
        Args: (1,)
        Kwargs: {'b': 2}
        Run times: 20
        Mean: 0.7000µs
        Median: 0.8000µs
        Min: 0.4000µs
        Max: 1.0000µs
        Standard deviation: 0.2828µs
        Sum time: 3.5000µs
        Real time: 965.1000µs
***** End of tempit data. *****
```

More examples can be found in the [examples.py](examples/examples.py) script.

## Features

- Simplified usage.
- Accurate measurement of function execution time.
- Support for `classmethod` and `staticmethods`.
- Parallel execution mode for performance measurement.
- Human-readable time formatting.
- Optional verbose mode for detailed information.

## Parameters

Using the decorator @tempit without any parameters executes the function once and displays the execution time. However, you can enhance the experience using the following arguments:

- `run_times` (int, optional): Specifies the number of function executions. Defaults to 1.
- `concurrency_mode` (bool, optional): Determines the concurrency mode for the function execution. It uses [joblib](https://pypi.org/project/joblib/) for parallel computing. The  default execution backend is "loky" but if the function is being triggered other than the main thread or main process, the backend will be changed to multithreading to aovid pickle errors. If, for any other reason, fails, the program will try to execute the func run_times non concurrently in the main process. Defaults to True.
- `verbose` (bool, optional): Controls whether detailed information is printed after execution. Defaults to False.

## Contributing

Contributions are welcome! Please follow these guidelines when contributing:

1. Fork the repository.
2. Create a new branch for your changes.
3. Implement your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request.

## Testing

The package has been thoroughly tested using unittesting. Test cases can be found in the [tests folder](tests) and can be executed using `make test`.

## License

This project is licensed under the [MIT License](LICENSE.txt).

## Contributors

- [Mario Crespo](https://github.com/mcrespoae)
