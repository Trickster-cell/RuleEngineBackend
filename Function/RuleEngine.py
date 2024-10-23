import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  # "operator" or "operand"
        self.left = left  # Left child (could be another Node)
        self.right = right  # Right child (could be another Node)
        self.value = value if value is not None else "N/A"  # Default value if not specified

def combine_rules(rules):
    combined_ast = None

    for rule in rules:
        rule_ast = create_rule(rule)
        if combined_ast is None:
            combined_ast = rule_ast
        else:
            combined_ast = Node("operator", combined_ast, rule_ast, "OR")  # Combine with AND for simplicity

    return combined_ast

def print_ast(node, level=0, count=None):
    if count is None:
        count = [1]  # Initialize count at the top level

    if node is not None:
        # Determine the label based on the current level
        label_prefix = chr(ord('A') + level)  # A for level 0, B for level 1, etc.
        label = f"{label_prefix}{count[level]}"  # Use count for the current level

        # Print the node type and value
        print("    " * level + f"{label}: {node.node_type}: {node.value if node.value is not None else ''}")

        # Increment the counter for the current level
        count[level] += 1

        # Reset the counter for child levels
        next_level_count = count.copy()
        next_level_count.append(1)  # Start new count for the next level

        # Print left and right children
        print_ast(node.left, level + 1, next_level_count)
        print_ast(node.right, level + 1, next_level_count)
        
def create_rule(rule_string):
    # Tokenize the rule string using regex


    tokens = re.findall(r'(\w+|[<>=!]+|AND|OR|\(|\))', rule_string)
    # print(tokens)
    
    def parse_expression(index):
        # print(index)
        token = tokens[index]
        if token == '(':
            left_node, index = parse_expression(index + 1)
            assert tokens[index] == ')', f"Expected closing parenthesis1"
            index += 1
            if index < len(tokens) and tokens[index] in ('AND', 'OR'):
                operator = tokens[index]  # AND/OR operator
                index+=1
                
                right_node, index = parse_expression(index+1)
                
                assert tokens[index] == ')', "Expected closing parenthesis2"
                index += 1
                return Node("operator", left_node, right_node, operator), index
            else:
                
                default_right_node = Node("default", left=None, right=None, value="default")  # Placeholder
                
                return Node("operator", left_node, default_right_node, "AND"), index
        else:
            attribute = token
            operator = tokens[index + 1]
            value = tokens[index + 2].strip("'")  # Remove quotes for strings
            index += 3
            return Node("value", left=Node("attribute", None, None, attribute), right=Node("comparator", None, None, operator), value=value), index

    # Parse the entire expression
    ast_root, _ = parse_expression(0)

    return ast_root


def evaluate_data_on_rules(rule_node, data):
    if rule_node is None:
        return True
    
    if rule_node.node_type == "operator":
        left_value = evaluate_data_on_rules(rule_node.left, data)
        right_value = evaluate_data_on_rules(rule_node.right, data)

        if rule_node.value == "OR":
            return left_value or right_value
        elif rule_node.value == "AND":
            return left_value and right_value

    elif rule_node.node_type == "value":
        attribute = rule_node.left.value
        comparator = rule_node.right.value
        stored_value = rule_node.value
        expected_value = data.get(attribute)

        if expected_value is None:
            return False

        if comparator == "=":
            return expected_value == stored_value
        elif comparator == ">":
            return expected_value > float(stored_value)
        elif comparator == "<":
            return expected_value < float(stored_value)
        else:
            raise ValueError(f"Unsupported Comparator: {comparator}")
    
    elif rule_node.node_type == "default":
        return True
    elif rule_node.node_type == "attribute":
        raise ValueError(f"Unexpected attribute node evaluation")
    elif rule_node.node_type == "comparator":
        raise ValueError(f"Unexpected comparator node evaluation")
    
    return False


# Example usage
# rule_string = "((age > 30) AND (exp < 2))"
# rule_string = "(age > 30)"
rule_string = "((((age > 30) AND (department = 'Sales')) OR ((age < 25) AND (department = 'Marketing'))) AND ((salary > 50000) OR (experience > 5)))"
# ast_rule = create_rule(rule_string)

rules = [
    "((((age > 30) AND (department = 'Sales')) OR ((age < 25) AND (department = 'Marketing'))) AND ((salary > 50000) OR (experience > 5)))", "(((age > 30) AND (department = 'Marketing')) AND ((salary > 20000) OR (experience > 5)))"
    ]

combined_ast = combine_rules(rules)


# Printing the AST
# print("AST for the rule:")
# print_ast(ast_rule)

# print_ast(combined_ast)

context = {
    'age': 32,
    'department': 'Sales',
    'salary': 60000
}

result = evaluate_data_on_rules(combined_ast, context)

print(result)