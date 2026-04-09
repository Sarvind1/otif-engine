"""
Data Fetcher Module for OTIF Stage Calculation Engine
=====================================================

This module extracts and consolidates data from multiple sources into a unified dataframe.
No business logic or calculations are performed - pure data extraction and mapping only.
"""

import pandas as pd
import numpy as np


def fetch_all_data(dfs_tables, dfs_excels, debug=False):
    """
    Main entry point for data fetching.
    Extracts and consolidates all necessary data from dfs_tables and dfs_excels.
    
    Args:
        dfs_tables (dict): Dictionary containing database table dataframes
        dfs_excels (dict): Dictionary containing excel file dataframes
        debug (bool): Enable debug mode for detailed logging
        
    Returns:
        pd.DataFrame: Consolidated dataframe with all mapped data
    """
    
    if debug:
        print("\n[DEBUG] Starting data fetching process...")
        print(f"[DEBUG] Available tables: {list(dfs_tables.keys())}")
        print(f"[DEBUG] Available excels: {list(dfs_excels.keys())}")
    
    # Extract all dataframes from dfs_tables
    po_data = dfs_tables.get('po_data', pd.DataFrame())
    pl_data = dfs_tables.get('pl_data', pd.DataFrame())
    batch_data = dfs_tables.get('batch_data', pd.DataFrame())
    inb_data = dfs_tables.get('inb_data', pd.DataFrame())
    telex_tableau = dfs_tables.get('telex_tableau', pd.DataFrame())
    pi_data = dfs_tables.get('pi_data', pd.DataFrame())
    pi_ns_data = dfs_tables.get('pi_ns_data', pd.DataFrame())
    supplier_confirmation = dfs_tables.get('supplier_confirmation', pd.DataFrame())
    master_data = dfs_tables.get('master_data', pd.DataFrame())
    comp = dfs_tables.get('compliance_hubspot', pd.DataFrame())
    hs_codes_data = dfs_tables.get('hs_codes_data', pd.DataFrame())
    
    # Extract all dataframes from dfs_excels
    memo_mapping = dfs_excels.get('memo_mapping', pd.DataFrame())
    status_mapping = dfs_excels.get('status_mapping', pd.DataFrame())
    blockers_mapping = dfs_excels.get('blockers_mapping', pd.DataFrame())
    cm_sm_vendor_mapping = dfs_excels.get('cm_sm_vendor_mapping', pd.DataFrame())
    asin_priority_mapping = dfs_excels.get('asin_priority_mapping', pd.DataFrame())
    payment_terms_mapping = dfs_excels.get('payment_terms_mapping', pd.DataFrame())
    team_priority_mapping = dfs_excels.get('team_priority_mapping', pd.DataFrame())
    asin_static_payment_status = dfs_excels.get('asin_static_payment_status', pd.DataFrame())
    ffw_status = dfs_excels.get('ffw_status', pd.DataFrame())
    fob_date = dfs_excels.get('fob_date', pd.DataFrame())
    spd_blockers = dfs_excels.get('spd_blockers', pd.DataFrame())
    ffw_blockers = dfs_excels.get('ffw_blockers', pd.DataFrame())
    telex_supplier = dfs_excels.get('telex_supplier', pd.DataFrame())
    telex_ffw = dfs_excels.get('telex_ffw', pd.DataFrame())
    payrun = dfs_excels.get('payrun', pd.DataFrame())
    packaging_data = dfs_excels.get('packaging_data', pd.DataFrame())
    transparency_data = dfs_excels.get('transparency_data', pd.DataFrame())
    transparency_master = dfs_excels.get('transparency_master', pd.DataFrame())
    prepayment = dfs_excels.get('prepayment', pd.DataFrame())
    prd = dfs_excels.get('prd', pd.DataFrame())
    cprd = dfs_excels.get('cprd', pd.DataFrame())
    g2 = dfs_excels.get('g2', pd.DataFrame())
    g4 = dfs_excels.get('g4', pd.DataFrame())
    qc = dfs_excels.get('qc', pd.DataFrame())
    compliance = dfs_excels.get('compliance', pd.DataFrame())
    booking_form_data = dfs_excels.get('booking_form_data', pd.DataFrame())
    
    if debug:
        print(f"\n[DEBUG] Base PO data shape: {po_data.shape}")
        if not po_data.empty:
            print(f"[DEBUG] PO data columns: {list(po_data.columns[:10])}...")  # First 10 columns
    
    # Start with po_data as base - make a copy to avoid modifying original
    final_df = po_data.copy()
    
    if debug:
        print("\n[DEBUG] Starting data mapping process...")
    
    # Standardize null values in base dataframe
    final_df["document_number"] = final_df["document_number"].fillna("")
    final_df["asin"] = final_df["asin"].fillna("")
    final_df["item"] = final_df["item"].fillna("")
    
    # Create key columns for mapping
    final_df["po_razin"] = final_df["document_number"].astype(str) + final_df["item"].astype(str)
    final_df["po_razin_id"] = final_df["document_number"].astype(str) + final_df["item"].astype(str) + final_df["line_id"].astype(str)
    final_df["razin_mp"] = final_df["item"].astype(str) + final_df["marketplace_header"].astype(str)
    final_df["asin_mp"] = final_df["asin"].astype(str) + final_df["marketplace_header"].astype(str)
    
    # Extract Vendor ID
    final_df['Vendor ID'] = final_df['po_vendor'].str.split(" ").str[0]
    
    if debug:
        print("[DEBUG] Created key columns: po_razin, po_razin_id, razin_mp, asin_mp, Vendor ID")
    
    # Map data from various sources
    # 1. Memo mapping
    if not memo_mapping.empty:
        final_df['Placement Batch'] = final_df['scm_po_scm_memo'].map(
            memo_mapping.set_index("Memo (Main)")["Summary Filter"]
        ).fillna("Other")
        if debug:
            print(f"[DEBUG] Mapped Placement Batch from memo_mapping")
    
    # 2. Supplier confirmation check
    if not supplier_confirmation.empty:
        final_df['Supplier Confirmation VP Check'] = final_df['document_number'].apply(
            lambda x: 'Available on VP' if x in supplier_confirmation['po_number'].values else 'Not Available on VP'
        )
        if debug:
            print(f"[DEBUG] Mapped Supplier Confirmation VP Check")
    
    # 3. PI Status mappings
    if not pi_ns_data.empty or not asin_static_payment_status.empty:
        # Merge PI status data
        merged_pi = pd.concat([
            asin_static_payment_status[['Static PO List', 'Status']].rename(
                columns={'Static PO List': 'document_number', 'Status': 'status'}
            ),
            pi_ns_data[['po_number', 'status']].rename(
                columns={'po_number': 'document_number'}
            )
        ], ignore_index=True).drop_duplicates(subset='document_number', keep='first')
        
        final_df['NS PI Status'] = final_df['document_number'].map(
            merged_pi.set_index("document_number")["status"]
        ).fillna("Not Submitted")
        if debug:
            print(f"[DEBUG] Mapped NS PI Status")
    
    if not pi_data.empty:
        final_df['VP PI Status'] = final_df['document_number'].map(
            pi_data[["PO#", "status"]].drop_duplicates(subset="PO#", keep="first").set_index("PO#")["status"]
        ).fillna("03. PI Upload Pending")
        if debug:
            print(f"[DEBUG] Mapped VP PI Status")
    
    # 4. Payment status from payrun
    if not payrun.empty:
        final_df["PI Payment Status"] = final_df['document_number'].map(
            payrun[['PO No.', 'Status']].rename(
                columns={'PO No.': 'document_number'}
            ).drop_duplicates(subset='document_number', keep='first').set_index("document_number")["Status"]
        ).fillna("Not In Payment Sheet")
        if debug:
            print(f"[DEBUG] Mapped PI Payment Status")
    
    # 5. INB mapping
    if not inb_data.empty:
        final_df['INB#'] = final_df['po_razin_id'].map(
            inb_data[['PO&RAZIN&ID', 'shipment_number']].drop_duplicates(
                subset="PO&RAZIN&ID", keep="first"
            ).set_index('PO&RAZIN&ID')['shipment_number']
        ).fillna("")
        
        # Map other INB fields
        inb_fields = {
            'Status': 'status',
            'Actual Pickup': 'actual_cargo_pick_up_date',
            'Actual Shipping Date3': 'actual_shipping_date',
            'Actual Arrival Date': 'actual_arrival_date',
            'Actual Delivery Date': 'actual_delivery_date',
            'Expected Arrival Date': 'expected_arrival_date',
            'Substatus': 'substatus',
            'Shipment Method': 'shipment_method'
        }
        
        for new_col, source_col in inb_fields.items():
            final_df[new_col] = final_df['po_razin_id'].map(
                inb_data[['PO&RAZIN&ID', source_col]].drop_duplicates(
                    subset="PO&RAZIN&ID", keep="first"
                ).set_index('PO&RAZIN&ID')[source_col]
            ).fillna("")
            
        if debug:
            print(f"[DEBUG] Mapped INB# and related fields")
    
    # 6. HS Code mapping
    if not hs_codes_data.empty:
        final_df["HS Code"] = final_df["razin_mp"].map(
            hs_codes_data[["RAZINxMP", "HS Code Status"]].drop_duplicates(
                subset="RAZINxMP", keep="first"
            ).set_index('RAZINxMP')['HS Code Status']
        ).fillna("HS Code Missing")
        if debug:
            print(f"[DEBUG] Mapped HS Code")
    
    # 7. Batch data mappings
    if not batch_data.empty:
        batch_fields = {
            'Actual pick-up date': 'actual_pickup_date',
            'Gate In Date': 'gate_in_date',
            'Actual Shipping Date': 'actual_shipping_date',
            'FOB Date': 'cfs_cut_off',
            'Incoterms2': 'incoterms',
            'SPD': 'scr_date',
            'SPD Delay Reason': 'scrd_delay_reasons'
        }
        
        for new_col, source_col in batch_fields.items():
            final_df[new_col] = final_df['batch_id'].map(
                batch_data.set_index("batch_id")[source_col]
            ).fillna("")
            
        if debug:
            print(f"[DEBUG] Mapped batch data fields")
    
    # 8. PL data mapping
    if not pl_data.empty:
        final_df["Batch Sign-Off"] = final_df["batch_id"].map(
            pl_data.drop_duplicates(subset="batch_id", keep="first").set_index("batch_id")["final_status"]
        ).fillna("14a. Documents Missing")
        if debug:
            print(f"[DEBUG] Mapped Batch Sign-Off")
    
    # 9. CM/SM mapping
    if not cm_sm_vendor_mapping.empty:
        final_df['Vendor ID'] = pd.to_numeric(final_df['Vendor ID'], errors='coerce').astype('Int64')
        cm_sm_vendor_mapping['Vendor ID'] = pd.to_numeric(cm_sm_vendor_mapping['Vendor ID'], errors='coerce').astype('Int64')
        
        vendor_cols = ['CM', 'SM', 'Team']
        for col in vendor_cols:
            if col in cm_sm_vendor_mapping.columns:
                final_df[col] = final_df['Vendor ID'].map(
                    cm_sm_vendor_mapping[['Vendor ID', col]].drop_duplicates(
                        subset="Vendor ID", keep="first"
                    ).set_index('Vendor ID')[col]
                ).fillna("")
        if debug:
            print(f"[DEBUG] Mapped CM, SM, Team")
    
    # 10. Compliance status
    if not comp.empty:
        final_df["razin_mp_vendor"] = final_df["item"].astype(str).str.upper() + final_df["marketplace_header"].astype(str) + final_df["Vendor ID"].astype(str)
        comp["RAZIN&MP&Vendor"] = comp["RAZIN&MP&Vendor"].str.strip()
        comp["compliance_status"] = comp["compliance_status"].str.strip()
        comp = comp[(comp["compliance_status"] != "") & (pd.notna(comp["compliance_status"]))]
        
        final_df['Compliance Status'] = final_df['razin_mp_vendor'].map(
            comp[["RAZIN&MP&Vendor", "compliance_status"]].drop_duplicates(
                subset="RAZIN&MP&Vendor", keep="first"
            ).set_index('RAZIN&MP&Vendor')['compliance_status']
        ).fillna("Missing")
        if debug:
            print(f"[DEBUG] Mapped Compliance Status")
    
    # 11. Additional excel mappings
    excel_mappings = {
        'Transparency Check': (transparency_master, 'asin', 'ASIN', 'Transparency Check', 'No'),
        'Transparency Pending': (transparency_data, 'po_razin', 'PO&RAZIN', 'Transparency Pending', 'Missing'),
        'OTIF Focus': (asin_priority_mapping, 'asin_mp', 'ASINxMP', 'OTIF Focus', 'Low'),
        'MD Blocker': (master_data, 'razin_mp', 'razin_mp', 'Action', 'No Blocker'),
        'L2 SPD': (spd_blockers, 'batch_id', 'batch_id', 'Final Status', 'Not in SPD Sheet'),
        'L2 Compliance': (compliance, 'po_razin_id', 'PO&RAZIN&ID', 'Final Status', 'Not in Compliance Sheet'),
        'L2 PI': (prepayment, 'document_number', 'document number', 'Final Status', 'Not in PI Sheet'),
        'L2 PRD': (prd, 'po_razin_id', 'otif_id', 'Final Status', 'Not in PRD Sheet'),
        'L2 CPRD': (cprd, 'po_razin_id', 'po_razin_id', 'Final Status', 'Not in CPRD Sheet'),
        'L2 G2': (g2, 'po_razin_id', 'otif_id', 'Final Status', 'Not in G2 Sheet'),
        'L2 G4': (g4, 'batch_id', 'batch_id', 'Final Status', 'Not in G4 Sheet'),
        'L2 Pickup': (ffw_status, 'batch_id', 'Batch ID', 'Final Blocker Reason', 'Not in FFW Sheet')
    }
    
    for target_col, (source_df, map_key, source_key, source_col, default_val) in excel_mappings.items():
        if not source_df.empty and source_key in source_df.columns and source_col in source_df.columns:
            final_df[target_col] = final_df[map_key].map(
                source_df[[source_key, source_col]].drop_duplicates(
                    subset=source_key, keep="first"
                ).set_index(source_key)[source_col]
            ).fillna(default_val)
            if debug:
                print(f"[DEBUG] Mapped {target_col}")
    
    # 12. QC mapping with special handling
    if not qc.empty and 'PO RAZIN ID' in qc.columns and 'Final Status2' in qc.columns:
        final_df['L2 QC'] = final_df['po_razin_id'].map(
            qc[["PO RAZIN ID", "Final Status2"]].drop_duplicates(
                subset="PO RAZIN ID", keep="first"
            ).set_index('PO RAZIN ID')['Final Status2']
        ).fillna("Not in QC Sheet")
        if debug:
            print(f"[DEBUG] Mapped L2 QC")
    
    # 13. Payment and invoice number mappings
    if not payrun.empty and 'Inv#' in payrun.columns:
        final_df['Line Payment Approval Status_map'] = final_df['invoice_number'].map(
            payrun[['Inv#', 'Status']].drop_duplicates(
                subset='Inv#', keep='first'
            ).set_index("Inv#")["Status"]
        )
        if debug:
            print(f"[DEBUG] Mapped Line Payment Approval Status")
    
    # 14. Booking form status
    if not booking_form_data.empty and 'Batch Id' in booking_form_data.columns:
        final_df['Booking Form Status_map'] = final_df['batch_id'].map(
            booking_form_data[['Batch Id', 'Status']].drop_duplicates(
                subset='Batch Id', keep='first'
            ).set_index('Batch Id')['Status']
        )
        if debug:
            print(f"[DEBUG] Mapped Booking Form Status")
    
    # 15. VP Booking Status
    if not batch_data.empty and 'Booking Status' in batch_data.columns:
        final_df['VP Booking Status_map'] = final_df['batch_id'].map(
            batch_data[['batch_id', 'Booking Status']].drop_duplicates(
                subset='batch_id', keep='first'
            ).set_index('batch_id')['Booking Status']
        )
        if debug:
            print(f"[DEBUG] Mapped VP Booking Status")
    
    # 16. Telex mappings
    if not telex_tableau.empty:
        telex_fields = {
            'Tableau (Supplier)': 'Final Status (Supplier)',
            'Tableau (FFW)': 'Final Status (FFW)',
            'Batch Status': 'Batch Status'
        }
        
        for target_col, source_col in telex_fields.items():
            if source_col in telex_tableau.columns:
                if target_col == 'Batch Status':
                    final_df[f'Telex {target_col}'] = final_df['batch_id'].map(
                        telex_tableau[["batch_id", source_col]].drop_duplicates(
                            subset="batch_id", keep="first"
                        ).set_index('batch_id')[source_col]
                    )
                else:
                    final_df[f'Telex {target_col}'] = final_df['INB#'].map(
                        telex_tableau[['shipment_number', source_col]].drop_duplicates(
                            subset="shipment_number", keep="first"
                        ).set_index('shipment_number')[source_col]
                    ).fillna("Not Released")
        if debug:
            print(f"[DEBUG] Mapped Telex data")
    
    # 17. Additional telex supplier/ffw mappings
    if not telex_supplier.empty:
        final_df['Joey Status'] = final_df['INB#'].map(
            telex_supplier[['shipment number', 'Final Status']].drop_duplicates(
                subset="shipment number", keep="first"
            ).set_index('shipment number')['Final Status']
        ).fillna("Not Released")
        
        final_df['Telex Supplier Action'] = final_df['batch_id'].map(
            telex_supplier[["batch_id", "Final Action"]].drop_duplicates(
                subset="batch_id", keep="first"
            ).set_index("batch_id")["Final Action"]
        ).fillna("Not in Telex Sheet")
        if debug:
            print(f"[DEBUG] Mapped Telex Supplier data")
    
    if not telex_ffw.empty:
        final_df['Muazam Status'] = final_df['INB#'].map(
            telex_ffw[['Shipment Number', 'Final Status']].drop_duplicates(
                subset="Shipment Number", keep="first"
            ).set_index('Shipment Number')['Final Status']
        ).fillna("Not Released")
        
        final_df['Telex FFW Blocker'] = final_df['INB#'].map(
            telex_ffw[["Shipment Number", "Final Blocker Status"]].drop_duplicates(
                subset="Shipment Number", keep="first"
            ).set_index("Shipment Number")["Final Blocker Status"]
        ).fillna("Not in FFW Telex Sheet")
        if debug:
            print(f"[DEBUG] Mapped Telex FFW data")
    
    # 18. Packaging mapping
    if not packaging_data.empty and 'PORAZIN' in packaging_data.columns:
        final_df['Packaging Status'] = final_df['po_razin'].map(
            packaging_data.drop_duplicates(subset='PORAZIN', keep="first").set_index('PORAZIN')['Final Status']
        ).fillna("Yes")
        
        final_df['Packaging Standard Status'] = final_df['po_razin'].map(
            packaging_data[['PORAZIN', 'Packaging Standard Status']].drop_duplicates(
                subset='PORAZIN', keep="first"
            ).set_index('PORAZIN')['Packaging Standard Status']
        )
        if debug:
            print(f"[DEBUG] Mapped Packaging data")
    
    # 19. FOB and FFW blockers
    if not fob_date.empty and 'BATCH ID' in fob_date.columns:
        final_df["FOB Status"] = final_df["batch_id"].map(
            fob_date[['BATCH ID', 'Pickup Status']].drop_duplicates(
                subset="BATCH ID", keep="first"
            ).set_index("BATCH ID")["Pickup Status"]
        ).fillna("")
        if debug:
            print(f"[DEBUG] Mapped FOB Status")
    
    if not ffw_blockers.empty and "Batch ID" in ffw_blockers.columns:
        final_df['FFW Blocker Status'] = final_df['batch_id'].map(
            ffw_blockers.drop_duplicates(subset="Batch ID", keep="first").set_index("Batch ID")["Final Status"]
        ).fillna("No")
        if debug:
            print(f"[DEBUG] Mapped FFW Blocker Status")
    
    # 20. Status and Reporting mappings
    if not status_mapping.empty:
        # Store status mapping for later use
        final_df['status_mapping_available'] = True
        if debug:
            print(f"[DEBUG] Status mapping available for downstream processing")
    
    # 21. Blockers mapping
    if not blockers_mapping.empty:
        # Store for later use
        final_df['blockers_mapping_available'] = True
        if debug:
            print(f"[DEBUG] Blockers mapping available for downstream processing")
    
    # Standardize empty values
    final_df = final_df.replace(["None", "none", "NaN", "nan", "null", "Null"], "")
    final_df = final_df.fillna("")
    
    if debug:
        print(f"\n[DEBUG] Final dataframe shape: {final_df.shape}")
        print(f"[DEBUG] Total columns added: {len(final_df.columns) - len(po_data.columns)}")
        print("[DEBUG] Data fetching complete!")
    
    return final_df, {
        'status_mapping': status_mapping,
        'blockers_mapping': blockers_mapping,
        'payment_terms_mapping': payment_terms_mapping,
        'asin_priority_mapping': asin_priority_mapping,
        'team_priority_mapping': team_priority_mapping
    }


if __name__ == "__main__":
    # Test the module
    print("Data Fetcher Module - Ready for use")
    print("Usage: final_df, mappings = fetch_all_data(dfs_tables, dfs_excels, debug=True)")
