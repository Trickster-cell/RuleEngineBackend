from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

# Type alias for ObjectId with a before validator to ensure it is a string
PyObjectId = Annotated[str, BeforeValidator(str)]

class Node(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)  # Unique identifier for the node
    node_type: str  # Type of the node (e.g., operator or operand)
    left: Optional[PyObjectId] = Field(default=None)  # Left child node reference
    right: Optional[PyObjectId] = Field(default=None)  # Right child node reference
    value: Optional[Union[str, int, float]] = Field(default=None)  # Value of the node (string, int, or float)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow arbitrary types for fields
        json_encoders={ObjectId: str}  # Encoder to convert ObjectId to string for JSON serialization
    )

import re

class BaseNode:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  # Type of the node (e.g., operator or operand)
        self.left = left  # Left child (could be another Node)
        self.right = right  # Right child (could be another Node)
        self.value = value if value is not None else "N/A"  # Default value if not specified

async def create_rule(rule_string: str) -> BaseNode:
    # Tokenize the rule string using regex
    tokens = re.findall(r'(\w+|!=|>=|<=|[<>=!]+|AND|XOR|OR|\(|\))', rule_string)
    
    async def parse_expression(index: int):
        token = tokens[index]
        
        if token == '(':
            left_node, index = await parse_expression(index + 1)  # Parse the left subtree
            assert tokens[index] == ')', f"Expected closing parenthesis after left node"
            index += 1
            
            if index < len(tokens) and tokens[index] in ('AND', 'OR', 'XOR'):
                operator = tokens[index]  # Logical operator
                index += 1
                
                right_node, index = await parse_expression(index + 1)  # Parse the right subtree
                
                assert tokens[index] == ')', "Expected closing parenthesis after right node"
                index += 1
                
                # Create an operator node
                return BaseNode(node_type="operator", left=left_node, right=right_node, value=operator), index
            else:
                # Default handling for missing right operand
                default_right_node = BaseNode(node_type="default", left=None, right=None, value="default")
                return BaseNode(node_type="operator", left=left_node, right=default_right_node, value="AND"), index
        else:
            # Handle attribute, operator, and value
            attribute = token
            operator = tokens[index + 1]
            value = tokens[index + 2].strip("'")  # Remove quotes for strings
            
            index += 3
            
            # Create nodes for attribute, comparator, and value
            return BaseNode(node_type="value", 
                            left=BaseNode(node_type="attribute", left=None, right=None, value=attribute),
                            right=BaseNode(node_type="comparator", left=None, right=None, value=operator),
                            value=value), index

    # Parse the entire expression
    ast_root, _ = await parse_expression(0)
    
    return ast_root

from typing import List

async def combine_rules(rules: List[str], combineType: str) -> BaseNode:
    combined_ast = None

    for rule in rules:
        rule_ast = await create_rule(rule)  # Create AST for each rule
        if combined_ast is None:
            combined_ast = rule_ast  # Initialize combined AST
        else:
            # Combine with the specified combine type (e.g., AND)
            combined_ast = BaseNode(node_type="operator", left=combined_ast, right=rule_ast, value=combineType)

    return combined_ast
