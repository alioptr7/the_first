#!/usr/bin/env python
"""
Create test ProfileTypes in Response Network
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from core.config import settings
from models.profile_type_config import ProfileTypeConfig


async def create_profile_types():
    """Create test ProfileTypes"""
    
    # Create async engine
    engine = create_async_engine(str(settings.DATABASE_URL))
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Profile Type 1: Sales Representative
            sales_profile = ProfileTypeConfig(
                name="sales",
                display_name="Sales Representative",
                description="User profile for sales representatives with access to customer and product data",
                permissions={
                    "allowed_request_types": ["customer_data", "product_info", "price_inquiry"],
                    "blocked_request_types": [],
                    "max_results_per_request": 500
                },
                daily_request_limit=50,
                monthly_request_limit=1000,
                rate_limit_per_minute=5,
                rate_limit_per_hour=50,
                is_active=True,
                is_builtin=False,
                config_metadata={
                    "category": "business",
                    "tier": "standard"
                }
            )
            
            # Profile Type 2: Developer/Technical User
            developer_profile = ProfileTypeConfig(
                name="developer",
                display_name="Developer",
                description="User profile for developers with full API access",
                permissions={
                    "allowed_request_types": [],  # Empty = allow all
                    "blocked_request_types": [],
                    "max_results_per_request": 5000
                },
                daily_request_limit=500,
                monthly_request_limit=10000,
                rate_limit_per_minute=20,
                rate_limit_per_hour=500,
                is_active=True,
                is_builtin=False,
                config_metadata={
                    "category": "technical",
                    "tier": "premium"
                }
            )
            
            # Check if they already exist
            existing_sales = await session.execute(
                select(ProfileTypeConfig).where(ProfileTypeConfig.name == "sales")
            )
            if existing_sales.scalar_one_or_none():
                print("✅ Sales profile already exists, skipping...")
            else:
                session.add(sales_profile)
                print("✅ Created: Sales Profile")
            
            existing_dev = await session.execute(
                select(ProfileTypeConfig).where(ProfileTypeConfig.name == "developer")
            )
            if existing_dev.scalar_one_or_none():
                print("✅ Developer profile already exists, skipping...")
            else:
                session.add(developer_profile)
                print("✅ Created: Developer Profile")
            
            # Commit changes
            await session.commit()
            
            # Display results
            print("\n" + "="*60)
            print("📊 ProfileTypes in Database:")
            print("="*60)
            
            result = await session.execute(select(ProfileTypeConfig))
            all_profiles = result.scalars().all()
            
            for profile in all_profiles:
                print(f"\n📌 {profile.display_name} (name: {profile.name})")
                print(f"   Description: {profile.description}")
                print(f"   Status: {'🟢 Active' if profile.is_active else '🔴 Inactive'}")
                print(f"   Allowed request types: {profile.get_allowed_request_types() or 'All types allowed'}")
                print(f"   Blocked request types: {profile.get_blocked_request_types() or 'None'}")
                print(f"   Daily limit: {profile.daily_request_limit} requests")
                print(f"   Rate limit: {profile.rate_limit_per_minute}/min, {profile.rate_limit_per_hour}/hour")
            
            print(f"\n✅ Total ProfileTypes: {len(all_profiles)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_profile_types())
