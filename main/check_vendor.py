from mac_vendor_lookup import MacLookup

def get_vendor(mac_address):
    # Initialize the MacLookup object
    mac_lookup = MacLookup()
    
    # Get vendor information
    try:
        vendor = mac_lookup.lookup(mac_address)
        print (vendor)
    except Exception as e:
        print(f"Error: {str(e)}")

