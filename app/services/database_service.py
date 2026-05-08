import os
from datetime import datetime
from typing import Optional, List
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from bson import ObjectId
from app.config import settings
from app.models import SavedQuote, QuoteResponse

class DatabaseService:
    """Service for database operations and quote persistence"""
    
    def __init__(self):
        self.client: Optional[AsyncClient] = None
        self.db: Optional[AsyncDatabase] = None
        self.quotes_collection = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            print(f"🔗 Connecting to MongoDB: {settings.mongodb_url}")
            self.client = AsyncClient(settings.mongodb_url)
            self.db = self.client[settings.mongodb_database]
            self.quotes_collection = self.db["quotes"]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB database: {settings.mongodb_database}")
            
            # Create indexes
            await self._create_indexes()
        except Exception as e:
            print(f"❌ MongoDB connection error: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for optimized queries"""
        try:
            await self.quotes_collection.create_index("electricianId")
            await self.quotes_collection.create_index("customerEmail")
            await self.quotes_collection.create_index("status")
            await self.quotes_collection.create_index("createdAt", expireAfterSeconds=7776000)  # 90 days TTL
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Index creation warning: {str(e)}")
    
    async def save_quote(self, quote_data: dict) -> str:
        """
        Save a quote to database
        
        Args:
            quote_data: Quote data dictionary
            
        Returns:
            str: Quote ID (MongoDB _id)
        """
        try:
            # Add timestamps
            quote_data["createdAt"] = datetime.now()
            quote_data["updatedAt"] = datetime.now()
            
            # Insert quote
            result = await self.quotes_collection.insert_one(quote_data)
            quote_id = str(result.inserted_id)
            
            print(f"✅ Quote saved successfully - ID: {quote_id}")
            return quote_id
            
        except Exception as e:
            print(f"❌ Error saving quote: {str(e)}")
            raise
    
    async def get_quote_by_id(self, quote_id: str) -> Optional[QuoteResponse]:
        """
        Retrieve a quote by ID
        
        Args:
            quote_id: MongoDB quote ID
            
        Returns:
            Optional[QuoteResponse]: Quote data or None if not found
        """
        try:
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(quote_id)
            except Exception:
                return None
            
            quote = await self.quotes_collection.find_one({"_id": object_id})
            
            if not quote:
                return None
            
            # Convert MongoDB document to QuoteResponse
            return self._doc_to_response(quote)
            
        except Exception as e:
            print(f"❌ Error retrieving quote: {str(e)}")
            raise
    
    async def get_quotes_by_electrician(self, electrician_id: str) -> List[QuoteResponse]:
        """
        Retrieve all quotes for a specific electrician
        
        Args:
            electrician_id: Electrician ID
            
        Returns:
            List[QuoteResponse]: List of quotes
        """
        try:
            cursor = self.quotes_collection.find({"electricianId": electrician_id})
            quotes = await cursor.to_list(length=1000)
            return [self._doc_to_response(doc) for doc in quotes]
            
        except Exception as e:
            print(f"❌ Error retrieving electrician quotes: {str(e)}")
            raise
    
    async def get_quotes_by_customer_email(self, customer_email: str) -> List[QuoteResponse]:
        """
        Retrieve all quotes for a specific customer
        
        Args:
            customer_email: Customer email address
            
        Returns:
            List[QuoteResponse]: List of quotes
        """
        try:
            cursor = self.quotes_collection.find({"customerEmail": customer_email})
            quotes = await cursor.to_list(length=1000)
            return [self._doc_to_response(doc) for doc in quotes]
            
        except Exception as e:
            print(f"❌ Error retrieving customer quotes: {str(e)}")
            raise
    
    async def get_all_quotes(self, status: Optional[str] = None, limit: int = 100) -> List[QuoteResponse]:
        """
        Retrieve all quotes (optionally filtered by status)
        
        Args:
            status: Optional status filter (pending/accepted/rejected)
            limit: Maximum number of quotes to retrieve
            
        Returns:
            List[QuoteResponse]: List of quotes
        """
        try:
            query = {}
            if status:
                query["status"] = status
            
            cursor = self.quotes_collection.find(query).sort("createdAt", -1).limit(limit)
            quotes = await cursor.to_list(length=limit)
            return [self._doc_to_response(doc) for doc in quotes]
            
        except Exception as e:
            print(f"❌ Error retrieving quotes: {str(e)}")
            raise
    
    async def update_quote_status(
        self, 
        quote_id: str, 
        status: str, 
        notes: Optional[str] = None
    ) -> Optional[QuoteResponse]:
        """
        Update quote status
        
        Args:
            quote_id: MongoDB quote ID
            status: New status (pending/accepted/rejected)
            notes: Optional notes
            
        Returns:
            Optional[QuoteResponse]: Updated quote or None if not found
        """
        try:
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(quote_id)
            except Exception:
                return None
            
            update_data = {
                "status": status,
                "updatedAt": datetime.now()
            }
            
            if notes:
                update_data["notes"] = notes
            
            result = await self.quotes_collection.find_one_and_update(
                {"_id": object_id},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                print(f"✅ Quote {quote_id} status updated to {status}")
                return self._doc_to_response(result)
            
            return None
            
        except Exception as e:
            print(f"❌ Error updating quote status: {str(e)}")
            raise
    
    async def delete_quote(self, quote_id: str) -> bool:
        """
        Delete a quote (soft or hard delete)
        
        Args:
            quote_id: MongoDB quote ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(quote_id)
            except Exception:
                return False
            
            result = await self.quotes_collection.delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                print(f"✅ Quote {quote_id} deleted")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error deleting quote: {str(e)}")
            raise
    
    def _doc_to_response(self, doc: dict) -> QuoteResponse:
        """Convert MongoDB document to QuoteResponse"""
        return QuoteResponse(
            id=str(doc.get("_id", "")),
            electricianId=doc.get("electricianId", ""),
            electricianName=doc.get("electricianName", ""),
            electricianEmail=doc.get("electricianEmail", ""),
            job_description=doc.get("job_description", ""),
            estimatedHours=doc.get("estimatedHours", 0),
            jobComplexity=doc.get("jobComplexity", "moderate"),
            callOutFee=doc.get("callOutFee", 0),
            hourlyRate=doc.get("hourlyRate", 0),
            labourCost=doc.get("labourCost", 0),
            emergencyUplift=doc.get("emergencyUplift"),
            minimumCharge=doc.get("minimumCharge", 0),
            totalQuote=doc.get("totalQuote", 0),
            isEmergency=doc.get("isEmergency", False),
            status=doc.get("status", "pending"),
            createdAt=doc.get("createdAt", datetime.now()),
            updatedAt=doc.get("updatedAt", datetime.now()),
            customerEmail=doc.get("customerEmail"),
            aiReasoning=doc.get("aiReasoning")
        )

# Create singleton instance
database_service = DatabaseService()
