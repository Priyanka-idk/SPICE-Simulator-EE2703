# SPICE Circuit Simulator

A Python-based SPICE circuit simulator that parses circuit netlist files, constructs system matrices using nodal analysis, and solves for node voltages and branch currents in resistive circuits.

## Features

- **Node Mapping**: Automatically assigns unique indices to nodes.
- **SPICE File Parsing**: Reads and extracts information about resistors, voltage sources, and current sources from a SPICE netlist file.
- **Matrix Formation**: Constructs nodal matrices to represent the circuit equations.
- **Solution Calculation**: Solves the system of linear equations to compute node voltages and branch currents.
- **Error Handling**: Detects malformed circuit files, duplicate component names, and invalid inputs.

## How It Works

1. **Input**: Provide a valid SPICE netlist file containing the circuit description.
2. **Parsing**: The program identifies circuit elements (resistors, voltage sources, and current sources) and assigns indices to nodes.
3. **Matrix Construction**: Forms a system of equations based on the nodal analysis method.
4. **Solving**: Uses numerical methods to solve the equations and compute the results.

## Usage
### Running the Simulator
Use the `evalSpice` function to evaluate a SPICE file:

```python
from simulator import evalSpice

filename = "circuit.netlist"  # Path to your SPICE netlist file
voltages, currents = evalSpice(filename)

print("Node Voltages:", voltages)
print("Branch Currents:", currents)
```

### Input File Format
- The input SPICE file must start with `.circuit` and end with `.end`.
- Supported components:
  - **Resistors**: Format - `R<name> <node1> <node2> <value>`
  - **Voltage Sources**: Format - `V<name> <node1> <node2> <value>`
  - **Current Sources**: Format - `I<name> <node1> <node2> <value>`

### Example Input
```text
.circuit
R1 1 0 1000
R2 2 0 2000
R3 1 2 1500
V1 1 0 10
I1 2 0 0.002
.end
```

### Output
- **Node Voltages**: Dictionary mapping node names to their voltages.
- **Branch Currents**: Dictionary mapping voltage source names to their currents.

## Error Handling
The simulator raises exceptions for the following scenarios:
- Missing `.circuit` or `.end` lines.
- Duplicate component names.
- Invalid or missing component values.
- Singular matrices (circuit with no solution).

## Limitations
- Supports only resistive circuits with independent voltage and current sources.
