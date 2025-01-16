def generate_reciprocal_sqrt_table_binary():
    """
    Generates a table of reciprocal square root values in binary representation.
    Keys:
        - Represented as 11-bit binary strings (2 bits integer + 12 bits fractional).
    Values:
        - The reciprocal square root as 19-bit binary strings (6 bits integer + 12 bits fractional).
    
    Returns:
        dict: A dictionary where keys and values are binary strings.
    """
    table = {}
    max_key = (1 << 14) - 1  # Maximum value with 11 bits

    for key in range(1, max_key + 1):  # Start from 1 to avoid division by zero
        # Key as a binary string
        key_binary = f"{key:014b}"  # Format as 11-bit binary
        key_formatted = f'{key_binary[:2]}_{key_binary[2:]}'
        
        # Convert key to a fixed-point value
        fixed_key = key / 2**12  # Scale the binary key to its real fixed-point value

        # Calculate the reciprocal square root
        reciprocal_sqrt = 1 / (fixed_key ** 0.5)

        # Convert the reciprocal square root to a fixed-point binary representation
        fixed_value = int(round(reciprocal_sqrt * 2**12))
        max_value = (1 << 18) - 1  # Maximum 24-bit value
        fixed_value = min(fixed_value, max_value)

        # Value as a binary string
        value_binary = f"{fixed_value:018b}"  # Format as 24-bit binary
        value_formatted = f"{value_binary[:6]}_{value_binary[6:]}"

        # Store in the table
        table[key_formatted] = value_formatted

    return table

# Generate the table
reciprocal_sqrt_table_binary = generate_reciprocal_sqrt_table_binary()

# Example: Display a few entries of the table
idx = 0

print("module reciprocal_sqrt_rom(KEY, VALUE);")
print("  input [14:0] KEY;")
print("  output reg [18:0] VALUE;\n")

print("  always @(KEY)begin")
print("    case (KEY)")
for key, value in list(reciprocal_sqrt_table_binary.items())[:]:
    print(f"      15'b0{key} : VALUE=19'b0{value};")

print("    endcase")
print("  end")
print("endmodule")
