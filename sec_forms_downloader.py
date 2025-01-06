import os
import requests
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

class SECFormsDownloader:
    """Class to handle SEC S-1 form downloads from SEC EDGAR database."""
    
    def __init__(self):
        self.api_key = os.getenv("SEC_API")
        self.base_url = "https://api.sec-api.io/form-s1-424b4"
        
        if not self.api_key:
            raise ValueError("SEC_API environment variable not set")

    def create_query(self, year: int) -> Dict[str, Any]:
        """
        Create a query for S-1 forms from specified year.
        
        Args:
            year: The year to search for forms
            
        Returns:
            Dict containing the query parameters
        """
        return {
            "query": f"formType:\"S-1\" AND filedAt:[{year}-01-01 TO {year}-12-31]",
            "from": "0",
            "size": "5",
            "sort": [{"filedAt": {"order": "desc"}}]
        }

    def fetch_forms(self, year: int) -> List[Dict[str, Any]]:
        """
        Fetch S-1 forms from the SEC API.
        
        Args:
            year: Year to fetch forms from
            
        Returns:
            List of form data dictionaries
        """
        try:
            headers = {"Authorization": self.api_key}
            query = self.create_query(year)
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=query
            )
            response.raise_for_status()
            
            return response.json()["data"]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forms: {str(e)}")
            return []

    def save_forms(self, forms: List[Dict[str, Any]], output_dir: str = "sec_forms"):
        """
        Save form data to JSON files.
        
        Args:
            forms: List of form data to save
            output_dir: Directory to save files in
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for form in forms:
            filename = f"{output_dir}/S1_{form['accessionNo']}.json"
            with open(filename, 'w') as f:
                json.dump(form, f, indent=2)
            print(f"Saved form to {filename}")

def main():
    """Main function to download SEC forms."""
    try:
        # Initialize downloader
        downloader = SECFormsDownloader()
        
        # Get last year
        last_year = datetime.now().year - 1
        
        # Fetch forms
        print(f"Fetching 5 latest S-1 forms from {last_year}...")
        forms = downloader.fetch_forms(last_year)
        
        if forms:
            print(f"Found {len(forms)} forms")
            
            # Save forms
            downloader.save_forms(forms)
            
            # Print summary
            print("\nDownloaded forms summary:")
            for form in forms:
                print(f"- {form['entityName']} ({form['filedAt']})")
        else:
            print("No forms found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()