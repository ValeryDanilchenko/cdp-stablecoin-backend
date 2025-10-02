#!/usr/bin/env python3
"""
CDP Demo API - Interactive Demo Script

This script demonstrates the key features of the CDP Demo API
by creating positions, simulating liquidations, and showing metrics.
"""

import asyncio
import json
from typing import Any

import httpx


class CDPDemoClient:
    """Client for interacting with the CDP Demo API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def create_position(self, position_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new CDP position."""
        response = await self.client.post(
            f"{self.base_url}/positions/",
            json=position_data
        )
        response.raise_for_status()
        return response.json()
    
    async def list_positions(self, limit: int = 10) -> list[dict[str, Any]]:
        """List CDP positions."""
        response = await self.client.get(
            f"{self.base_url}/positions/",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    async def simulate_liquidation(self, position_id: str) -> dict[str, Any]:
        """Simulate liquidation for a position."""
        response = await self.client.get(
            f"{self.base_url}/liquidation/simulate/{position_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def execute_liquidation(self, position_id: str, max_slippage_bps: int = 100) -> dict[str, Any]:
        """Execute liquidation for a position."""
        response = await self.client.post(
            f"{self.base_url}/liquidation/execute",
            json={
                "position_id": position_id,
                "max_slippage_bps": max_slippage_bps
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_system_metrics(self) -> dict[str, Any]:
        """Get system metrics."""
        response = await self.client.get(f"{self.base_url}/metrics/system")
        response.raise_for_status()
        return response.json()
    
    async def get_position_metrics(self) -> dict[str, Any]:
        """Get position metrics."""
        response = await self.client.get(f"{self.base_url}/metrics/positions")
        response.raise_for_status()
        return response.json()
    
    async def create_batch_positions(self, positions: list[dict[str, Any]]) -> dict[str, Any]:
        """Create multiple positions in batch."""
        response = await self.client.post(
            f"{self.base_url}/batch/positions",
            json={"positions": positions}
        )
        response.raise_for_status()
        return response.json()


async def run_demo():
    """Run the CDP Demo API demonstration."""
    print("?? CDP Demo API - Interactive Demonstration")
    print("=" * 50)
    
    client = CDPDemoClient()
    
    try:
        # 1. Health Check
        print("\n1. ?? Checking API Health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Timestamp: {health['timestamp']}")
        
        # 2. Create Sample Positions
        print("\n2. ?? Creating Sample Positions...")
        
        sample_positions = [
            {
                "position_id": "demo_pos_001",
                "owner_address": "0x1234567890123456789012345678901234567890",
                "collateral_symbol": "ETH",
                "collateral_amount": "10.0",
                "debt_symbol": "USDC",
                "debt_amount": "25000.0"
            },
            {
                "position_id": "demo_pos_002",
                "owner_address": "0x2345678901234567890123456789012345678901",
                "collateral_symbol": "WBTC",
                "collateral_amount": "1.0",
                "debt_symbol": "USDC",
                "debt_amount": "60000.0"
            },
            {
                "position_id": "demo_pos_003",
                "owner_address": "0x3456789012345678901234567890123456789012",
                "collateral_symbol": "ETH",
                "collateral_amount": "5.0",
                "debt_symbol": "USDC",
                "debt_amount": "15000.0"
            }
        ]
        
        for pos_data in sample_positions:
            try:
                position = await client.create_position(pos_data)
                print(f"   ? Created position: {position['position_id']}")
            except httpx.HTTPStatusError as e:
                print(f"   ? Failed to create {pos_data['position_id']}: {e.response.text}")
        
        # 3. List Positions
        print("\n3. ?? Listing All Positions...")
        positions = await client.list_positions(limit=10)
        print(f"   Found {len(positions)} positions:")
        for pos in positions:
            print(f"   - {pos['position_id']}: {pos['collateral_amount']} {pos['collateral_symbol']} ? {pos['debt_amount']} {pos['debt_symbol']}")
        
        # 4. Simulate Liquidations
        print("\n4. ?? Simulating Liquidations...")
        for pos in positions:
            try:
                simulation = await client.simulate_liquidation(pos['position_id'])
                status = "?? ELIGIBLE" if simulation['eligible'] else "?? SAFE"
                print(f"   {pos['position_id']}: {status} (HF: {simulation['health_factor']:.2f}, Profit: ${simulation['estimated_profit_usd']:.2f})")
            except httpx.HTTPStatusError as e:
                print(f"   ? Failed to simulate {pos['position_id']}: {e.response.text}")
        
        # 5. Execute Liquidations (for eligible positions)
        print("\n5. ? Executing Liquidations...")
        for pos in positions:
            try:
                simulation = await client.simulate_liquidation(pos['position_id'])
                if simulation['eligible']:
                    execution = await client.execute_liquidation(pos['position_id'])
                    print(f"   ? Liquidated {pos['position_id']}: TX {execution['tx_hash'][:10]}... (Profit: ${execution['realized_profit_usd']:.2f})")
                else:
                    print(f"   ??  Skipped {pos['position_id']}: Not eligible for liquidation")
            except httpx.HTTPStatusError as e:
                print(f"   ? Failed to execute liquidation for {pos['position_id']}: {e.response.text}")
        
        # 6. System Metrics
        print("\n6. ?? System Metrics...")
        try:
            system_metrics = await client.get_system_metrics()
            print(f"   Total Positions: {system_metrics['total_positions']}")
            print(f"   Liquidatable: {system_metrics['liquidatable_positions']}")
            print(f"   Average Health Factor: {system_metrics['average_health_factor']:.2f}")
            print(f"   System Status: {system_metrics['status']}")
        except httpx.HTTPStatusError as e:
            print(f"   ? Failed to get system metrics: {e.response.text}")
        
        # 7. Position Metrics
        print("\n7. ?? Position Risk Analysis...")
        try:
            position_metrics = await client.get_position_metrics()
            dist = position_metrics['health_distribution']
            print(f"   Health Distribution:")
            print(f"   - Safe: {dist['safe']} positions")
            print(f"   - Warning: {dist['warning']} positions")
            print(f"   - Critical: {dist['critical']} positions")
            print(f"   Average Health Factor: {position_metrics['average_health_factor']:.2f}")
            
            if position_metrics['riskiest_positions']:
                print("   Riskiest Positions:")
                for risky in position_metrics['riskiest_positions'][:3]:
                    print(f"   - {risky['position_id']}: HF {risky['health_factor']:.2f} ({risky['risk_level']})")
        except httpx.HTTPStatusError as e:
            print(f"   ? Failed to get position metrics: {e.response.text}")
        
        # 8. Batch Operations Demo
        print("\n8. ?? Batch Operations Demo...")
        batch_positions = [
            {
                "position_id": "batch_pos_001",
                "owner_address": "0x4567890123456789012345678901234567890123",
                "collateral_symbol": "ETH",
                "collateral_amount": "8.0",
                "debt_symbol": "USDC",
                "debt_amount": "20000.0"
            },
            {
                "position_id": "batch_pos_002",
                "owner_address": "0x5678901234567890123456789012345678901234",
                "collateral_symbol": "LINK",
                "collateral_amount": "100.0",
                "debt_symbol": "USDC",
                "debt_amount": "1500.0"
            }
        ]
        
        try:
            batch_result = await client.create_batch_positions(batch_positions)
            print(f"   ? Batch created: {batch_result['created_count']} positions")
            if batch_result['error_count'] > 0:
                print(f"   ??  Errors: {batch_result['error_count']} positions failed")
        except httpx.HTTPStatusError as e:
            print(f"   ? Batch operation failed: {e.response.text}")
        
        print("\n?? Demo completed successfully!")
        print("\n?? Next Steps:")
        print("   - Visit http://localhost:8000/docs for interactive API documentation")
        print("   - Check http://localhost:8000/redoc for detailed API reference")
        print("   - Explore the metrics endpoints for monitoring")
        print("   - Try the batch operations for efficient bulk processing")
        
    except Exception as e:
        print(f"\n? Demo failed with error: {e}")
        print("   Make sure the API server is running on http://localhost:8000")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_demo())
