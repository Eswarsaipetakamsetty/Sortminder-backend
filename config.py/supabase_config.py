from supabase import create_client
import os


SUPABASE_URL = "https://gtyjozzqkslmsutwzats.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd0eWpvenpxa3NsbXN1dHd6YXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzNzc1NjksImV4cCI6MjA0ODk1MzU2OX0.syxZYygbcQ5cBm2AUXUDaz6OPrTSbNpzO0tNcuHI7Ik"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)