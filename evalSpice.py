from typing import Dict, List, Tuple
import numpy as np


def mapping_nodes(
    node_name: str, node_mapping: Dict[str, int], node_counter: int
) -> Tuple[int, int]:
    """
    Assigns a unique index to each node in the circuit.

    Arguments:
        node_name (str): Name of the node.
        node_mapping (dict): Dictionary mapping node names to unique integer indices.
        node_counter (int): Counter to assign the next index for new nodes.

    Returns:
        The integer assigned to the node and the final value of the node counter.
    """
    if node_name not in node_mapping:
        node_mapping[node_name] = node_counter
        node_counter += 1
    return node_mapping[node_name], node_counter


def parsing(
    filename: str,
) -> Tuple[
    List[Dict[str, str]],
    List[Dict[str, str]],
    List[Dict[str, str]],
    Dict[str, int],
    int,
]:
    """
    Parses through the SPICE circuit file, valid circuit information is between the first .circuit line and the first .end line of the file and extracts information about resistors,
    voltage sources, and current sources.

    Arguments:
        filename (str): Path to the input SPICE file.

    Returns:
        Lists of dictionaries storing information about resistors, voltage sources, and current sources, along with
        node mapping and the total number of nodes.

    Raises:
        FileNotFoundError: Raises error if the file is not found.
        ValueError: Raises error if the file is malformed or has invalid components, has duplicate entries or insufficient data to access from.

    """
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            node_mapping = {"GND": 0}  # Ground node is assigned default 0
            Resistors: List[Dict[str, str]] = []
            Voltage_sources: List[Dict[str, str]] = []
            Current_sources: List[Dict[str, str]] = []
            node_counter = 1  # Starts from 1 because 0 is reserved for GND
            Junk = True  # Flag when it's outside the valid circuit
            count = 0
            num_lines = len(lines)

            # Sets to track unique names
            resistor_names = set()
            voltage_source_names = set()
            current_source_names = set()

            # Ensures that there is a '.circuit'
            for line in range(num_lines):
                if lines[line].strip() != ".circuit":
                    count += 1
            if count == len(lines):
                raise ValueError("Malformed circuit file")

            # Ensures that there is an '.end'
            count = 0
            for line in range(num_lines):
                if lines[line].strip() != ".end":
                    count += 1
            if count == len(lines):
                raise ValueError("Malformed circuit file")

            # Parsing the actual circuit elements
            for line in lines:
                if line.strip() == ".circuit":
                    Junk = False
                    continue
                elif line.strip() == ".end":
                    Junk = True
                    continue
                if not Junk:
                    words = line.split()  # Split the line into components
                    if len(words) > 0:
                        element_type = words[0][
                            0
                        ].upper()  # Taking the first character of each line to identify element type (R, V, I)
                        n1, n2 = words[1], words[2]
                        n1, node_counter = mapping_nodes(n1, node_mapping, node_counter)
                        n2, node_counter = mapping_nodes(n2, node_mapping, node_counter)

                        if element_type == "R":
                            # Checks for duplicate entries where two components ahve the same name
                            if words[0] in resistor_names:
                                raise ValueError("Duplicate resistor name found.")
                            resistor_names.add(words[0])
                            # Checks if there are enough data to access the value
                            if len(words) < 4:
                                raise ValueError(
                                    "Insufficient data to access resistor value."
                                )
                            value = words[3]
                            Resistor = {
                                "name": words[0],
                                "n1": str(n1),
                                "n2": str(n2),
                                "value": value,
                            }
                            Resistors.append(Resistor)
                        elif element_type == "V":
                            # Checks for duplicate entries where two components ahve the same name
                            if words[0] in voltage_source_names:
                                raise ValueError("Duplicate voltage source name found.")
                            voltage_source_names.add(words[0])
                            # Check if there are enough data to access the value
                            if len(words) < 5:
                                raise ValueError(
                                    "Insufficient data to access voltage source value."
                                )
                            value = words[4]
                            Voltage_source = {
                                "name": words[0],
                                "n1": str(n1),
                                "n2": str(n2),
                                "value": value,
                            }
                            Voltage_sources.append(Voltage_source)
                        elif element_type == "I":
                            # Checks for duplicate entries where two components ahve the same name
                            if words[0] in current_source_names:
                                raise ValueError("Duplicate current source name found.")
                            current_source_names.add(words[0])
                            # Check if there are enough elements to access the value
                            if len(words) < 5:
                                raise ValueError(
                                    "Insufficient data to access current source value."
                                )
                            value = words[4]
                            Current_source = {
                                "name": words[0],
                                "n1": str(n1),
                                "n2": str(n2),
                                "value": value,
                            }
                            Current_sources.append(Current_source)
                        else:
                            raise ValueError("Only V, I, R elements are permitted")
            return (
                Resistors,
                Voltage_sources,
                Current_sources,
                node_mapping,
                node_counter,
            )

    except FileNotFoundError:
        raise FileNotFoundError("Please give the name of a valid SPICE file as input")


def matrix_formation(
    Resistors: List[Dict[str, str]],
    Voltage_sources: List[Dict[str, str]],
    Current_sources: List[Dict[str, str]],
    node_mapping: Dict[str, int],
    node_count: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Forms the matrix of the circuit using the logic of nodal equations.

    Arguments:
        Resistors (list of dictionaries): Resistors, their node connections and values.
        Voltage_sources (list of dictionaries): voltage sources, their node connections and values.
        Current_sources (list of dictionaries): Current sources, their node connections and values.
        node_mapping (dicttionary): Node names mapped to their indices.
        node_count (int): Total number of unique nodes in the circuit + GND.

    Raises:
        TypeError: When the Value of different components are of invalid type.

    Returns:
        Two matrices - one representing the circuit using the coefficients of the unknowns in the nodal equations and the other representing the constants of the same equations.
    """
    total_nodes = node_count - 1
    total_voltage_sources = len(Voltage_sources)

    # Initialize matrices
    Matrix = np.zeros(
        (total_nodes + total_voltage_sources, total_nodes + total_voltage_sources)
    )
    Matrix_right = np.zeros((total_nodes + total_voltage_sources, 1))

    # Process resistors
    for Resistor in Resistors:
        n1 = int(Resistor["n1"])
        n2 = int(Resistor["n2"])
        if float(Resistor["value"]==0):
            raise ZeroDivisionError
        try:
            Y = 1 / float(Resistor["value"])
        except:
            raise TypeError("Malformed circuit file")

        if n1 != n2:
            if n1 != 0:
                Matrix[n1 - 1][n1 - 1] += Y
            if n2 != 0:
                Matrix[n2 - 1][n2 - 1] += Y
            if n1 != 0 and n2 != 0:
                Matrix[n1 - 1][n2 - 1] -= Y
                Matrix[n2 - 1][n1 - 1] -= Y
        else:
            Matrix[n1 - 1][n1 - 1] += Y

    # Process current sources
    for Current_source in Current_sources:
        n1 = int(Current_source["n1"])
        n2 = int(Current_source["n2"])
        try:
            I = float(Current_source["value"])
        except:
            raise TypeError("Malformed circuit file")
        if n1 != 0:
            Matrix_right[n1 - 1][0] -= I
        if n2 != 0:
            Matrix_right[n2 - 1][0] += I

    # Process voltage sources
    for i, Voltage_source in enumerate(Voltage_sources):
        n1 = int(Voltage_source["n1"])
        n2 = int(Voltage_source["n2"])
        try:
            V = float(Voltage_source["value"])
        except:
            raise TypeError("Malformed circuit file")
        if n1 != 0:
            Matrix[total_nodes + i][n1 - 1] = 1
            Matrix[n1 - 1][total_nodes + i] = 1
        if n2 != 0:
            Matrix[total_nodes + i][n2 - 1] = -1
            Matrix[n2 - 1][total_nodes + i] = -1
        Matrix_right[total_nodes + i][0] = V

    return Matrix, Matrix_right


def evalSpice(filename: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Evaluates the SPICE circuit by calling other necessary functions and computes node voltages and branch currents.

    Arguments:
        filename (str): The name of the SPICE file with the circuit information

    Returns:
        A dictionary of node voltages and a dictionary of branch currents.

    Raises:
        ValueError: Raises error if the circuit has no solution(singular matrix).
    """
    Resistors, Voltage_sources, Current_sources, node_mapping, node_count = parsing(
        filename
    )
    Matrix, Matrix_right = matrix_formation(
        Resistors, Voltage_sources, Current_sources, node_mapping, node_count
    )

    try:
        solution = np.linalg.solve(Matrix, Matrix_right)
    except np.linalg.LinAlgError:
        raise ValueError("Circuit error: no solution")

    # Compute node voltages
    voltages: Dict[str, float] = {}
    for node in node_mapping:
        if node == "GND":
            voltages[node] = 0
        else:
            i = int(node_mapping[node])
            if i <= len(solution):
                voltages[node] = float(solution[i - 1][0])

    # Compute currents for voltage sources
    currents: Dict[str, float] = {}
    idx = 0  # Initialize the index manually
    for Voltage_source in Voltage_sources:
        voltage_name = Voltage_source["name"]
        current_idx = node_count + idx - 1

        if current_idx < len(solution):  # Check if the index is within bounds
            currents[voltage_name] = float(
                solution[current_idx][0]
            )  # Assign current value

        idx += 1  # Increment index for the next voltage source

    return voltages, currents
