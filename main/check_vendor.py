from mac_vendor_lookup import MacLookup

def get_vendor(mac_address):
    # Initialize the MacLookup object
    mac_lookup = MacLookup()
    vendor = ""
    # Get vendor information
    try:
        vendor = mac_lookup.lookup(mac_address)
        print (vendor)
        return vendor
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'anonymous'

    



