"""Supabase database client for gazetted rates"""
import os
from typing import List, Dict, Optional
import pandas as pd
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from datetime import datetime
import streamlit as st

class SupabaseRatesClient:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set"
            )
        
        self.client: Client = create_client(
            self.supabase_url,
            self.supabase_key,
            options=SyncClientOptions(
                postgrest_client_timeout=20,
                storage_client_timeout=20,
                function_client_timeout=10,
            ),
        )

    def health_check(self) -> bool:
        """Verify connectivity with a lightweight query."""
        try:
            self.client.table("gazetted_rates").select("id").limit(1).execute()
            return True
        except Exception as e:
            raise ConnectionError(f"Supabase health check failed: {str(e)}") from e
    def health_check(self) -> bool:
        """Verify connectivity with a lightweight query."""
        try:
            self.client.table("gazetted_rates").select("id").limit(1).execute()
            return True
        except Exception as e:
            raise ConnectionError(f"Supabase health check failed: {str(e)}") from e
    
    def get_all_years(self) -> List[int]:
        """Get list of all available years in database"""
        try:
            response = self.client.table("gazetted_rates").select("year").execute()
            years = sorted(set(item["year"] for item in response.data))
            return years
        except Exception as e:
            st.error(f"Error fetching years: {str(e)}")
            return []
    
    def get_rates_by_year(self, year: int) -> pd.DataFrame:
        """Fetch all rates for a specific year"""
        try:
            response = self.client.table("gazetted_rates")\
                .select("*")\
                .eq("year", year)\
                .execute()
            
            df = pd.DataFrame(response.data)
            return df
        except Exception as e:
            st.error(f"Error fetching rates for year {year}: {str(e)}")
            return pd.DataFrame()
    
    def get_rate_by_service(
        self, 
        year: int, 
        service_category: str, 
        service_name: str
    ) -> Optional[Dict]:
        """Get specific rate for calculation"""
        try:
            response = self.client.table("gazetted_rates")\
                .select("*")\
                .eq("year", year)\
                .eq("service_category", service_category)\
                .eq("service_name", service_name)\
                .single()\
                .execute()
            
            return response.data
        except Exception as e:
            st.warning(f"Rate not found: {str(e)}")
            return None
    
    def add_rate(
        self,
        year: int,
        rate_type: str,
        service_category: str,
        service_name: str,
        amount: float,
        unit: str = "per service",
        remarks: str = "",
        created_by: str = "admin"
    ) -> bool:
        """Add a new gazetted rate"""
        try:
            response = self.client.table("gazetted_rates").insert({
                "year": year,
                "rate_type": rate_type,
                "service_category": service_category,
                "service_name": service_name,
                "amount": amount,
                "unit": unit,
                "remarks": remarks,
                "created_by": created_by
            }).execute()
            
            return True
        except Exception as e:
            st.error(f"Error adding rate: {str(e)}")
            return False
    
    def update_rate(
        self,
        rate_id: int,
        amount: float,
        remarks: str = "",
        modified_by: str = "admin"
    ) -> bool:
        """Update an existing rate and log the change"""
        try:
            # Get old amount for audit log
            old_data = self.client.table("gazetted_rates")\
                .select("amount")\
                .eq("id", rate_id)\
                .single()\
                .execute()
            
            old_amount = old_data.data["amount"]
            
            # Update the rate
            self.client.table("gazetted_rates")\
                .update({
                    "amount": amount,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", rate_id)\
                .execute()
            
            # Log the change
            self.client.table("rates_audit_log").insert({
                "rate_id": rate_id,
                "old_amount": old_amount,
                "new_amount": amount,
                "modified_by": modified_by,
                "notes": remarks
            }).execute()
            
            return True
        except Exception as e:
            st.error(f"Error updating rate: {str(e)}")
            return False
    
    def bulk_upload_rates(
        self,
        df: pd.DataFrame,
        year: int,
        rate_type: str = "standard",
        created_by: str = "admin"
    ) -> bool:
        """Bulk upload rates from DataFrame"""
        try:
            records = []
            for _, row in df.iterrows():
                records.append({
                    "year": year,
                    "rate_type": rate_type,
                    "service_category": row.get("service_category", ""),
                    "service_name": row.get("service_name", ""),
                    "amount": float(row.get("amount", 0)),
                    "unit": row.get("unit", "per service"),
                    "remarks": row.get("remarks", ""),
                    "created_by": created_by
                })
            
            # Insert in batches to avoid timeout
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                self.client.table("gazetted_rates").insert(batch).execute()
            
            st.success(f"Successfully uploaded {len(records)} rates")
            return True
        except Exception as e:
            st.error(f"Error bulk uploading rates: {str(e)}")
            return False
    
    def get_audit_history(self, rate_id: int) -> pd.DataFrame:
        """Get audit history for a specific rate"""
        try:
            response = self.client.table("rates_audit_log")\
                .select("*")\
                .eq("rate_id", rate_id)\
                .order("modified_at", desc=True)\
                .execute()
            
            return pd.DataFrame(response.data)
        except Exception as e:
            st.error(f"Error fetching audit history: {str(e)}")
            return pd.DataFrame()
