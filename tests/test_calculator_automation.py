import pytest
import asyncio
from src.app.core.ai.tools.calculator_tools import CalculatorTool
from src.app.core.ai.agent import LabeebAgent

@pytest.mark.asyncio
async def test_calculator_automation():
    """Test calculator automation functionality."""
    agent = LabeebAgent()
    calculator_tool = CalculatorTool()
    agent.register_tool(calculator_tool)

    # Test opening calculator
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'open'
    })
    assert result['success'] is True

    # Test moving mouse to clear button
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'move_and_click',
        'params': {'x': calculator_tool.calculator_positions['clear'][0],
                  'y': calculator_tool.calculator_positions['clear'][1]}
    })
    assert result['success'] is True

    # Test typing number 12
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'type_number',
        'params': {'number': '12'}
    })
    assert result['success'] is True

    # Test pressing enter
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'press_enter'
    })
    assert result['success'] is True

    # Test moving mouse to plus button
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'move_and_click',
        'params': {'x': calculator_tool.calculator_positions['plus'][0],
                  'y': calculator_tool.calculator_positions['plus'][1]}
    })
    assert result['success'] is True

    # Test typing number 2
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'type_number',
        'params': {'number': '2'}
    })
    assert result['success'] is True

    # Test moving mouse to equals button
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'move_and_click',
        'params': {'x': calculator_tool.calculator_positions['equals'][0],
                  'y': calculator_tool.calculator_positions['equals'][1]}
    })
    assert result['success'] is True

    # Test getting result
    result = await agent.execute({
        'tool': 'calculator',
        'action': 'get_result'
    })
    assert result['success'] is True 