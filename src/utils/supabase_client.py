"""
Supabase Client Utility for EduCraft
Handles database operations for user management and syllabus storage.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv()


class SupabaseManager:
    """Manager for all Supabase database operations."""

    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY in .env file"
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    def get_or_create_user(
        self,
        username: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Dict:
        """
        Get existing user by username or create new one.

        Args:
            username: User's username
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            User dictionary with id, username, names, timestamps
        """
        # Check if user exists
        result = (
            self.client.table("users").select("*").eq("username", username).execute()
        )

        if result.data:
            # User exists - update last_active_at
            user = result.data[0]
            self.client.table("users").update(
                {"last_active_at": datetime.utcnow().isoformat()}
            ).eq("id", user["id"]).execute()
            return user
        else:
            # Create new user
            new_user_data = {"username": username}
            if first_name:
                new_user_data["first_name"] = first_name
            if last_name:
                new_user_data["last_name"] = last_name

            result = self.client.table("users").insert(new_user_data).execute()
            return result.data[0]

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        result = self.client.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        result = self.client.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None

    def get_all_users(self) -> List[Dict]:
        """Get all users (for analytics)."""
        result = (
            self.client.table("users")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    # ========================================================================
    # SYLLABUS MANAGEMENT
    # ========================================================================

    def save_syllabus(
        self,
        user_id: str,
        title: str,
        domain: str,
        level: str,
        description: str,
        syllabus_json: Dict,
        generation_time_seconds: float,
    ) -> Dict:
        """
        Save a generated syllabus to the database.

        Args:
            user_id: UUID of the user who generated this
            title: Course title
            domain: Domain (computer_science, mathematics, physics)
            level: Difficulty level (beginner, intermediate, advanced)
            description: Course description
            syllabus_json: Complete syllabus as dictionary
            generation_time_seconds: Time taken to generate

        Returns:
            Saved syllabus record with ID
        """
        # Extract metadata from syllabus for quick queries
        modules = syllabus_json.get("modules", [])
        activities = syllabus_json.get("activities", [])
        assessments = syllabus_json.get("assessments", [])
        objectives = syllabus_json.get("learning_objectives", [])

        metadata = syllabus_json.get("metadata", {})
        rag_count = metadata.get("rag_retrieved_components", 0)
        generated_count = metadata.get("generated_components", 0)

        syllabus_data = {
            "user_id": user_id,
            "title": title,
            "domain": domain,
            "level": level,
            "description": description,
            "generation_time_seconds": generation_time_seconds,
            "module_count": len(modules),
            "activity_count": len(activities),
            "assessment_count": len(assessments),
            "objective_count": len(objectives),
            "rag_component_count": rag_count,
            "generated_component_count": generated_count,
            "syllabus_json": syllabus_json,
        }

        result = self.client.table("generated_syllabi").insert(syllabus_data).execute()
        return result.data[0]

    def get_user_syllabi(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """
        Get all syllabi generated by a user.

        Args:
            user_id: User's UUID
            limit: Max number of results (default 50)
            offset: Offset for pagination

        Returns:
            List of syllabus records (without full JSON by default)
        """
        result = (
            self.client.table("generated_syllabi")
            .select(
                "id, title, domain, level, generated_at, generation_time_seconds, module_count, activity_count, assessment_count"
            )
            .eq("user_id", user_id)
            .order("generated_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )
        return result.data

    def get_syllabus_by_id(self, syllabus_id: str) -> Optional[Dict]:
        """Get complete syllabus by ID (includes full JSON)."""
        result = (
            self.client.table("generated_syllabi")
            .select("*")
            .eq("id", syllabus_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_all_syllabi(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all syllabi (for analytics)."""
        result = (
            self.client.table("generated_syllabi")
            .select("*")
            .order("generated_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )
        return result.data

    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================

    def get_total_syllabi_count(self) -> int:
        """Get total number of syllabi generated."""
        result = (
            self.client.table("generated_syllabi").select("id", count="exact").execute()
        )
        return result.count

    def get_unique_users_count(self) -> int:
        """Get number of unique users who generated syllabi."""
        result = self.client.table("users").select("id", count="exact").execute()
        return result.count

    def get_domain_distribution(self) -> List[Dict]:
        """Get syllabi count by domain."""
        # Note: Supabase doesn't support GROUP BY directly via Python client
        # Use RPC function or fetch all and process in Python
        result = (
            self.client.table("generated_syllabi")
            .select("domain, generation_time_seconds, module_count")
            .execute()
        )

        # Group by domain in Python
        from collections import defaultdict

        domain_stats = defaultdict(
            lambda: {"count": 0, "total_time": 0, "total_modules": 0}
        )

        for row in result.data:
            domain = row["domain"]
            domain_stats[domain]["count"] += 1
            domain_stats[domain]["total_time"] += row.get("generation_time_seconds", 0)
            domain_stats[domain]["total_modules"] += row.get("module_count", 0)

        # Calculate averages
        stats_list = []
        for domain, stats in domain_stats.items():
            count = stats["count"]
            stats_list.append(
                {
                    "domain": domain,
                    "count": count,
                    "avg_time": round(stats["total_time"] / count, 2)
                    if count > 0
                    else 0,
                    "avg_modules": round(stats["total_modules"] / count, 1)
                    if count > 0
                    else 0,
                }
            )

        return sorted(stats_list, key=lambda x: x["count"], reverse=True)

    def get_user_activity_summary(self, user_id: str) -> Dict:
        """Get activity summary for a specific user."""
        syllabi = self.get_user_syllabi(user_id, limit=1000)

        if not syllabi:
            return {
                "total_syllabi": 0,
                "domains_tested": [],
                "avg_generation_time": 0,
                "first_generation": None,
                "last_generation": None,
            }

        from collections import Counter

        domains = Counter(s["domain"] for s in syllabi)
        times = [
            s.get("generation_time_seconds", 0)
            for s in syllabi
            if s.get("generation_time_seconds")
        ]

        return {
            "total_syllabi": len(syllabi),
            "domains_tested": list(domains.keys()),
            "domain_distribution": dict(domains),
            "avg_generation_time": round(sum(times) / len(times), 2) if times else 0,
            "first_generation": syllabi[-1]["generated_at"] if syllabi else None,
            "last_generation": syllabi[0]["generated_at"] if syllabi else None,
        }


# Singleton instance
_supabase_manager: Optional[SupabaseManager] = None


def get_supabase_manager() -> SupabaseManager:
    """Get or create singleton Supabase manager instance."""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager
