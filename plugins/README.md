# Cheshire Cat AI toolkit plugins

## Overview

This repository contains a preliminary plugin for the Cheshire Cat AI framework, designed to demonstrate the integration of custom tools. Please note that this plugin is intended solely for testing purposes and will not be included in the final release.

## What is a Plugin?

In the context of the Cheshire Cat AI framework, a **plugin** is a package that extends the functionality of the core system by introducing new tools and hooks. These plugins enable developers to customize and enhance the capabilities of their AI agents. A plugin typically consists of:

- **Tools**: Python functions that can be invoked by the AI agent to perform specific tasks.
- **Hooks**: Functions that allow developers to modify the behavior of the AI agent at various points in its execution.

For a comprehensive guide on creating plugins, refer to the official [Cheshire Cat AI documentation](https://cheshire-cat-ai.github.io/docs/plugins/plugins/).

## Plugin Details

The included script defines a tool named `zero_order_equation`, which calculates the dependent variable `y` for a given set of independent variables `x` using the formula:

\[ y = a \times x + b \]

Where:
- `x`: A list of float values representing the independent variable.
- `a`: The slope of the linear equation (float).
- `b`: The intercept of the linear equation (float).

The function accepts a JSON string as input, processes the data, and returns a JSON string containing the calculated values.

**Note**: This script is intended for testing purposes and will not be part of the final release.

## Usage

To utilize this plugin within the Cheshire Cat AI framework, place the script in the `cat/plugins` directory.
