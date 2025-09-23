import pytest
import sys
from pathlib import Path
import requests
import pandas as pd
# Add backend directory to path (simple one-liner)
sys.path.append(str(Path(__file__).parents[3]))

from MCP.server import extract_features_from_question
# from tool.retrieve_data_from_google_sheet import fetch_google_sheet  # We'll use our own function


class TestExtractFeaturesFromQuestion:
    """Test cases for extract_features_from_question tool"""

    def test_extract_features_from_question(self, query):
        prompt_type = "extract_features_question_about_job"
        result = extract_features_from_question(query, prompt_type)
        print(result)
        return result

def write_results_to_google_sheet(rows):
    """
    Ghi kết quả test vào Google Sheet
    Args:
        rows: list of dict chứa các kết quả test với keys 'predict' và 'status'
    """
    WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwRjKyCJrEGD8r12W3ljS8VBg5zm_vL0JWs6Bi6Ff82SV79NXHuRN7TXUhDcrWIjVqq/exec"
    
    payload = {
        "rows": rows,
        "predictCol": 5,  # tùy chọn, có thể bỏ để dùng mặc định
        "startRow": 2     # tùy chọn, có thể bỏ để dùng mặc định
    }
    
    try:
        response = requests.post(WEB_APP_URL, json=payload)
        print(f"✅ Results written to Google Sheet: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error writing to Google Sheet: {e}")
        return False

def fetch_google_sheet_data(url):
    """
    Fetch complete data from Google Sheet
    Args:
        url: Google Sheet TSV URL
    Returns:
        DataFrame: Complete sheet data
    """
    try:
        df = pd.read_csv(url, sep="\t", encoding="utf-8")
        return df
    except Exception as e:
        print(f"Error fetching Google Sheet: {e}")
        return pd.DataFrame()
        
if __name__ == "__main__":
    # pytest.main([__file__, "-s"])
    
    # URL for Google Sheet
    SHEET_URL = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vTCE5n_v7BO2vL5G5VNLtek4K29UldZq45ChVFoTKgAFd1SD0pfFajWu2vL615V-R3g-HS5d2Lefn_l/"
        "pub?gid=1388742879&single=true&output=tsv"
    )
    
    # Fetch the full sheet data
    df_full = fetch_google_sheet_data(SHEET_URL)
    
    if df_full.empty:
        print("❌ Failed to fetch data from Google Sheet")
        exit(1)
    
    # Extract test questions (first column) and expected results (second column)
    test_questions = df_full.iloc[:, 0].dropna()  # First column: questions
    expected_results = df_full.iloc[:, 1].dropna()  # Second column: expected results
    
    # Create test instance
    test_instance = TestExtractFeaturesFromQuestion()
    
    # Run tests and collect results
    print("🧪 Running tests...")
    passed_tests = 0
    total_tests = min(len(test_questions), len(expected_results))
    test_results = []
    
    for i in range(total_tests):
        question = test_questions.iloc[i]
        expected = expected_results.iloc[i] if i < len(expected_results) else None
        
        print(f"\n--- Test {i+1} ---")
        print(f"Question: {question}")
        print(f"Expected: {expected}")
        
        try:
            # Get prediction from your function
            result_dict = test_instance.test_extract_features_from_question(question)
            

            
            # Add result to list for Google Sheets
            test_results.append({
                "predict": result_dict,
            })
          
        except Exception as e:
            print(f"❌ ERROR: {e}")
      
    print(f"\n📊 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    # Write results to Google Sheet
    if test_results:
        print("\n📝 Writing results to Google Sheet...")
        success = write_results_to_google_sheet(test_results)
        if success:
            print("✅ Test results successfully written to Google Sheet!")
        else:
            print("❌ Failed to write results to Google Sheet")
            # Print results locally as backup
            print("\n📋 Test Results (backup):")
            for i, result in enumerate(test_results, 1):
                print(f"Test {i}: {result}")
    else:
        print("❌ No test results to write to Google Sheet")

