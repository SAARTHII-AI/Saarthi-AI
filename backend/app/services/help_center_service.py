from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

HELP_CENTERS: List[Dict[str, Any]] = [
    {"name": "PM-KISAN Helpline", "state": "All India", "district": "National", "type": "national_helpline", "phone": "155261 / 011-24300606", "address": "Ministry of Agriculture, Krishi Bhawan, New Delhi"},
    {"name": "Ayushman Bharat Helpline", "state": "All India", "district": "National", "type": "national_helpline", "phone": "14555 / 1800-111-565", "address": "National Health Authority, 9th Floor, Tower-L, Jeevan Bharati Building, Connaught Place, New Delhi"},
    {"name": "PM Awas Yojana Helpline", "state": "All India", "district": "National", "type": "national_helpline", "phone": "1800-11-6163", "address": "Ministry of Housing and Urban Affairs, Nirman Bhawan, New Delhi"},
    {"name": "Common Service Centre Helpline", "state": "All India", "district": "National", "type": "national_helpline", "phone": "1800-121-3468", "address": "CSC e-Governance Services India Ltd, Electronics Niketan, New Delhi"},
    {"name": "DigiLocker Helpline", "state": "All India", "district": "National", "type": "national_helpline", "phone": "011-24303714", "address": "National e-Governance Division, Electronics Niketan, New Delhi"},

    {"name": "CSC Lucknow", "state": "Uttar Pradesh", "district": "Lucknow", "type": "CSC", "phone": "0522-2238902", "address": "CSC District Centre, Vikas Bhawan, Lucknow, UP"},
    {"name": "CSC Varanasi", "state": "Uttar Pradesh", "district": "Varanasi", "type": "CSC", "phone": "0542-2501218", "address": "CSC District Centre, Collectorate Compound, Varanasi, UP"},
    {"name": "District Office Prayagraj", "state": "Uttar Pradesh", "district": "Prayagraj", "type": "district_office", "phone": "0532-2504001", "address": "District Collectorate, Civil Lines, Prayagraj, UP"},
    {"name": "CSC Kanpur", "state": "Uttar Pradesh", "district": "Kanpur", "type": "CSC", "phone": "0512-2304567", "address": "CSC District Centre, Collectorate, Kanpur Nagar, UP"},

    {"name": "CSC Mumbai", "state": "Maharashtra", "district": "Mumbai", "type": "CSC", "phone": "022-22632521", "address": "CSC Centre, Old CGO Building, CBD Belapur, Navi Mumbai, Maharashtra"},
    {"name": "CSC Pune", "state": "Maharashtra", "district": "Pune", "type": "CSC", "phone": "020-26123188", "address": "CSC District Centre, Collector Office, Pune, Maharashtra"},
    {"name": "District Office Nagpur", "state": "Maharashtra", "district": "Nagpur", "type": "district_office", "phone": "0712-2562021", "address": "District Collectorate, Civil Lines, Nagpur, Maharashtra"},
    {"name": "CSC Nashik", "state": "Maharashtra", "district": "Nashik", "type": "CSC", "phone": "0253-2575012", "address": "CSC District Centre, Collector Office Compound, Nashik, Maharashtra"},

    {"name": "CSC Chennai", "state": "Tamil Nadu", "district": "Chennai", "type": "CSC", "phone": "044-25671444", "address": "CSC District Centre, Collectorate Complex, Chennai, Tamil Nadu"},
    {"name": "CSC Coimbatore", "state": "Tamil Nadu", "district": "Coimbatore", "type": "CSC", "phone": "0422-2301234", "address": "CSC District Centre, Collector Office, Coimbatore, Tamil Nadu"},
    {"name": "District Office Madurai", "state": "Tamil Nadu", "district": "Madurai", "type": "district_office", "phone": "0452-2531234", "address": "District Collectorate, Madurai, Tamil Nadu"},
    {"name": "CSC Tiruchirappalli", "state": "Tamil Nadu", "district": "Tiruchirappalli", "type": "CSC", "phone": "0431-2411234", "address": "CSC District Centre, Collector Office, Tiruchirappalli, Tamil Nadu"},

    {"name": "CSC Patna", "state": "Bihar", "district": "Patna", "type": "CSC", "phone": "0612-2217734", "address": "CSC District Centre, Collectorate, Patna, Bihar"},
    {"name": "CSC Gaya", "state": "Bihar", "district": "Gaya", "type": "CSC", "phone": "0631-2220025", "address": "CSC District Centre, Collector Office, Gaya, Bihar"},
    {"name": "District Office Muzaffarpur", "state": "Bihar", "district": "Muzaffarpur", "type": "district_office", "phone": "0621-2240100", "address": "District Collectorate, Muzaffarpur, Bihar"},
    {"name": "CSC Bhagalpur", "state": "Bihar", "district": "Bhagalpur", "type": "CSC", "phone": "0641-2401234", "address": "CSC District Centre, Collector Office, Bhagalpur, Bihar"},

    {"name": "CSC Jaipur", "state": "Rajasthan", "district": "Jaipur", "type": "CSC", "phone": "0141-2227908", "address": "CSC District Centre, Collectorate, Jaipur, Rajasthan"},
    {"name": "CSC Jodhpur", "state": "Rajasthan", "district": "Jodhpur", "type": "CSC", "phone": "0291-2544200", "address": "CSC District Centre, Collector Office, Jodhpur, Rajasthan"},
    {"name": "District Office Udaipur", "state": "Rajasthan", "district": "Udaipur", "type": "district_office", "phone": "0294-2528801", "address": "District Collectorate, Udaipur, Rajasthan"},
    {"name": "CSC Kota", "state": "Rajasthan", "district": "Kota", "type": "CSC", "phone": "0744-2500123", "address": "CSC District Centre, Collectorate, Kota, Rajasthan"},

    {"name": "CSC Bhopal", "state": "Madhya Pradesh", "district": "Bhopal", "type": "CSC", "phone": "0755-2551234", "address": "CSC District Centre, Collectorate, Bhopal, Madhya Pradesh"},
    {"name": "CSC Indore", "state": "Madhya Pradesh", "district": "Indore", "type": "CSC", "phone": "0731-2432100", "address": "CSC District Centre, Collector Office, Indore, Madhya Pradesh"},
    {"name": "District Office Jabalpur", "state": "Madhya Pradesh", "district": "Jabalpur", "type": "district_office", "phone": "0761-2621234", "address": "District Collectorate, Jabalpur, Madhya Pradesh"},
    {"name": "CSC Gwalior", "state": "Madhya Pradesh", "district": "Gwalior", "type": "CSC", "phone": "0751-2321234", "address": "CSC District Centre, Collector Office, Gwalior, Madhya Pradesh"},

    {"name": "CSC Bengaluru", "state": "Karnataka", "district": "Bengaluru", "type": "CSC", "phone": "080-22210888", "address": "CSC District Centre, DC Office, Bengaluru, Karnataka"},
    {"name": "CSC Mysuru", "state": "Karnataka", "district": "Mysuru", "type": "CSC", "phone": "0821-2422200", "address": "CSC District Centre, DC Office, Mysuru, Karnataka"},
    {"name": "District Office Hubballi", "state": "Karnataka", "district": "Dharwad", "type": "district_office", "phone": "0836-2233100", "address": "District Commissioner Office, Dharwad, Karnataka"},
    {"name": "CSC Mangaluru", "state": "Karnataka", "district": "Dakshina Kannada", "type": "CSC", "phone": "0824-2220589", "address": "CSC District Centre, DC Office, Mangaluru, Karnataka"},

    {"name": "CSC Kolkata", "state": "West Bengal", "district": "Kolkata", "type": "CSC", "phone": "033-22145600", "address": "CSC District Centre, Writers Building Area, Kolkata, West Bengal"},
    {"name": "CSC Howrah", "state": "West Bengal", "district": "Howrah", "type": "CSC", "phone": "033-26381234", "address": "CSC District Centre, DM Office, Howrah, West Bengal"},
    {"name": "District Office Siliguri", "state": "West Bengal", "district": "Darjeeling", "type": "district_office", "phone": "0353-2432100", "address": "District Magistrate Office, Siliguri, Darjeeling, West Bengal"},
    {"name": "CSC Asansol", "state": "West Bengal", "district": "Paschim Bardhaman", "type": "CSC", "phone": "0341-2252100", "address": "CSC District Centre, DM Office, Asansol, West Bengal"},

    {"name": "CSC Hyderabad", "state": "Telangana", "district": "Hyderabad", "type": "CSC", "phone": "040-23454610", "address": "CSC District Centre, Collectorate, Hyderabad, Telangana"},
    {"name": "CSC Warangal", "state": "Telangana", "district": "Warangal", "type": "CSC", "phone": "0870-2578100", "address": "CSC District Centre, Collector Office, Warangal, Telangana"},
    {"name": "District Office Karimnagar", "state": "Telangana", "district": "Karimnagar", "type": "district_office", "phone": "0878-2228001", "address": "District Collectorate, Karimnagar, Telangana"},
    {"name": "CSC Nizamabad", "state": "Telangana", "district": "Nizamabad", "type": "CSC", "phone": "08462-234567", "address": "CSC District Centre, Collector Office, Nizamabad, Telangana"},

    {"name": "CSC Bhubaneswar", "state": "Odisha", "district": "Khordha", "type": "CSC", "phone": "0674-2391234", "address": "CSC District Centre, Collectorate, Bhubaneswar, Odisha"},
    {"name": "CSC Cuttack", "state": "Odisha", "district": "Cuttack", "type": "CSC", "phone": "0671-2301234", "address": "CSC District Centre, Collector Office, Cuttack, Odisha"},
    {"name": "District Office Berhampur", "state": "Odisha", "district": "Ganjam", "type": "district_office", "phone": "0680-2281234", "address": "District Collectorate, Berhampur, Ganjam, Odisha"},
    {"name": "CSC Sambalpur", "state": "Odisha", "district": "Sambalpur", "type": "CSC", "phone": "0663-2521234", "address": "CSC District Centre, Collector Office, Sambalpur, Odisha"},
]


def _build_maps_url(name: str, address: str) -> str:
    query_str = f"{name}, {address}"
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query_str)}"


def get_help_centers(state: Optional[str] = None) -> List[Dict[str, Any]]:
    national = [c for c in HELP_CENTERS if c["type"] == "national_helpline"]

    if not state:
        results = national
    else:
        state_lower = state.strip().lower()
        state_centers = [
            c for c in HELP_CENTERS
            if c["state"].lower() == state_lower and c["type"] != "national_helpline"
        ]
        results = national + state_centers

    for center in results:
        center["maps_url"] = _build_maps_url(center["name"], center["address"])

    return results
