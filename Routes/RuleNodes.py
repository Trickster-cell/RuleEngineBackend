from fastapi import APIRouter, Body, HTTPException
from Controllers.RuleNodes import (
    create_dummy_node,
    get_json_from_rule_id,
    add_rule_and_save,
    add_and_save_combined_rules,
    delete_rule,
    combine_preset_rules_in_db,
    evaluate_json_on_rule_id,
    get_all_rules_from_db
)
from typing import List

router = APIRouter()

@router.get("/dummy")
async def createDummy():
    try:
        await create_dummy_node()  # Create a dummy node in the database
        return {"message": "Dummy node created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-rule")
async def add_rule_in_db(rule: str = Body(...), name: str = Body(...)):
    try:
        new_node_id = await add_rule_and_save(rule, name)  # Add a new rule to the database
        return new_node_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/combine-rule")
async def combine_rule_in_db(rules: List[str] = Body(...), combineType: str = Body(...), name: str = Body(...)):
    try:
        print(rules)  # Log the rules being combined
        new_node_id = await add_and_save_combined_rules(rules, combineType, name)  # Combine and save rules
        return new_node_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-rule")
async def delete_rule_from_db(prevId: str = Body(...)):
    try:
        response = await delete_rule(prevId)  # Delete a rule by ID

        if response:
            return {"message": "Rule Deleted"}
        
        raise HTTPException(status_code=404, detail="Invalid Rule Id")  # Raise error if rule ID is invalid
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/combine-preset-rules")
async def combine_preset_rules(list_of_ids: List[str] = Body(...), list_of_combineTypes: List[str] = Body(...)):
    try:
        if (len(list_of_combineTypes) + 1) != len(list_of_ids):  # Validate combine types against IDs
            raise HTTPException(status_code=400, detail="Invalid number of combine types")
        
        new_id = await combine_preset_rules_in_db(list_of_ids, list_of_combineTypes)  # Combine preset rules
        return new_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/json")
async def get_json_of_node(idx: str):
    try:
        return await get_json_from_rule_id(idx)  # Retrieve JSON representation of a rule by ID
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/evaluate")
async def evaluate_data_on_rule(idx: str, data: dict):
    try:
        return await evaluate_json_on_rule_id(idx, data)  # Evaluate data against a rule by ID
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/allRules")
async def get_all_rules():
    try:
        return await get_all_rules_from_db()  # Retrieve all rules from the database
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
