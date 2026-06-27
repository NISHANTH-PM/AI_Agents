import os
import pandas as pd
from datetime import datetime

# MCP Tool Registry
TOOLS = {}

def mcp_tool(name, description):
    def decorator(func):
        TOOLS[name] = {
            "function": func,
            "description": description
        }
        return func
    return decorator

@mcp_tool("get_member_count", "Get total number of members by status")
def get_member_count(status: str = "all"):
    df = pd.read_csv("data/members.csv")
    if status == "all":
        return {"count": len(df)}
    return {"count": len(df[df['is_active'] == (status == "active")])}

@mcp_tool("get_event_stats", "Get event statistics like average attendance")
def get_event_stats():
    df = pd.read_csv("data/events.csv")
    return {
        "total_events": len(df),
        "avg_attendance_rate": round(df['attendance_rate'].mean(), 2),
        "avg_satisfaction": round(df['satisfaction_score'].mean(), 2)
    }

@mcp_tool("get_finance_summary", "Get financial summary including total spending")
def get_finance_summary():
    df = pd.read_csv("data/finance.csv")
    return {
        "total_transactions": len(df),
        "total_amount": round(df['amount'].sum(), 2),
        "pending_count": len(df[df['status'] == 'Pending'])
    }

@mcp_tool("get_project_status", "Get project completion statistics")
def get_project_status():
    df = pd.read_csv("data/projects.csv")
    return {
        "total_projects": len(df),
        "avg_completion": round(df['completion_pct'].mean(), 2),
        "at_risk": len(df[(df['completion_pct'] < 50) & (df['status'] == 'Active')])
    }

@mcp_tool("get_communication_stats", "Get communication engagement statistics")
def get_communication_stats():
    df = pd.read_csv("data/communications.csv")
    return {
        "total_messages": len(df),
        "avg_open_rate": round(df['open_rate'].mean(), 2),
        "avg_click_rate": round(df['click_rate'].mean(), 2)
    }

def call_tool(tool_name: str, **kwargs):
    tool = TOOLS.get(tool_name)
    if not tool:
        return {"error": f"Tool {tool_name} not found"}
    return tool["function"](**kwargs)

def list_tools():
    return {name: tool["description"] for name, tool in TOOLS.items()}