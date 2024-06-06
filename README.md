
# tempit

![PyPI](https://img.shields.io/pypi/v/tempit?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tempit)

## Overview

`tempit` is a Python package designed to simplify the process of measuring the execution time of your functions through a straightforward decorator.

## Installation

You can install `tempit` using pip:

```bash
pip install tempit
```

## Usage

Utilizing the `tempit` decorator is simple and intuitive. Follow this section to learn how to make the most of its capabilities.

### Basic Usage

Below are some examples demonstrating `tempit`'s usage:

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

It is possible to use [Parameters](#parameters) to customize the behavior of the `tempit` decorator, allowing you to tailor its functionality to better suit your specific benchmarking needs. Here is an example of how to use them:

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
        Function object: <function my_function_with_args at 0x0000000000000000>
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

More examples can be found in the [examples.py](https://github.com/mcrespoae/tempit/blob/main/examples/examples.py) script.

### Recommended Usage

To accurately measure the performance of your functions using the `tempit` tool, follow these guidelines:

- **Run Functions Multiple Times**: Set the `run_times` parameter to a value greater than 1 to obtain precise measurements. This is especially important for quick functions, as a single execution can be inaccurate due to measurement overhead. For very small functions, using 5 runs is a good rule of thumb. By default, `run_times` is set to 1, which is generally sufficient for time-consuming functions because their longer execution times are less prone to inaccuracies.
- **Sequential Execution**: Set `concurrent_execution` to `False` for the most accurate measurements. This ensures each run is measured independently, avoiding the averaging effect of concurrent execution.

### Timeit in Production Environments

The `tempit` decorator is designed **exclusively for benchmarking and is not suitable for use in production code**. You can globally deactivate the `tempit` feature by setting the `TempitConfig.ACTIVE` flag to false at the top of your imports. While this will skip the decoration of callables, there may still be a minimal CPU overhead. For production-grade applications, it's recommended to manually remove the decorators and `tempit` imports to maintain optimal performance.

```python
from tempit import TempitConfig, tempit
TempitConfig.ACTIVE = False  # Deactivates the decorator
```

## Features

- Simplified usage.
- Accurate measurement of function execution time.
- Support for functions, methods, `classmethod` and `staticmethods`.
- Human-readable time formatting.
- Optional verbose mode for detailed information.
- Ability to globally deactivate the `tempit` decorator.
- Parallel execution mode for performance measurement.
- Automatic recursion detection.

## Parameters

Using the decorator `@tempit` without any parameters executes the function once and displays the execution time. However, you can enhance the experience using the following arguments:

- `run_times` (int, optional): Specifies the number of function executions. Defaults to 1.
- `concurrency_mode` (bool, optional): Determines the concurrency mode for the function execution. It uses [joblib](https://pypi.org/project/joblib/) for parallel computing. Defaults to True. **Will be changed to False as default in v.0.2.0**
- `verbose` (bool, optional): Controls whether detailed information is printed after execution. Defaults to False.

## Best Practices

The ideal way to use this package is by applying the decorator to the functions you want to measure and running them side by side to compare the results more easily.

- If you want to measure several times to get an average, you can use the `run_times` parameter.

- For more precise time execution, it is recommended to set `concurrency_mode` to `False`. Please see the [Concurrency](#concurrency) section to understand the limitations of concurrency.

- Recursive functions should be encapsulated for better benchmarking. Please refer to the [Recursive functions](#recursive-functions) section to to learn more about recursion and `tempit`.

- Decorating classes will return the class unmodified and will not be decorated. For more information about this decision, please see the [Why is class decoration bypassed](#why-is-class-decoration-bypassed) in the [Other Limitations](#other-limitations) section.

## Recursive Functions

Measuring the execution time of recursive functions using decorators can be challenging due to potential verbosity in the output. This package offers an automatic recursion detection feature, but it is strongly recommended to use the [encapsulating the recursive function](#encapsulating-the-recursive-function) solution for cleaner, more precise, and safer results.

### Using the Auto-Recursion Feature

The auto-recursion feature detects recursion in the decorated function by checking the parent call function. If recursion is found, it will only output the time taken to run the appropriate function, plus an overhead. It is not recommended to rely on this feature intentionally since the collected time data will not be accurate and the process will take longer.

This feature is intended for passive use in case the user forgets to encapsulate the recursive function or for non-accurate comparisons.

```python
@tempit(run_times=3, concurrent_execution=True, verbose=False)
def recursive_func(n):
    if n == 0:
        return 0
    else:
        return n + recursive_func(n - 1)


# This will trigger the auto-recursion feature
result = recursive_func(3)
```

### Encapsulating the Recursive Function

The recommended option is to encapsulate the recursive function within another function and then, decorate and call the parent function. Here's an example:

```python
@tempit
def encapsulated_recursive_function(n):
    """A non-verbose wrapper for the recursive function."""
    def recursive_func(n):
        if n == 0:
            return 0
        else:
            return n + recursive_func(n - 1)

    return recursive_func(n)

# Encapsulating the recursive function
result = encapsulated_recursive_function(3)
```

This approach enhances readability without incurring any performance penalties. However, its main drawback is that users must modify their code to measure this type of function.

## Concurrency

### How Concurrency Works in timeit

`tempit` uses [joblib](https://pypi.org/project/joblib/) for parallel computing. By default, the execution backend is "loky". If a `PicklingError` occurs while trying to execute the decorated function, `tempit` switches the backend to "threading" and retries the execution. If any other error occurs with "loky" or "threading", `tempit` falls back to sequential execution, discarding the joblib option.

The "threading" backend is chosen if `tempit` is detected to be running outside the MainProcess or MainThread.

The number of workers for any parallel execution is `num_processors - 1`. While this may not always be the optimal approach (especially for multithreading with large I/O operations), simplicity of use has been prioritized over complexity for this decorator.

Additionally, if the `run_times` parameter exceeds `num_processors - 1`, it will be downsized to match the number of available processors minus one to maximize parallelization. Finally, if `tempit` detects that it is running in concurrency mode and finds that the downsized `run_times` is equal to 1, `tempit` falls back to sequential execution, discarding the joblib option.

### Concurrency Caveats

There are some caveats when using parallel computing. Creating a process or thread incurs overhead, so it's normal to find that for very low CPU-intensive functions, the concurrent mode may be slower than the sequential one. However, as the functions become more CPU-intensive, concurrency usually results in faster execution times.

That being said, timings measured when using concurrent executions may not be as accurate as those in sequential mode.

## Other Limitations

While this package generally delivers excellent performance and reliability, it's essential to be aware of certain scenarios where using the `tempit` decorator could lead to unexpected behavior.

### Why is Class Decoration Bypassed?

When a class is decorated using `tempit`, it remains unmodified and is not decorated. If the user intends to measure the time of `__init__` or any other constructor, it can be done directly on those methods.

This design decision was made due to a potential issue that arises when a decorated class is used in conjunction with spawning a new process. Specifically, if a class decorated with `tempit` is pickled for use in a separate process and then a method is called within that new process, it may result in a `PicklingError`.

### Zero Values

In some rare cases where multiple recursively decorated functions are called nested within each other, `tempit` may return some zero values for the measurements of the inner functions.

## Error Management and Warnings

### Errors

If an error occurs while executing the decorated function in sequential mode or within a recursively decorated function, the error will be propagated to the user's function.

### Warnings

- Deprecation warnings will be added before removing a feature.

- If the `run_times` parameter exceeds `num_processors - 1`, it will be downsized to match the number of available processors minus one to maximize parallelization.

- If recursion has been detected, a warning will be prompted. If so, please, go to [Recursive functions](#recursive-functions).

## Contributing

Contributions are welcome! Please follow these guidelines when contributing:

1. Fork the repository.
2. Use `make install` to install all dependencies.
3. Create a new branch for your changes.
4. Implement your changes and commit them.
5. Push your changes to your forked repository.
6. Submit a pull request.

You can also open an issue if you find a bug or have a suggestion.

You can test your code using `make test` and `make example` to trigger the examples. Please, check the [Makefile](https://github.com/mcrespoae/tempit/blob/main/Makefile) to know more about commands.

## Testing

The package has been thoroughly tested using unittesting. Test cases can be found in the [tests folder](https://github.com/mcrespoae/tempit/tree/main/tests).

## License

This project is licensed under the [MIT License](https://github.com/mcrespoae/tempit/blob/main/LICENSE).

## Contributors

- [Mario Crespo](https://github.com/mcrespoae)
