from tempit import tempit


@tempit
def wrapper_recursive_func_nocheck(n):
    def recursive_func_wrapped(n):
        if n < 2:
            return n
        return recursive_func_wrapped(n - 2) + recursive_func_wrapped(n - 1)

    return recursive_func_wrapped(n)


@tempit(run_times=1, check_for_recursion=False)
def wrapper_recursive_func_check(n):
    def recursive_func_wrapped(n):
        if n < 2:
            return n
        return recursive_func_wrapped(n - 2) + recursive_func_wrapped(n - 1)

    return recursive_func_wrapped(n)


@tempit(run_times=1, check_for_recursion=False)
def recursive_func(n):
    if n < 2:
        return n
    return recursive_func(n - 2) + recursive_func(n - 1)


@tempit
def non_recursive_func(n):
    return n


def main():

    print("---OTHER EXAMPLES---")
    a = wrapper_recursive_func_nocheck(16)
    b = wrapper_recursive_func_check(16)
    c = recursive_func(16)
    print(a, b, c)
    print("---END OTHER EXAMPLES---")


if __name__ == "__main__":
    main()
