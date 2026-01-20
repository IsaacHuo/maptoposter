# -*- coding: utf-8 -*-
"""
Cities database with hierarchical structure for cascading selection.
Format: Country -> Province/State -> Cities
"""

CITIES = {
    "中国": {
        "北京": ["北京"],
        "上海": ["上海"],
        "天津": ["天津"],
        "重庆": ["重庆"],
        "广东": ["广州", "深圳", "东莞", "佛山", "珠海", "惠州", "中山", "汕头", "湛江", "江门"],
        "浙江": ["杭州", "宁波", "温州", "绍兴", "嘉兴", "金华", "台州", "湖州"],
        "江苏": ["南京", "苏州", "无锡", "常州", "南通", "徐州", "扬州", "镇江"],
        "山东": ["济南", "青岛", "烟台", "威海", "潍坊", "临沂", "济宁", "淄博"],
        "四川": ["成都", "绵阳", "德阳", "宜宾", "泸州", "南充", "乐山"],
        "湖北": ["武汉", "宜昌", "襄阳", "荆州", "黄石", "十堰"],
        "湖南": ["长沙", "株洲", "湘潭", "衡阳", "岳阳", "常德"],
        "河南": ["郑州", "洛阳", "开封", "新乡", "安阳", "焦作"],
        "河北": ["石家庄", "唐山", "秦皇岛", "邯郸", "保定", "沧州"],
        "福建": ["福州", "厦门", "泉州", "漳州", "莆田", "龙岩"],
        "安徽": ["合肥", "芜湖", "蚌埠", "马鞍山", "安庆", "黄山"],
        "江西": ["南昌", "九江", "景德镇", "赣州", "上饶", "吉安"],
        "陕西": ["西安", "咸阳", "宝鸡", "延安", "榆林", "汉中"],
        "山西": ["太原", "大同", "临汾", "运城", "晋中", "长治"],
        "辽宁": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "营口"],
        "吉林": ["长春", "吉林", "四平", "通化", "延边"],
        "黑龙江": ["哈尔滨", "齐齐哈尔", "牡丹江", "佳木斯", "大庆"],
        "云南": ["昆明", "大理", "丽江", "西双版纳", "曲靖"],
        "贵州": ["贵阳", "遵义", "安顺", "六盘水", "毕节"],
        "甘肃": ["兰州", "天水", "嘉峪关", "酒泉", "张掖"],
        "海南": ["海口", "三亚", "儋州", "琼海"],
        "广西": ["南宁", "桂林", "柳州", "北海", "玉林"],
        "内蒙古": ["呼和浩特", "包头", "鄂尔多斯", "赤峰", "呼伦贝尔"],
        "新疆": ["乌鲁木齐", "喀什", "吐鲁番", "阿克苏", "伊宁"],
        "西藏": ["拉萨", "日喀则", "林芝", "昌都"],
        "宁夏": ["银川", "石嘴山", "吴忠", "固原"],
        "青海": ["西宁", "格尔木", "玉树", "海东"],
        "香港": ["香港"],
        "澳门": ["澳门"],
        "台湾": ["台北", "高雄", "台中", "台南", "新竹", "基隆"],
    },
    "USA": {
        "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento", "Oakland", "Fresno"],
        "New York": ["New York City", "Buffalo", "Rochester", "Albany", "Syracuse"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso"],
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
        "Illinois": ["Chicago", "Aurora", "Naperville", "Rockford"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh", "Harrisburg"],
        "Arizona": ["Phoenix", "Tucson", "Mesa", "Scottsdale"],
        "Nevada": ["Las Vegas", "Reno", "Henderson"],
        "Washington": ["Seattle", "Tacoma", "Spokane", "Bellevue"],
        "Massachusetts": ["Boston", "Cambridge", "Worcester"],
        "Colorado": ["Denver", "Colorado Springs", "Aurora", "Boulder"],
        "Georgia": ["Atlanta", "Savannah", "Augusta"],
        "North Carolina": ["Charlotte", "Raleigh", "Durham"],
        "Michigan": ["Detroit", "Grand Rapids", "Ann Arbor"],
        "Oregon": ["Portland", "Salem", "Eugene"],
        "District of Columbia": ["Washington"],
        "Hawaii": ["Honolulu"],
    },
    "Japan": {
        "関東": ["Tokyo", "Yokohama", "Kawasaki", "Saitama", "Chiba"],
        "関西": ["Osaka", "Kyoto", "Kobe", "Nara"],
        "中部": ["Nagoya", "Kanazawa", "Shizuoka"],
        "北海道": ["Sapporo", "Hakodate", "Asahikawa"],
        "九州": ["Fukuoka", "Nagasaki", "Kumamoto", "Kagoshima"],
        "東北": ["Sendai", "Aomori", "Akita"],
        "中国": ["Hiroshima", "Okayama"],
        "四国": ["Matsuyama", "Takamatsu"],
        "沖縄": ["Naha", "Okinawa"],
    },
    "UK": {
        "England": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds", "Bristol", "Sheffield", "Newcastle", "Nottingham", "Cambridge", "Oxford"],
        "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee"],
        "Wales": ["Cardiff", "Swansea", "Newport"],
        "Northern Ireland": ["Belfast", "Londonderry"],
    },
    "France": {
        "Île-de-France": ["Paris"],
        "Provence-Alpes-Côte d'Azur": ["Marseille", "Nice", "Cannes", "Toulon"],
        "Auvergne-Rhône-Alpes": ["Lyon", "Grenoble", "Saint-Étienne"],
        "Nouvelle-Aquitaine": ["Bordeaux", "Limoges"],
        "Occitanie": ["Toulouse", "Montpellier", "Nîmes"],
        "Hauts-de-France": ["Lille", "Amiens"],
        "Grand Est": ["Strasbourg", "Reims", "Nancy", "Metz"],
        "Normandie": ["Rouen", "Le Havre", "Caen"],
        "Bretagne": ["Rennes", "Brest", "Nantes"],
    },
    "Germany": {
        "Bayern": ["Munich", "Nuremberg", "Augsburg"],
        "Berlin": ["Berlin"],
        "Hamburg": ["Hamburg"],
        "Hessen": ["Frankfurt", "Wiesbaden"],
        "Baden-Württemberg": ["Stuttgart", "Heidelberg", "Freiburg", "Karlsruhe"],
        "Nordrhein-Westfalen": ["Cologne", "Düsseldorf", "Dortmund", "Essen", "Bonn"],
        "Niedersachsen": ["Hanover", "Braunschweig", "Oldenburg"],
        "Sachsen": ["Dresden", "Leipzig"],
        "Brandenburg": ["Potsdam"],
    },
    "Italy": {
        "Lazio": ["Rome"],
        "Lombardia": ["Milan", "Bergamo", "Brescia"],
        "Veneto": ["Venice", "Verona", "Padua"],
        "Toscana": ["Florence", "Pisa", "Siena"],
        "Campania": ["Naples", "Salerno"],
        "Piemonte": ["Turin", "Genoa"],
        "Emilia-Romagna": ["Bologna", "Parma", "Modena"],
        "Sicilia": ["Palermo", "Catania", "Syracuse"],
    },
    "Spain": {
        "Comunidad de Madrid": ["Madrid"],
        "Cataluña": ["Barcelona", "Tarragona", "Girona"],
        "Andalucía": ["Seville", "Granada", "Málaga", "Córdoba"],
        "Comunidad Valenciana": ["Valencia", "Alicante"],
        "País Vasco": ["Bilbao", "San Sebastián"],
        "Galicia": ["Santiago de Compostela", "A Coruña", "Vigo"],
        "Islas Baleares": ["Palma de Mallorca"],
        "Islas Canarias": ["Las Palmas", "Santa Cruz de Tenerife"],
    },
    "Australia": {
        "New South Wales": ["Sydney", "Newcastle", "Wollongong"],
        "Victoria": ["Melbourne", "Geelong"],
        "Queensland": ["Brisbane", "Gold Coast", "Cairns"],
        "Western Australia": ["Perth", "Fremantle"],
        "South Australia": ["Adelaide"],
        "Tasmania": ["Hobart"],
        "Australian Capital Territory": ["Canberra"],
        "Northern Territory": ["Darwin"],
    },
    "Canada": {
        "Ontario": ["Toronto", "Ottawa", "Hamilton", "Mississauga"],
        "Quebec": ["Montreal", "Quebec City", "Laval"],
        "British Columbia": ["Vancouver", "Victoria", "Surrey"],
        "Alberta": ["Calgary", "Edmonton"],
        "Manitoba": ["Winnipeg"],
        "Saskatchewan": ["Saskatoon", "Regina"],
        "Nova Scotia": ["Halifax"],
    },
    "South Korea": {
        "서울특별시": ["Seoul"],
        "부산광역시": ["Busan"],
        "경기도": ["Incheon", "Suwon", "Seongnam"],
        "대구광역시": ["Daegu"],
        "대전광역시": ["Daejeon"],
        "광주광역시": ["Gwangju"],
        "제주특별자치도": ["Jeju"],
    },
    "Singapore": {
        "Singapore": ["Singapore"],
    },
    "India": {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
        "Delhi": ["New Delhi"],
        "Karnataka": ["Bangalore", "Mysore"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
        "West Bengal": ["Kolkata"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
        "Telangana": ["Hyderabad"],
        "Kerala": ["Kochi", "Trivandrum"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
        "Uttar Pradesh": ["Lucknow", "Agra", "Varanasi"],
    },
    "Russia": {
        "Центральный": ["Moscow"],
        "Северо-Западный": ["Saint Petersburg", "Kaliningrad"],
        "Южный": ["Sochi", "Rostov-on-Don", "Krasnodar"],
        "Приволжский": ["Kazan", "Nizhny Novgorod", "Samara"],
        "Уральский": ["Yekaterinburg", "Chelyabinsk"],
        "Сибирский": ["Novosibirsk", "Krasnoyarsk", "Irkutsk"],
        "Дальневосточный": ["Vladivostok", "Khabarovsk"],
    },
    "Brazil": {
        "São Paulo": ["São Paulo", "Campinas", "Santos"],
        "Rio de Janeiro": ["Rio de Janeiro", "Niterói"],
        "Minas Gerais": ["Belo Horizonte"],
        "Bahia": ["Salvador"],
        "Rio Grande do Sul": ["Porto Alegre"],
        "Paraná": ["Curitiba"],
        "Distrito Federal": ["Brasília"],
        "Ceará": ["Fortaleza"],
        "Pernambuco": ["Recife"],
        "Amazonas": ["Manaus"],
    },
    "Mexico": {
        "Ciudad de México": ["Mexico City"],
        "Jalisco": ["Guadalajara"],
        "Nuevo León": ["Monterrey"],
        "Quintana Roo": ["Cancún", "Playa del Carmen"],
        "Baja California": ["Tijuana", "Ensenada"],
        "Yucatán": ["Mérida"],
        "Puebla": ["Puebla"],
        "Guanajuato": ["León", "Guanajuato"],
    },
    "Netherlands": {
        "Noord-Holland": ["Amsterdam", "Haarlem"],
        "Zuid-Holland": ["Rotterdam", "The Hague", "Leiden"],
        "Utrecht": ["Utrecht"],
        "Noord-Brabant": ["Eindhoven", "Tilburg", "'s-Hertogenbosch"],
        "Gelderland": ["Arnhem", "Nijmegen"],
        "Limburg": ["Maastricht"],
    },
    "Belgium": {
        "Brussels-Capital": ["Brussels"],
        "Flanders": ["Antwerp", "Ghent", "Bruges"],
        "Wallonia": ["Liège", "Charleroi", "Namur"],
    },
    "Switzerland": {
        "Zürich": ["Zurich"],
        "Bern": ["Bern"],
        "Geneva": ["Geneva"],
        "Vaud": ["Lausanne"],
        "Basel-Stadt": ["Basel"],
        "Lucerne": ["Lucerne"],
    },
    "Austria": {
        "Wien": ["Vienna"],
        "Salzburg": ["Salzburg"],
        "Tirol": ["Innsbruck"],
        "Steiermark": ["Graz"],
        "Oberösterreich": ["Linz"],
    },
    "Portugal": {
        "Lisboa": ["Lisbon"],
        "Porto": ["Porto"],
        "Faro": ["Faro", "Albufeira"],
        "Coimbra": ["Coimbra"],
    },
    "Greece": {
        "Attica": ["Athens", "Piraeus"],
        "Central Macedonia": ["Thessaloniki"],
        "Crete": ["Heraklion"],
        "South Aegean": ["Rhodes", "Mykonos", "Santorini"],
    },
    "Turkey": {
        "Istanbul": ["Istanbul"],
        "Ankara": ["Ankara"],
        "Izmir": ["Izmir"],
        "Antalya": ["Antalya"],
        "Bursa": ["Bursa"],
        "Cappadocia": ["Nevşehir", "Göreme"],
    },
    "UAE": {
        "Dubai": ["Dubai"],
        "Abu Dhabi": ["Abu Dhabi"],
        "Sharjah": ["Sharjah"],
        "Ras Al Khaimah": ["Ras Al Khaimah"],
    },
    "Thailand": {
        "Bangkok": ["Bangkok"],
        "Chiang Mai": ["Chiang Mai"],
        "Phuket": ["Phuket"],
        "Chonburi": ["Pattaya"],
        "Krabi": ["Krabi"],
    },
    "Vietnam": {
        "Hà Nội": ["Hanoi"],
        "Hồ Chí Minh": ["Ho Chi Minh City"],
        "Đà Nẵng": ["Da Nang"],
        "Khánh Hòa": ["Nha Trang"],
        "Quảng Ninh": ["Ha Long"],
    },
    "Indonesia": {
        "DKI Jakarta": ["Jakarta"],
        "Bali": ["Bali", "Denpasar", "Ubud"],
        "Jawa Timur": ["Surabaya"],
        "Jawa Barat": ["Bandung"],
        "DI Yogyakarta": ["Yogyakarta"],
    },
    "Malaysia": {
        "Kuala Lumpur": ["Kuala Lumpur"],
        "Penang": ["George Town"],
        "Selangor": ["Petaling Jaya", "Shah Alam"],
        "Johor": ["Johor Bahru"],
        "Sabah": ["Kota Kinabalu"],
        "Sarawak": ["Kuching"],
    },
    "Philippines": {
        "Metro Manila": ["Manila", "Makati", "Quezon City"],
        "Cebu": ["Cebu City"],
        "Davao": ["Davao City"],
        "Palawan": ["Puerto Princesa"],
    },
    "Egypt": {
        "Cairo Governorate": ["Cairo"],
        "Alexandria Governorate": ["Alexandria"],
        "Giza Governorate": ["Giza"],
        "Luxor Governorate": ["Luxor"],
        "Red Sea Governorate": ["Hurghada", "Sharm El Sheikh"],
    },
    "South Africa": {
        "Gauteng": ["Johannesburg", "Pretoria"],
        "Western Cape": ["Cape Town"],
        "KwaZulu-Natal": ["Durban"],
        "Eastern Cape": ["Port Elizabeth"],
    },
    "Morocco": {
        "Casablanca-Settat": ["Casablanca"],
        "Rabat-Salé-Kénitra": ["Rabat"],
        "Marrakech-Safi": ["Marrakech", "Essaouira"],
        "Fès-Meknès": ["Fes", "Meknes"],
        "Tanger-Tétouan-Al Hoceïma": ["Tangier", "Chefchaouen"],
    },
    "Argentina": {
        "Buenos Aires": ["Buenos Aires", "La Plata"],
        "Córdoba": ["Córdoba"],
        "Mendoza": ["Mendoza"],
        "Santa Fe": ["Rosario"],
        "Tierra del Fuego": ["Ushuaia"],
    },
    "Chile": {
        "Región Metropolitana": ["Santiago"],
        "Valparaíso": ["Valparaíso", "Viña del Mar"],
        "Biobío": ["Concepción"],
        "Los Lagos": ["Puerto Montt"],
        "Magallanes": ["Punta Arenas"],
    },
    "Colombia": {
        "Bogotá D.C.": ["Bogotá"],
        "Antioquia": ["Medellín"],
        "Valle del Cauca": ["Cali"],
        "Atlántico": ["Barranquilla"],
        "Bolívar": ["Cartagena"],
    },
    "Peru": {
        "Lima": ["Lima"],
        "Cusco": ["Cusco"],
        "Arequipa": ["Arequipa"],
        "La Libertad": ["Trujillo"],
    },
    "New Zealand": {
        "Auckland": ["Auckland"],
        "Wellington": ["Wellington"],
        "Canterbury": ["Christchurch"],
        "Otago": ["Dunedin", "Queenstown"],
    },
    "Ireland": {
        "Leinster": ["Dublin"],
        "Munster": ["Cork", "Limerick"],
        "Connacht": ["Galway"],
    },
    "Sweden": {
        "Stockholms län": ["Stockholm"],
        "Västra Götalands län": ["Gothenburg"],
        "Skåne län": ["Malmö"],
        "Uppsala län": ["Uppsala"],
    },
    "Norway": {
        "Oslo": ["Oslo"],
        "Vestland": ["Bergen"],
        "Troms og Finnmark": ["Tromsø"],
        "Trøndelag": ["Trondheim"],
    },
    "Denmark": {
        "Hovedstaden": ["Copenhagen"],
        "Midtjylland": ["Aarhus"],
        "Syddanmark": ["Odense"],
    },
    "Finland": {
        "Uusimaa": ["Helsinki", "Espoo"],
        "Pirkanmaa": ["Tampere"],
        "Southwest Finland": ["Turku"],
        "Lapland": ["Rovaniemi"],
    },
    "Poland": {
        "Mazowieckie": ["Warsaw"],
        "Małopolskie": ["Kraków"],
        "Wielkopolskie": ["Poznań"],
        "Dolnośląskie": ["Wrocław"],
        "Pomorskie": ["Gdańsk"],
    },
    "Czech Republic": {
        "Praha": ["Prague"],
        "Jihomoravský": ["Brno"],
        "Moravskoslezský": ["Ostrava"],
        "Plzeňský": ["Plzeň"],
    },
    "Hungary": {
        "Budapest": ["Budapest"],
        "Pest": ["Szentendre"],
        "Baranya": ["Pécs"],
        "Hajdú-Bihar": ["Debrecen"],
    },
    "Israel": {
        "Tel Aviv District": ["Tel Aviv", "Jaffa"],
        "Jerusalem District": ["Jerusalem"],
        "Haifa District": ["Haifa"],
        "Southern District": ["Eilat"],
    },
    "Saudi Arabia": {
        "Riyadh": ["Riyadh"],
        "Makkah": ["Mecca", "Jeddah"],
        "Eastern Province": ["Dammam", "Dhahran"],
        "Medina": ["Medina"],
    },
    "Qatar": {
        "Doha": ["Doha"],
    },
    "Kenya": {
        "Nairobi": ["Nairobi"],
        "Mombasa": ["Mombasa"],
        "Nakuru": ["Nakuru"],
    },
    "Nigeria": {
        "Lagos": ["Lagos"],
        "Abuja": ["Abuja"],
        "Kano": ["Kano"],
    },
    "Pakistan": {
        "Punjab": ["Lahore", "Faisalabad"],
        "Sindh": ["Karachi"],
        "Islamabad": ["Islamabad"],
        "Khyber Pakhtunkhwa": ["Peshawar"],
    },
    "Bangladesh": {
        "Dhaka Division": ["Dhaka"],
        "Chittagong Division": ["Chittagong"],
        "Sylhet Division": ["Sylhet"],
    },
    "Sri Lanka": {
        "Western Province": ["Colombo"],
        "Central Province": ["Kandy"],
        "Southern Province": ["Galle"],
    },
    "Nepal": {
        "Bagmati": ["Kathmandu"],
        "Gandaki": ["Pokhara"],
    },
}


def get_countries():
    """Return sorted list of all countries."""
    return sorted(CITIES.keys())


def get_provinces(country):
    """Return sorted list of provinces/states for a given country."""
    if country in CITIES:
        return sorted(CITIES[country].keys())
    return []


def get_cities(country, province):
    """Return sorted list of cities for a given country and province."""
    if country in CITIES and province in CITIES[country]:
        return sorted(CITIES[country][province])
    return []


def search_cities(query):
    """
    Search for cities matching the query.
    Returns list of tuples: (city, province, country)
    """
    if not query or len(query) < 2:
        return []
    
    query = query.lower()
    results = []
    
    for country, provinces in CITIES.items():
        for province, cities in provinces.items():
            for city in cities:
                if query in city.lower():
                    results.append((city, province, country))
    
    # Sort by city name
    return sorted(results, key=lambda x: x[0])[:20]  # Limit to 20 results


def get_city_full_name(city, province, country):
    """Return formatted full name for display."""
    if province == city:  # Direct-controlled municipalities
        return f"{city}, {country}"
    return f"{city}, {province}, {country}"
