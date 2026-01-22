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
        "广西": ["南宁", "桂林", "柳州", "梧州", "北海", "玉林"],
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

# Translation layer for dual-language support
CN_TO_EN = {
    # Countries (CN -> EN)
    "中国": "China",
    "美国": "United States",
    "日本": "Japan",
    "英国": "United Kingdom",
    "法国": "France",
    "德国": "Germany",
    "意大利": "Italy",
    "西班牙": "Spain",
    "澳大利亚": "Australia",
    "加拿大": "Canada",
    "韩国": "South Korea",
    "新加坡": "Singapore",
    "印度": "India",
    "俄罗斯": "Russia",
    "巴西": "Brazil",
    "墨西哥": "Mexico",
    "荷兰": "Netherlands",
    "比利时": "Belgium",
    "瑞士": "Switzerland",
    "奥地利": "Austria",
    "葡萄牙": "Portugal",
    "希腊": "Greece",
    "土耳其": "Turkey",
    "阿联酋": "United Arab Emirates",
    "泰国": "Thailand",
    "越南": "Vietnam",
    "印度尼西亚": "Indonesia",
    "马来西亚": "Malaysia",
    "菲律宾": "Philippines",
    "埃及": "Egypt",
    "南非": "South Africa",
    "摩洛哥": "Morocco",
    "阿根廷": "Argentina",
    "智利": "Chile",
    "哥伦比亚": "Colombia",
    "秘鲁": "Peru",
    "新西兰": "New Zealand",
    "爱尔兰": "Ireland",
    "瑞典": "Sweden",
    "挪威": "Norway",
    "丹麦": "Denmark",
    "芬兰": "Finland",
    "波兰": "Poland",
    "捷克": "Czech Republic",
    "匈牙利": "Hungary",
    "以色列": "Israel",
    "沙特阿拉伯": "Saudi Arabia",
    "卡塔尔": "Qatar",
    "肯尼亚": "Kenya",
    "尼日利亚": "Nigeria",
    "巴基斯坦": "Pakistan",
    "孟加拉国": "Bangladesh",
    "斯里兰卡": "Sri Lanka",
    "尼泊尔": "Nepal",
    
    # Chinese Provinces (CN -> EN)
    "北京": "Beijing",
    "上海": "Shanghai",
    "天津": "Tianjin",
    "重庆": "Chongqing",
    "广东": "Guangdong",
    "浙江": "Zhejiang",
    "江苏": "Jiangsu",
    "山东": "Shandong",
    "四川": "Sichuan",
    "湖北": "Hubei",
    "湖南": "Hunan",
    "河南": "Henan",
    "河北": "Hebei",
    "福建": "Fujian",
    "安徽": "Anhui",
    "江西": "Jiangxi",
    "陕西": "Shaanxi",
    "山西": "Shanxi",
    "辽宁": "Liaoning",
    "吉林": "Jilin",
    "黑龙江": "Heilongjiang",
    "云南": "Yunnan",
    "贵州": "Guizhou",
    "甘肃": "Gansu",
    "海南": "Hainan",
    "广西": "Guangxi",
    "内蒙古": "Inner Mongolia",
    "新疆": "Xinjiang",
    "西藏": "Tibet",
    "宁夏": "Ningxia",
    "青海": "Qinghai",
    "香港": "Hong Kong",
    "澳门": "Macau",
    "台湾": "Taiwan",

    # Chinese Cities (CN -> EN)
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "东莞": "Dongguan",
    "佛山": "Foshan",
    "珠海": "Zhuhai",
    "惠州": "Huizhou",
    "中山": "Zhongshan",
    "汕头": "Shantou",
    "湛江": "Zhanjiang",
    "江门": "Jiangmen",
    "梧州": "Wuzhou",
    "杭州": "Hangzhou",
    "宁波": "Ningbo",
    "温州": "Wenzhou",
    "绍兴": "Shaoxing",
    "嘉兴": "Jiaxing",
    "金华": "Jinhua",
    "台州": "Taizhou",
    "湖州": "Huzhou",
    "南京": "Nanjing",
    "苏州": "Suzhou",
    "无锡": "Wuxi",
    "常州": "Changzhou",
    "南通": "Nantong",
    "徐州": "Xuzhou",
    "扬州": "Yangzhou",
    "镇江": "Zhenjiang",
    "济南": "Jinan",
    "青岛": "Qingdao",
    "烟台": "Yantai",
    "威海": "Weihai",
    "潍坊": "Weifang",
    "临沂": "Linyi",
    "济宁": "Jining",
    "淄博": "Zibo",
    "成都": "Chengdu",
    "绵阳": "Mianyang",
    "德阳": "Deyang",
    "宜宾": "Yibin",
    "泸州": "Luzhou",
    "南充": "Nanchong",
    "乐山": "Leshan",
    "武汉": "Wuhan",
    "宜昌": "Yichang",
    "襄阳": "Xiangyang",
    "荆州": "Jingzhou",
    "黄石": "Huangshi",
    "十堰": "Shiyan",
    "长沙": "Changsha",
    "株洲": "Zhuzhou",
    "湘潭": "Xiangtan",
    "衡阳": "Hengyang",
    "岳阳": "Yueyang",
    "常德": "Changde",
    "郑州": "Zhengzhou",
    "洛阳": "Luoyang",
    "开封": "Kaifeng",
    "新乡": "Xinxiang",
    "安阳": "Anyang",
    "焦作": "Jiaozuo",
    "石家庄": "Shijiazhuang",
    "唐山": "Tangshan",
    "秦皇岛": "Qinhuangdao",
    "邯郸": "Handan",
    "保定": "Baoding",
    "沧州": "Cangzhou",
    "福州": "Fuzhou",
    "厦门": "Xiamen",
    "泉州": "Quanzhou",
    "漳州": "Zhangzhou",
    "莆田": "Putian",
    "龙岩": "Longyan",
    "合肥": "Hefei",
    "芜湖": "Wuhu",
    "蚌埠": "Bengbu",
    "马鞍山": "Ma'anshan",
    "安庆": "Anqing",
    "黄山": "Huangshan",
    "南昌": "Nanchang",
    "九江": "Jiujiang",
    "景德镇": "Jingdezhen",
    "赣州": "Ganzhou",
    "上饶": "Shangrao",
    "吉安": "Ji'an",
    "西安": "Xi'an",
    "咸阳": "Xianyang",
    "宝鸡": "Baoji",
    "延安": "Yan'an",
    "榆林": "Yulin",
    "汉中": "Hanzhong",
    "太原": "Taiyuan",
    "大同": "Datong",
    "临汾": "Linfen",
    "运城": "Yuncheng",
    "晋中": "Jinzhong",
    "长治": "Changzhi",
    "沈阳": "Shenyang",
    "大连": "Dalian",
    "鞍山": "Anshan",
    "抚顺": "Fushun",
    "本溪": "Benxi",
    "营口": "Yingkou",
    "长春": "Changchun",
    "吉林": "Jilin",
    "四平": "Siping",
    "通化": "Tonghua",
    "延边": "Yanbian",
    "哈尔滨": "Harbin",
    "齐齐哈尔": "Qiqihar",
    "牡丹江": "Mudanjiang",
    "佳木斯": "Jiamusi",
    "大庆": "Daqing",
    "昆明": "Kunming",
    "大理": "Dali",
    "丽江": "Lijiang",
    "西双版纳": "Xishuangbanna",
    "曲靖": "Qujing",
    "贵阳": "Guiyang",
    "遵义": "Zunyi",
    "安顺": "Anshun",
    "六盘水": "Liupanshui",
    "毕节": "Bijie",
    "兰州": "Lanzhou",
    "天水": "Tianshui",
    "嘉峪关": "Jiayuguan",
    "酒泉": "Jiuquan",
    "张掖": "Zhangye",
    "海口": "Haikou",
    "三亚": "Sanya",
    "儋州": "Danzhou",
    "琼海": "Qionghai",
    "南宁": "Nanning",
    "桂林": "Guilin",
    "柳州": "Liuzhou",
    "北海": "Beihai",
    "玉林": "Yulin",
    "呼和浩特": "Hohhot",
    "包头": "Baotou",
    "鄂尔多斯": "Ordos",
    "赤峰": "Chifeng",
    "呼伦贝尔": "Hulunbuir",
    "乌鲁木齐": "Urumqi",
    "喀什": "Kashgar",
    "吐鲁番": "Turpan",
    "阿克苏": "Aksu",
    "伊宁": "Yining",
    "拉萨": "Lhasa",
    "日喀则": "Shigatse",
    "林芝": "Nyingchi",
    "昌都": "Qamdo",
    "银川": "Yinchuan",
    "石嘴山": "Shizuishan",
    "吴忠": "Wuzhong",
    "固原": "Guyuan",
    "西宁": "Xining",
    "格尔木": "Golmud",
    "玉树": "Yushu",
    "海东": "Haidong",
    "台北": "Taipei",
    "高雄": "Kaohsiung",
    "台中": "Taichung",
    "台南": "Tainan",
    "新竹": "Hsinchu",
    "基隆": "Keelung",
    
    
    # Theme Names - MOVED TO EN_TO_CN

}

# English name to Chinese (for when UI/Poster is in Chinese)
EN_TO_CN = {
    "China": "中国",
    "USA": "美国",
    "United States": "美国",
    "Japan": "日本",
    "UK": "英国",
    "United Kingdom": "英国",
    "France": "法国",
    "Germany": "德国",
    "Italy": "意大利",
    "Spain": "西班牙",
    "Australia": "澳大利亚",
    "Canada": "加拿大",
    "South Korea": "韩国",
    "Singapore": "新加坡",
    "India": "印度",
    "Russia": "俄罗斯",
    "Brazil": "巴西",
    "Mexico": "墨西哥",
    "Netherlands": "荷兰",
    "Belgium": "比利时",
    "Switzerland": "瑞士",
    "Austria": "奥地利",
    "Portugal": "葡萄牙",
    "Greece": "希腊",
    "Turkey": "土耳其",
    "UAE": "阿联酋",
    "United Arab Emirates": "阿联酋",
    "Thailand": "泰国",
    "Vietnam": "越南",
    "Indonesia": "印度尼西亚",
    "Malaysia": "马来西亚",
    "Philippines": "菲律宾",
    "Egypt": "埃及",
    "South Africa": "南非",
    "Morocco": "摩洛哥",
    "Argentina": "阿根廷",
    "Chile": "智利",
    "Colombia": "哥伦比亚",
    "Peru": "秘鲁",
    "New Zealand": "新西兰",
    "Ireland": "爱尔兰",
    "Sweden": "瑞典",
    "Norway": "挪威",
    "Denmark": "丹麦",
    "Finland": "芬兰",
    "Poland": "波兰",
    "Czech Republic": "捷克",
    "Hungary": "匈牙利",
    "Israel": "以色列",
    "Saudi Arabia": "沙特阿拉伯",
    "Qatar": "卡塔尔",
    "Kenya": "肯尼亚",
    "Nigeria": "尼日利亚",
    "Pakistan": "巴基斯坦",
    "Bangladesh": "孟加拉国",
    "Sri Lanka": "斯里兰卡",
    "Nepal": "尼泊尔",
    
    # Common Cities
    "New York City": "纽约",
    "London": "伦敦",
    "Paris": "巴黎",
    "Tokyo": "东京",
    "Guangzhou": "广州",
    "Shenzhen": "深圳",
    "Beijing": "北京",
    "Shanghai": "上海",

    # Theme Names
    "Feature-Based Shading": "特征着色",
    "Japanese Ink": "日式水墨",
    "Midnight Blue": "午夜蓝",
    "Terracotta": "陶土色",
    "Autumn": "秋日",
    "Blueprint": "蓝图",
    "Contrast Zones": "高对比度",
    "Copper Patina": "铜绿",
    "Forest": "森林",
    "Gradient Roads": "渐变道路",
    "Monochrome Blue": "单色蓝",
    "Neon Cyberpunk": "霓虹赛博",
    "Noir": "诺尔黑白",
    "Ocean": "海洋",
    "Pastel Dream": "蜡笔梦幻",
    "Sunset": "日落",
    "Warm Beige": "温暖米色",
}

# Add inverse mappings to ensure completeness
for k, v in CN_TO_EN.items():
    if v not in EN_TO_CN:
        EN_TO_CN[v] = k

# Expose helpers
__all__ = [
    'CITIES', 'get_countries', 'get_provinces', 'get_cities', 
    'get_city_full_name', 'translate', 'get_country_key',
    'get_manual_coordinates'
]

# Manual overrides for city centers to ensure logical centering (e.g. Tiananmen for Beijing)
CITY_CENTERS = {
    "北京": (39.9042, 116.4074),
    "Beijing": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "Shanghai": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "Guangzhou": (23.1291, 113.2644),
    "深圳": (22.5422, 114.0579),
    "Shenzhen": (22.5422, 114.0579),
    "杭州": (30.2741, 120.1551),
    "Hangzhou": (30.2741, 120.1551),
    "成都": (30.6570, 104.0660),
    "Chengdu": (30.6570, 104.0660),
    "南京": (32.0603, 118.7969),
    "Nanjing": (32.0603, 118.7969),
    "武汉": (30.5928, 114.3055),
    "Wuhan": (30.5928, 114.3055),
    "西安": (34.3416, 108.9398),
    "Xi'an": (34.3416, 108.9398),
    "苏州": (31.2990, 120.5853),
    "Suzhou": (31.2990, 120.5853),
    "重庆": (29.5630, 106.5516),
    "Chongqing": (29.5630, 106.5516),
    "天津": (39.1255, 117.1901),
    "Tianjin": (39.1255, 117.1901),
    "香港": (22.3193, 114.1694),
    "Hong Kong": (22.3193, 114.1694),
    "台北": (25.0330, 121.5654),
    "Taipei": (25.0330, 121.5654),
    "New York City": (40.7128, -74.0060),
    "纽约": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "伦敦": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "巴黎": (48.8566, 2.3522),
    "Tokyo": (35.6895, 139.6917),
    "东京": (35.6895, 139.6917),
}

def get_manual_coordinates(city_name):
    """Return manual coordinates if available, else None."""
    if not city_name:
        return None
    return CITY_CENTERS.get(city_name)

def translate(text, target_lang='en'):
    """
    Simple translation helper.
    target_lang: 'en' or 'cn'
    """
    if not text:
        return text
        
    if target_lang == 'en':
        # If text is already in CN_TO_EN keys (Chinese), return the English value
        return CN_TO_EN.get(text, text)
    
    if target_lang == 'cn':
        # If text is in EN_TO_CN keys (English), return the Chinese value
        return EN_TO_CN.get(text, text)
    
    return text

def get_countries(lang='en'):
    """Return list of countries in the target language."""
    countries = []
    for country_key in sorted(CITIES.keys()):
        countries.append(translate(country_key, lang))
    return sorted(list(set(countries)))

def get_country_key(name):
    """Map a localized name back to the CITIES dictionary key."""
    # Check if it's already a key
    if name in CITIES:
        return name
    # Check if it's an English name that needs to be Chinese key
    cn_name = EN_TO_CN.get(name)
    if cn_name in CITIES:
        return cn_name
    # Check if it's a Chinese name that needs to be English key
    en_name = CN_TO_EN.get(name)
    if en_name in CITIES:
        return en_name
    return name

def get_provinces(country_name, lang='en'):
    """Return sorted list of provinces/states for a given country in target language."""
    country_key = get_country_key(country_name)
    if country_key in CITIES:
        # Translate provinces to target lang
        provinces = [translate(p, lang) for p in CITIES[country_key].keys()]
        return sorted(provinces)
    return []

def get_cities(country_name, province_name, lang='en'):
    """Return sorted list of cities in target language."""
    country_key = get_country_key(country_name)
    # To find the province key, we might need to map it back if it was translated
    # For now, let's assume provincial keys in CITIES are what we search against
    # If the province_name is translated, we need to find the original key
    province_key = province_name
    if country_key in CITIES:
        # Check if province_name is a direct key
        if province_name not in CITIES[country_key]:
            # Try to find the key that translates to province_name
            for p_key in CITIES[country_key].keys():
                if translate(p_key, lang) == province_name:
                    province_key = p_key
                    break
        
        if province_key in CITIES[country_key]:
            cities = [translate(c, lang) for c in CITIES[country_key][province_key]]
            return sorted(cities)
    return []

def search_cities(query):
    """
    Search for cities matching the query (checks both Native and English names).
    Returns list of tuples: (city, province, country)
    """
    if not query or len(query) < 2:
        return []
    
    query = query.lower()
    results = []
    
    for country, provinces in CITIES.items():
        country_en = CN_TO_EN.get(country, "").lower()
        for province, cities in provinces.items():
            for city in cities:
                city_en = CN_TO_EN.get(city, "").lower()
                # Match against native name or English name
                if query in city.lower() or (city_en and query in city_en):
                    results.append((city, province, country))
    
    # Sort by city name
    return sorted(results, key=lambda x: x[0])[:20]

def get_city_full_name(city, province, country, target_lang=None):
    """
    Return formatted full name.
    If target_lang is provided ('en' or 'cn'), translates components.
    """
    if target_lang:
        city = translate(city, target_lang)
        province = translate(province, target_lang)
        country = translate(country, target_lang)

    if province == city:  # Direct-controlled municipalities
        return f"{city}, {country}"
    return f"{city}, {province}, {country}"
