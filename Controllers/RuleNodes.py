from Models.NodeModel import Node, create_rule, BaseNode, combine_rules
from db import collection, final_node_collection
from Models.StringWithNode import StringWithNode,StringWithNodeCollection



async def create_dummy_node():
    node = Node(node_type="dummy")
    await collection.insert_one(dict(node))


async def save_node(node:BaseNode):

    # new_node = Node(node_type={node.node_type}, value={node.value})    
    new_node = Node(node_type=node.node_type, value=node.value)
    # print(new_node)

    # return new_node
    result = await collection.insert_one(new_node.model_dump(by_alias=True, exclude=["id"]))
    # return result
    # new_node_id = str(result.inserted_id)
    # return str(result.inserted_id)

    # print("Node inserted with ID:", repr(result.inserted_id))

    if node.left:
        left_child = await save_node(node.left)
        await collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"left": left_child.inserted_id}}
        )
        # print(f"Updated node {str(result.inserted_id)} with left child ID: {left_child_id}")

    if node.right:
        right_child = await save_node(node.right)
        await collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"right": right_child.inserted_id}}
        )
        # print(f"Updated node {str(result.inserted_id)} with right child ID: {right_child_id}")

    return result


async def add_rule_and_save(rule:str, name:str):
    ast = await create_rule(rule)
    # print(type(ast.node_type), type(ast.value), type(ast.left), type(ast.right))
    node = await save_node(ast)

    new_str_node = StringWithNode(finalString=rule, name=name)

    new_db_str = await final_node_collection.insert_one(new_str_node.model_dump(by_alias=True, exclude=["id"]))

    await final_node_collection.update_one(
        {"_id": new_db_str.inserted_id},
        {"$set":{"node_id":node.inserted_id}}
        )

    node_id = str(new_db_str.inserted_id)
    # print(node_id)
    return node_id

# async def add_final_string(rule_string: str, )

from typing import List

async def add_and_save_combined_rules(rules: List[str], combineType: str, name:str):
    combined_ast = await combine_rules(rules, combineType)

    node = await save_node(combined_ast)

    finalStr = "("

    for index, rule in enumerate(rules):
        if(index!=0):
            finalStr += " " + combineType + " "
        finalStr += rule
    
    finalStr += ")"

    # print(finalStr)

    new_str_node = StringWithNode(finalString=finalStr, name=name)

    new_db_str = await final_node_collection.insert_one(new_str_node.model_dump(by_alias=True, exclude=["id"]))

    await final_node_collection.update_one(
        {"_id": new_db_str.inserted_id},
        {"$set":{"node_id":node.inserted_id}}
        )


    return str(new_db_str.inserted_id)

from bson import ObjectId

async def delete_node(nodeId: ObjectId):
    node = await collection.find_one(nodeId)
    if node:
        if node["left"]:
            await delete_node(node["left"])
        if node["right"]:
            await delete_node(node["right"])
        
        await collection.delete_one({"_id":nodeId})

async def delete_rule(prevId: str):

    node = await final_node_collection.find_one({"_id":ObjectId(prevId)})

    # print(node["node_id"])
    if node:
        # print(1)
        await delete_node(node["node_id"])

        delete_result = await final_node_collection.delete_one({"_id":ObjectId(prevId)})

        return delete_result.deleted_count == 1
    
    return False

async def get_ast_from_rule_id(objId: ObjectId)->BaseNode:
    if objId is None:
        return None
    node_in_db = await collection.find_one({"_id":objId})

    if node_in_db is None:
        return None
    
    left_node = await get_ast_from_rule_id(node_in_db["left"])
    right_node = await get_ast_from_rule_id(node_in_db["right"])

    return BaseNode(node_type=node_in_db["node_type"], left=left_node, right=right_node, value=node_in_db["value"])



async def get_ast_from_final_rule_id(rule_id: str)->BaseNode:
    rule_node = await final_node_collection.find_one({"_id":ObjectId(rule_id)})

    rule_db_id = rule_node["node_id"]

    baseNode = await get_ast_from_rule_id(rule_db_id)

    return baseNode


async def generate_rule_string(node: BaseNode) -> str:

    if isinstance(node, BaseNode):
        if node.node_type == "operator":
            left_str = await generate_rule_string(node.left)
            right_str = await generate_rule_string(node.right)
            return f"({left_str} {node.value} {right_str})"
        
    
        elif node.node_type == "value":
            attribute_str = await generate_rule_string(node.left)  

            comparator_str =await generate_rule_string(node.right)  
            return f"{attribute_str} {comparator_str} '{node.value}'"
        

        elif node.node_type in {"attribute", "comparator"}:
            return node.value
        

        elif node.node_type == "default":
            return "default"

    return ""
    
async def combine_preset_rules_in_db(list_of_ids: List[str], list_of_combine_type:List[str]):

    final_ast = await get_ast_from_final_rule_id(list_of_ids[0])
    
    for i in range(1,len(list_of_ids)):
        ast_temp = await get_ast_from_final_rule_id(list_of_ids[i])
        combined_type = list_of_combine_type[i-1]
        final_ast = BaseNode(node_type="operator", left=final_ast, right=ast_temp, value=combined_type)

    final_str = await generate_rule_string(final_ast)
    # print(final_str)

    new_node = await save_node(final_ast)

    new_str_node = StringWithNode(finalString=final_str)

    new_db_str = await final_node_collection.insert_one(new_str_node.model_dump(by_alias=True, exclude=["id"]))

    await final_node_collection.update_one(
        {"_id": new_db_str.inserted_id},
        {"$set":{"node_id":new_node.inserted_id}}
        )

    node_id = str(new_db_str.inserted_id)
    # print(node_id)
    return node_id

    



async def generate_rule_json_custom(node: BaseNode) -> dict:
    if isinstance(node, BaseNode):
        node_json = {"name": node.value}  # Use `name` for node type
        
        # Add attributes if it's a value, attribute, or comparator node
        if node.node_type == "value":
            node_json["attributes"] = {
                # "attribute": node.left.value if node.left else None,
                # "comparator": node.right.value if node.right else None,
                # "value": node.value,
                "final": f"{node.left.value if node.left else True} {node.right.value if node.right else True} {node.value}"
            }
        elif node.node_type == "attribute":
            node_json["attributes"] = {"attribute": node.value}
        elif node.node_type == "comparator":
            node_json["attributes"] = {"comparator": node.value}
        
        # Add children for operator nodes
        if node.node_type == "operator":
            node_json["children"] = []
            if node.left:
                node_json["children"].append(await generate_rule_json_custom(node.left))
            if node.right:
                node_json["children"].append(await generate_rule_json_custom(node.right))
        
        # Add children for value nodes (considering attributes as left/right children)
        if node.node_type == "value" and node.left and node.right:
            node_json["children"] = [
                await generate_rule_json_custom(node.left),
                await generate_rule_json_custom(node.right)
            ]

        return node_json

    return {}

async def get_json_from_rule_id(idx: str):
    ast = await get_ast_from_final_rule_id(idx)

    data = await generate_rule_json_custom(ast)

    return data


async def evaluate_json_from_base_node(node: BaseNode, data:dict):
    if node is None:
        return True
    
    if node.node_type == "operator":
        left_value = await evaluate_json_from_base_node(node.left, data)
        right_value = await evaluate_json_from_base_node(node.right, data)

        if node.value=="OR":
            return left_value or right_value
        elif node.value=="XOR":
            return left_value ^ right_value
        elif node.value=="AND":
            return left_value and right_value
    
    elif node.node_type == "value":
        attribute = node.left.value
        comparator = node.right.value
        stored_value = node.value

        expected_value = data.get(attribute)

        if expected_value is None:
            return False
        
        if comparator == "=":
            return expected_value == stored_value
        elif comparator == ">":
            return expected_value > float(stored_value)
        elif comparator == "<":
            return expected_value < float(stored_value)
        elif comparator == ">=":
            return expected_value >= float(stored_value)
        elif comparator == "<=":
            return expected_value <= float(stored_value)
        elif comparator == "!=":
            if re.match(r'^-?\d+(\.\d+)?$', string):
                return expected_value != float(stored_value)
            return expected_value != stored_value
        else:
            raise ValueError(f"Unsupprted Comparator: {comparator}")
    
    elif node.node_type == "default":
        return True
    elif node.node_type == "attribute":
        raise ValueError(f"Unexpected attribute node evaluation")
    elif rule_node.node_type == "comparator":
        raise ValueError(f"Unexpected comparator node evaluation")

    return False 

async def evaluate_json_on_rule_id(rule_id: str, json_data: dict):
    ast = await get_ast_from_final_rule_id(rule_id)

    finalVal = await evaluate_json_from_base_node(ast, json_data)

    return finalVal

    


async def get_all_rules_from_db():
    rules = StringWithNodeCollection(nodes = await final_node_collection.find().to_list())
    # print(rules)
    return rules