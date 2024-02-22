use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pymodule]
fn string_sum(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}

/*
The code is written in Rust and uses the `pyo3` crate to create a Python module.
The `sum_as_string` function takes two `usize` arguments `a` and `b` and returns a `PyResult<String>`. It calculates the sum of `a` and `b`, converts it to a string using the `to_string()` method, and wraps it in a `PyResult` to handle any potential errors.
The `string_sum` function is the entry point of the module. It takes two arguments: `_py`, which is a reference to the Python interpreter, and `m`, which is a reference to the `PyModule` struct. The function adds the `sum_as_string` function to the module using the `add_function` method of `PyModule`. The `wrap_pyfunction!` macro is used to wrap the `sum_as_string` function in a Python-compatible wrapper. Finally, the function returns `Ok(())` to indicate that the module was successfully created.

The code `<'_>` is a lifetime annotation in Rust.
In Rust, lifetimes are used to ensure that references are always valid and prevent dangling references. They specify the scope for which a reference is valid.
In this code, `<'_>` is a shorthand syntax for an anonymous lifetime. It is used when the lifetime of a reference doesn't need to be explicitly named or specified. The underscore `_` represents a placeholder for the anonymous lifetime.
This syntax is often used when working with closures or function signatures that accept references. It allows the compiler to infer the appropriate lifetime for the reference based on its usage within the code.
*/
