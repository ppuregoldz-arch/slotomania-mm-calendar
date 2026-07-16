#!/usr/bin/env python3
"""
Extract SQL queries from Tableau workbook (.twbx file)
Searches for specific query names: "Simulation" and "progression"
"""

import zipfile
import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path

def extract_queries_from_twbx(twbx_path, query_names):
    """
    Extract specified SQL queries from a Tableau workbook (.twbx file)
    
    Args:
        twbx_path: Path to the .twbx file
        query_names: List of query names to search for (case-insensitive)
    
    Returns:
        Dict mapping query names to SQL content
    """
    queries_found = {}
    
    try:
        # Open the .twbx file (it's a zip archive)
        with zipfile.ZipFile(twbx_path, 'r') as zip_file:
            
            # Look for .twb files inside the archive
            twb_files = [f for f in zip_file.namelist() if f.endswith('.twb')]
            
            if not twb_files:
                print("No .twb files found in the workbook")
                return queries_found
            
            # Process each .twb file (usually just one)
            for twb_file in twb_files:
                print(f"Processing {twb_file}...")
                
                # Extract and parse the XML content
                with zip_file.open(twb_file) as xml_file:
                    content = xml_file.read().decode('utf-8')
                    
                    # Parse XML
                    root = ET.fromstring(content)
                    
                    # Search for datasources and their custom SQL
                    for datasource in root.findall('.//datasource'):
                        datasource_name = datasource.get('name', 'Unknown')
                        
                        # Look for custom SQL in connection elements
                        for connection in datasource.findall('.//connection'):
                            
                            # Check for custom SQL in relation elements
                            for relation in connection.findall('.//relation'):
                                if relation.get('type') == 'text':
                                    sql_text = relation.text
                                    if sql_text:
                                        # Check if this matches any of our target query names
                                        for target_name in query_names:
                                            if target_name.lower() in datasource_name.lower():
                                                queries_found[target_name] = {
                                                    'datasource_name': datasource_name,
                                                    'sql': sql_text.strip()
                                                }
                                                print(f"Found query '{target_name}' in datasource '{datasource_name}'")
                            
                            # Also check for named-connection custom SQL
                            for named_connection in connection.findall('.//named-connection'):
                                conn_name = named_connection.get('name', '')
                                
                                for relation in named_connection.findall('.//relation'):
                                    if relation.get('type') == 'text':
                                        sql_text = relation.text
                                        if sql_text:
                                            # Check if this matches any of our target query names
                                            for target_name in query_names:
                                                if (target_name.lower() in conn_name.lower() or 
                                                    target_name.lower() in datasource_name.lower()):
                                                    queries_found[target_name] = {
                                                        'datasource_name': f"{datasource_name} ({conn_name})",
                                                        'sql': sql_text.strip()
                                                    }
                                                    print(f"Found query '{target_name}' in connection '{conn_name}'")
                    
                    # Also search in worksheets for custom SQL
                    for worksheet in root.findall('.//worksheet'):
                        ws_name = worksheet.get('name', 'Unknown')
                        
                        # Look for datasource references and custom SQL
                        for ds_ref in worksheet.findall('.//datasource-dependencies'):
                            datasource_name = ds_ref.get('datasource', 'Unknown')
                            
                            # Check if worksheet name matches our targets
                            for target_name in query_names:
                                if target_name.lower() in ws_name.lower():
                                    # Try to find associated SQL in the datasource
                                    print(f"Found worksheet '{ws_name}' matching '{target_name}', checking for SQL...")
    
    except Exception as e:
        print(f"Error extracting queries: {str(e)}")
    
    return queries_found

def main():
    # Path to the Tableau workbook
    twbx_path = r"C:\Users\mayed\Downloads\Clan Xhunt 06.05 (7).twbx"
    
    # Target query names
    target_queries = ["Simulation", "progression"]
    
    print(f"Extracting queries from: {twbx_path}")
    print(f"Looking for queries: {target_queries}")
    print("-" * 50)
    
    # Check if file exists
    if not os.path.exists(twbx_path):
        print(f"File not found: {twbx_path}")
        return
    
    # Extract the queries
    queries = extract_queries_from_twbx(twbx_path, target_queries)
    
    print("\n" + "=" * 50)
    print("EXTRACTION RESULTS")
    print("=" * 50)
    
    if queries:
        for query_name, query_info in queries.items():
            print(f"\nQuery Name: {query_name}")
            print(f"Datasource: {query_info['datasource_name']}")
            print("-" * 30)
            print("SQL Query:")
            print(query_info['sql'])
            print("\n" + "=" * 50)
    else:
        print("No matching queries found.")
        print("\nTrying broader search...")
        
        # If no exact matches, let's see all datasources
        try:
            with zipfile.ZipFile(twbx_path, 'r') as zip_file:
                twb_files = [f for f in zip_file.namelist() if f.endswith('.twb')]
                
                for twb_file in twb_files:
                    with zip_file.open(twb_file) as xml_file:
                        content = xml_file.read().decode('utf-8')
                        root = ET.fromstring(content)
                        
                        print("\nAll datasources found:")
                        for datasource in root.findall('.//datasource'):
                            ds_name = datasource.get('name', 'Unknown')
                            print(f"  - {ds_name}")
                        
                        print("\nAll worksheets found:")
                        for worksheet in root.findall('.//worksheet'):
                            ws_name = worksheet.get('name', 'Unknown')
                            print(f"  - {ws_name}")
        
        except Exception as e:
            print(f"Error during broader search: {str(e)}")

if __name__ == "__main__":
    main()