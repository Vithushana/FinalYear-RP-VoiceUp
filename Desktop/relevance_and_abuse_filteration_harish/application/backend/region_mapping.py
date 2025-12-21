"""
Sri Lanka Region Mapping
Maps GPS coordinates to specific regions/MC/UC within districts
"""

# Region mapping: Province -> District -> List of Regions (MC/UC/PS)
REGION_MAPPING = {
    "Western Province": {
        "Colombo": [
            "Colombo MC",
            "Dehiwala-Mount Lavinia MC",
            "Sri Jayawardenepura Kotte MC",
            "Kaduwela MC",
            "Kolonnawa UC",
            "Kesbewa UC",
            "Maharagama UC",
            "Moratuwa MC",
            "Homagama UC",
            "Seethawaka PS",
            "Padukka PS",
            "Hanwella PS",
            "Rathmalana UC"
        ],
        "Gampaha": [
            "Gampaha MC",
            "Negombo MC",
            "Katunayake-Seeduwa UC",
            "Ja-Ela UC",
            "Wattala-Mabole UC",
            "Kelaniya UC",
            "Peliyagoda UC",
            "Kadawatha UC",
            "Biyagama PS",
            "Dompe PS",
            "Gampaha PS",
            "Ja-Ela PS",
            "Katana PS",
            "Kelaniya PS",
            "Mahara PS",
            "Minuwangoda PS",
            "Mirigama PS",
            "Negombo PS",
            "Wattala PS",
            "Attanagalla PS",
            "Divulapitiya PS"
        ],
        "Kalutara": [
            "Kalutara UC",
            "Beruwala UC",
            "Panadura UC",
            "Horana UC",
            "Matugama UC",
            "Bandaragama PS",
            "Beruwala PS",
            "Bulathsinhala PS",
            "Dodangoda PS",
            "Horana PS",
            "Ingiriya PS",
            "Kalutara PS",
            "Madurawala PS",
            "Matugama PS",
            "Millaniya PS",
            "Palindanuwara PS",
            "Panadura PS",
            "Walallavita PS"
        ]
    },
    "Central Province": {
        "Kandy": [
            "Kandy MC",
            "Gampola UC",
            "Nawalapitiya UC",
            "Katugastota UC",
            "Akurana UC",
            "Galagedara PS",
            "Harispattuwa PS",
            "Hatharaliyadda PS",
            "Kandy Four Gravets PS",
            "Medadumbara PS",
            "Minipe PS",
            "Panvila PS",
            "Pasbage Korale PS",
            "Pathahewaheta PS",
            "Pathadumbara PS",
            "Poojapitiya PS",
            "Tumpane PS",
            "Udadumbara PS",
            "Udapalatha PS",
            "Udunuwara PS",
            "Yatinuwara PS"
        ],
        "Matale": [
            "Matale MC",
            "Dambulla UC",
            "Ukuwela UC",
            "Ambanganga Korale PS",
            "Dambulla PS",
            "Galewela PS",
            "Laggala-Pallegama PS",
            "Matale PS",
            "Naula PS",
            "Rattota PS",
            "Ukuwela PS",
            "Yatawatta PS"
        ],
        "Nuwara Eliya": [
            "Nuwara Eliya MC",
            "Hatton-Dickoya UC",
            "Talawakelle UC",
            "Nuwara Eliya PS",
            "Kotmale PS",
            "Hanguranketha PS",
            "Walapane PS",
            "Ambagamuwa PS"
        ]
    },
    "Southern Province": {
        "Galle": [
            "Galle MC",
            "Hikkaduwa UC",
            "Ambalangoda UC",
            "Elpitiya UC",
            "Bentota UC",
            "Baddegama PS",
            "Balapitiya PS",
            "Benthota PS",
            "Elpitiya PS",
            "Galle Four Gravets PS",
            "Gonapinuwala PS",
            "Habaraduwa PS",
            "Hikkaduwa PS",
            "Imaduwa PS",
            "Karandeniya PS",
            "Nagoda PS",
            "Niyagama PS",
            "Thawalama PS",
            "Yakkalamulla PS"
        ],
        "Matara": [
            "Matara MC",
            "Weligama UC",
            "Akuressa UC",
            "Deniyaya UC",
            "Hakmana UC",
            "Akuressa PS",
            "Athuraliya PS",
            "Devinuwara PS",
            "Dickwella PS",
            "Hakmana PS",
            "Kamburupitiya PS",
            "Kirinda Puhulwella PS",
            "Kotapola PS",
            "Matara Four Gravets PS",
            "Mulatiyana PS",
            "Pasgoda PS",
            "Pitabeddara PS",
            "Thihagoda PS",
            "Weligama PS"
        ],
        "Hambantota": [
            "Hambantota UC",
            "Tangalle UC",
            "Tissamaharama UC",
            "Ambalantota PS",
            "Angunakolapelessa PS",
            "Beliatta PS",
            "Hambantota PS",
            "Katuwana PS",
            "Lunugamvehera PS",
            "Okewela PS",
            "Suriyawewa PS",
            "Tangalle PS",
            "Thissamaharama PS",
            "Weeraketiya PS"
        ]
    },
    "Northern Province": {
        "Jaffna": [
            "Jaffna MC",
            "Chavakachcheri UC",
            "Point Pedro UC",
            "Valvettithurai UC",
            "Chankanai PS",
            "Chavakachcheri PS",
            "Delft PS",
            "Island North PS",
            "Island South PS",
            "Jaffna PS",
            "Karainagar PS",
            "Kayts PS",
            "Nallur PS",
            "Point Pedro PS",
            "Sandilipay PS",
            "Tellippalai PS",
            "Uduvil PS",
            "Vadamaradchi East PS",
            "Vadamaradchi South-West PS",
            "Valikamam East PS",
            "Valikamam North PS",
            "Valikamam South PS",
            "Valikamam South-West PS",
            "Valikamam West PS"
        ],
        "Kilinochchi": [
            "Kilinochchi PS",
            "Kandavalai PS",
            "Karachchi PS",
            "Pachchilaipalli PS",
            "Poonakary PS"
        ],
        "Mannar": [
            "Mannar UC",
            "Mannar Town PS",
            "Madhu PS",
            "Manthai West PS",
            "Musali PS",
            "Nanaddan PS"
        ],
        "Vavuniya": [
            "Vavuniya UC",
            "Vavuniya PS",
            "Vavuniya North PS",
            "Vavuniya South PS",
            "Vengalacheddikulam PS"
        ],
        "Mullaitivu": [
            "Mullaitivu PS",
            "Maritimepattu PS",
            "Oddusuddan PS",
            "Puthukudiyiruppu PS",
            "Thunukkai PS",
            "Welioya PS"
        ]
    },
    "Eastern Province": {
        "Trincomalee": [
            "Trincomalee UC",
            "Kinniya UC",
            "Gomarankadawala PS",
            "Kantalai PS",
            "Kinniya PS",
            "Kuchchaveli PS",
            "Morawewa PS",
            "Muttur PS",
            "Padavi Siripura PS",
            "Seruvila PS",
            "Thampalakamam PS",
            "Town and Gravets PS",
            "Trincomalee Gravets PS",
            "Verugal PS"
        ],
        "Batticaloa": [
            "Batticaloa MC",
            "Kattankudy UC",
            "Eravur Town UC",
            "Batticaloa PS",
            "Eravur Pattu PS",
            "Eravur Town PS",
            "Kattankudy PS",
            "Koralai Pattu PS",
            "Koralai Pattu North PS",
            "Koralai Pattu West PS",
            "Manmunai North PS",
            "Manmunai Pattu PS",
            "Manmunai South and Eruvil Pattu PS",
            "Manmunai South West PS",
            "Manmunai West PS",
            "Porativu Pattu PS"
        ],
        "Ampara": [
            "Ampara UC",
            "Kalmunai MC",
            "Sammanthurai PS",
            "Akkaraipattu PS",
            "Alayadivembu PS",
            "Ampara PS",
            "Dehiattakandiya PS",
            "Irakkamam PS",
            "Kalmunai PS",
            "Karaitivu PS",
            "Lahugala PS",
            "Mahaoya PS",
            "Navithanveli PS",
            "Ninthavur PS",
            "Padiyathalawa PS",
            "Pottuvil PS",
            "Sainthamaruthu PS",
            "Samanthurai PS",
            "Thirukkovil PS",
            "Uhana PS"
        ]
    },
    "North Western Province": {
        "Kurunegala": [
            "Kurunegala MC",
            "Kuliyapitiya UC",
            "Pannala UC",
            "Wariyapola UC",
            "Alawwa PS",
            "Ambanpola PS",
            "Bamunakotuwa PS",
            "Bingiriya PS",
            "Ehetuwewa PS",
            "Galgamuwa PS",
            "Ganewatta PS",
            "Giriulla PS",
            "Ibbagamuwa PS",
            "Katugampola PS",
            "Kobeigane PS",
            "Kuliyapitiya PS",
            "Kurunegala PS",
            "Maho PS",
            "Mallawapitiya PS",
            "Maspotha PS",
            "Mawathagama PS",
            "Narammala PS",
            "Nikaweratiya PS",
            "Panduwasnuwara PS",
            "Pannala PS",
            "Polgahawela PS",
            "Polpithigama PS",
            "Rasnayakapura PS",
            "Rideegama PS",
            "Udubaddawa PS",
            "Wariyapola PS",
            "Weuda PS",
            "Yapahuwa PS"
        ],
        "Puttalam": [
            "Puttalam UC",
            "Chilaw UC",
            "Wennappuwa UC",
            "Nattandiya UC",
            "Dankotuwa UC",
            "Anamaduwa PS",
            "Arachchikattuwa PS",
            "Chilaw PS",
            "Dankotuwa PS",
            "Kalpitiya PS",
            "Karuwalagaswewa PS",
            "Madampe PS",
            "Mahakumbukkadawala PS",
            "Mahawewa PS",
            "Mundel PS",
            "Nattandiya PS",
            "Nawagattegama PS",
            "Pallama PS",
            "Puttalam PS",
            "Vanathavilluwa PS",
            "Wennappuwa PS"
        ]
    },
    "North Central Province": {
        "Anuradhapura": [
            "Anuradhapura MC",
            "Medawachchiya UC",
            "Anuradhapura PS",
            "Galenbindunuwewa PS",
            "Galnewa PS",
            "Horowpothana PS",
            "Ipalogama PS",
            "Kahatagasdigiliya PS",
            "Kebithigollewa PS",
            "Kekirawa PS",
            "Madawachchiya PS",
            "Mihintale PS",
            "Nochchiyagama PS",
            "Nuwaragam Palatha Central PS",
            "Nuwaragam Palatha East PS",
            "Padaviya PS",
            "Palugaswewa PS",
            "Rajanganaya PS",
            "Rambewa PS",
            "Talawa PS",
            "Tambuttegama PS",
            "Thirappane PS"
        ],
        "Polonnaruwa": [
            "Polonnaruwa UC",
            "Kaduruwela UC",
            "Dimbulagala PS",
            "Elahera PS",
            "Hingurakgoda PS",
            "Lankapura PS",
            "Medirigiriya PS",
            "Polonnaruwa PS",
            "Thamankaduwa PS",
            "Welikanda PS"
        ]
    },
    "Uva Province": {
        "Badulla": [
            "Badulla MC",
            "Bandarawela MC",
            "Haputale UC",
            "Welimada UC",
            "Mahiyanganaya UC",
            "Badulla PS",
            "Bandarawela PS",
            "Ella PS",
            "Haldummulla PS",
            "Hali-Ela PS",
            "Haputale PS",
            "Kandaketiya PS",
            "Lunugala PS",
            "Mahiyanganaya PS",
            "Meegahakivula PS",
            "Passara PS",
            "Rideemaliyadda PS",
            "Soranathota PS",
            "Uva Paranagama PS",
            "Welimada PS",
            "Wiyaluwa PS"
        ],
        "Monaragala": [
            "Monaragala UC",
            "Wellawaya UC",
            "Bibile PS",
            "Buttala PS",
            "Katharagama PS",
            "Madulla PS",
            "Medagama PS",
            "Moneragala PS",
            "Nelliyadda PS",
            "Sevanagala PS",
            "Siyambalanduwa PS",
            "Thanamalvila PS",
            "Wellawaya PS"
        ]
    },
    "Sabaragamuwa Province": {
        "Ratnapura": [
            "Ratnapura MC",
            "Embilipitiya UC",
            "Balangoda UC",
            "Pelmadulla UC",
            "Ayagama PS",
            "Balangoda PS",
            "Eheliyagoda PS",
            "Elapatha PS",
            "Embilipitiya PS",
            "Godakawela PS",
            "Imbulpe PS",
            "Kahawatta PS",
            "Kalawana PS",
            "Kiriella PS",
            "Kolonna PS",
            "Kuruwita PS",
            "Nivithigala PS",
            "Opanayaka PS",
            "Pelmadulla PS",
            "Ratnapura PS",
            "Weligepola PS"
        ],
        "Kegalle": [
            "Kegalle MC",
            "Mawanella UC",
            "Warakapola UC",
            "Rambukkana UC",
            "Aranayaka PS",
            "Bulathkohupitiya PS",
            "Dehiowita PS",
            "Deraniyagala PS",
            "Galigamuwa PS",
            "Kegalle PS",
            "Mawanella PS",
            "Rambukkana PS",
            "Ruwanwella PS",
            "Warakapola PS",
            "Yatiyantota PS"
        ]
    }
}


def get_region_from_locality(locality, district):
    """
    Get the specific region from locality string
    
    Args:
        locality (str): Locality from geocoding (e.g., "Kaduwela", "Colombo")
        district (str): District name
        
    Returns:
        str: Matched region or locality itself
    """
    if not locality or not district:
        return locality
    
    # Get regions for this district
    for province, districts in REGION_MAPPING.items():
        if district in districts:
            regions = districts[district]
            
            # Try to find exact match
            for region in regions:
                if locality.lower() in region.lower() or region.lower() in locality.lower():
                    return region
            
            # If no match, return locality as-is
            return locality
    
    return locality
