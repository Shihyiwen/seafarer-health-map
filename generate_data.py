"""
船員健康風險地圖 — 模擬資料產生器
Seafarer Health Risk Map — synthetic data generator (seed fixed, reproducible)

全部為模擬資料，不含任何真實船舶、船員或公司資料。
港口醫療分級為示意性假設，非官方評等。
"""
import csv, json, math, random
from datetime import date, timedelta

random.seed(20261130)

# ---------- 航線（經緯度 [lon, lat] 簡化航路點）----------
ROUTES = {
    "R1": {"name": "澳洲東岸→台灣", "en": "E. Australia → Taiwan", "ships": 10,
           "pts": [[151.8,-32.9],[154.5,-25],[153.5,-14],[150,-8],[140,2],[128,12],[121.5,21],[120.3,22.6]]},
    "R2": {"name": "西澳→中國北方", "en": "W. Australia → N. China", "ships": 8,
           "pts": [[118.6,-20.3],[116,-12],[115.8,-8.9],[117.8,-4],[119.3,0],[122,4.5],[127,6],[127,13],[123.5,22],[123.5,30],[121.5,34.5],[120.3,36.1]]},
    "R3": {"name": "巴西→中國（經好望角）", "en": "Brazil → China via Cape", "ships": 7,
           "pts": [[-40.2,-20.3],[-25,-28],[0,-34],[20,-37],[40,-35],[70,-22],[92,-5],[98,4],[103.8,1.2],[107,5],[112,12],[117,20],[119.8,25],[122.5,31],[120.3,36.1]]},
    "R4": {"name": "印尼加里曼丹→台中", "en": "Kalimantan → Taichung", "ships": 8,
           "pts": [[114.6,-3.6],[109.5,-2.5],[107.5,2],[110,8],[114,15],[118.5,21],[120.5,24.3]]},
    "R5": {"name": "南非→台灣（經麻六甲）", "en": "South Africa → Taiwan", "ships": 4,
           "pts": [[32.1,-28.8],[50,-28],[80,-12],[95,2],[98,4],[103.8,1.2],[107,5],[112,12],[117,20],[120.3,22.6]]},
    "R6": {"name": "加拿大溫哥華→韓國（北太平洋）", "en": "Vancouver → Korea (N. Pacific)", "ships": 3,
           "pts": [[-123.2,49.2],[-130,50.5],[-150,52.5],[-170,52],[175,48.5],[160,43],[145,37],[135,33.5],[129,35.1]]},
    "R7": {"name": "幾內亞鋁土礦→中國（經好望角）", "en": "Guinea bauxite → China", "ships": 4,
           "pts": [[-14.6,10.4],[-17,6],[-10,-5],[0,-15],[10,-28],[18,-36],[30,-37],[50,-32],[80,-15],[92,0],[98,4],[103.8,1.2],[107,5],[112,12],[117,20],[119.8,25],[122.5,31],[120.3,36.1]]},
    "R8": {"name": "波斯灣（沙烏地）→台灣", "en": "Persian Gulf → Taiwan", "ships": 3,
           "pts": [[49.3,27.4],[51.5,26.7],[54.5,26.3],[56.4,26.5],[57.5,25.2],[60,23],[64,20],[73,10],[79,5.6],[86,5.8],[95,5.8],[98,4],[103.8,1.2],[107,5],[112,12],[117,20],[120.3,22.6]]},
}

# ---------- 戰爭風險列名區域（JWC JWLA-035, 2026-09-16；海域多邊形為簡化示意）----------
LISTED_SEA = {
    "印度洋北部／亞丁灣／紅海南部／波斯灣／阿曼灣": [[34,25.5],[38.5,25.5],[48,30.5],[50.5,30.2],[57,27.5],[61.6,25.2],[65,25.32],[65,10.8],[60.25,10.8],[48.75,-6.75],[41.57,-1.67],[43.2,11.5],[38,18],[34,25.5]],
    "幾內亞灣": [[1.2,6.1],[3,-0.67],[8.7,-0.67],[9.6,3.5],[8.6,4.6],[6,4.3],[4.5,6.3],[3,6.4],[1.2,6.1]],
    "黑海北部及亞速海": [[29.5,45.6],[31,44.5],[33.5,44.2],[36,44.6],[38.5,44.5],[39.8,46.8],[37.5,47.2],[35,46.3],[33,46.2],[30.7,46.5],[29.5,45.6]],
    "德爾加杜角（莫三比克）": [[40.3,-10.3],[40.6,-10.2],[40.85,-13.5],[40.5,-13.5],[40.3,-10.3]],
}
LISTED_COUNTRIES = ["Benin","Djibouti","Eritrea","Libya","Nigeria","Somalia","Sudan","Togo","Bahrain","Iran","Iraq","Israel",
                    "Kuwait","Lebanon","Oman","Qatar","Saudi Arabia","Syria","United Arab Emirates","Yemen","Venezuela"]


def in_poly(lon, lat, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def listed_area(lon, lat):
    for k, p in LISTED_SEA.items():
        if in_poly(lon, lat, p): return k
    return ""

# ---------- 港口與醫療能量分級（示意假設）----------
# A = 港口鄰近具急重症能力之醫學中心；B = 區域醫院（可穩定病況，重症需再轉送）；C = 僅診所/基本醫療
PORTS_RAW = """
高雄 Kaohsiung|120.27|22.61|A||||D
台中 Taichung|120.51|24.29|A||||
青島 Qingdao|120.32|36.07|A||||
釜山 Busan|129.04|35.10|A||||
新加坡 Singapore|103.82|1.26|A||||D
馬尼拉 Manila|120.96|14.59|A||||D
紐卡索 Newcastle|151.78|-32.92|A||||
布里斯本 Brisbane|153.17|-27.38|A||||
德班 Durban|31.03|-29.87|A||||
開普敦 Cape Town|18.43|-33.91|A||||
伊莉莎白港 Gqeberha|25.62|-33.96|A||||
可倫坡 Colombo|79.85|6.95|A||||D
孟買 Mumbai|72.85|18.95|A||M||D
溫哥華 Vancouver|-123.11|49.29|A||||
橫濱 Yokohama|139.64|35.45|A||||
香港 Hong Kong|114.17|22.30|A||||
上海 Shanghai|121.49|31.23|A||||
里約 Rio de Janeiro|-43.18|-22.89|A|||YF|D
黑德蘭港 Port Hedland|118.58|-20.31|B||||
理查茲灣 Richards Bay|32.07|-28.80|B||m||
維多利亞 Vitória|-40.29|-20.32|B|||YF|D
望加錫 Makassar|119.41|-5.13|B||m||D
達爾文 Darwin|130.84|-12.46|B||||
路易港 Port Louis|57.50|-20.16|B||||
關島 Guam|144.66|13.44|B||||
納卯 Davao|125.63|7.07|B||m||D
胡志明市 Ho Chi Minh|106.72|10.77|B||||D
布萊爾港 Port Blair|92.73|11.62|B||M||D
巴里巴板 Balikpapan|116.83|-1.27|B||M||D
科迪亞克 Kodiak|-152.40|57.79|B||||
喀拉蚩 Karachi|66.98|24.85|B||M||D
沃爾維斯灣 Walvis Bay|14.50|-22.95|B||||
馬布多 Maputo|32.57|-25.97|B||M||D
達卡 Dakar|-17.43|14.69|B||M|YF|
柯那克里 Conakry|-13.71|9.51|B||M|YF|
阿必尚 Abidjan|-4.01|5.30|B||M|YF|D
拉哥斯 Lagos|3.40|6.45|B|L|M|YF|
吉布地 Djibouti|43.14|11.60|B|L|M||D
達曼 Dammam|50.10|26.50|A|L|||
馬斯喀特 Muscat|58.59|23.62|A|L|||
富查伊拉 Fujairah|56.36|25.12|B|L|||
塞拉萊 Salalah|54.00|16.95|B|L|||
莫爾斯比港 Port Moresby|147.15|-9.47|C||M||D
荷尼阿拉 Honiara|159.95|-9.43|C||M||D
荷蘭港 Dutch Harbor|-166.54|53.89|C||||
馬林達 Samarinda|117.15|-0.50|C||M||D
馬任 Banjarmasin|114.59|-3.32|C||M||D
聖海倫那 St Helena|-5.72|-15.93|C||||
坎薩爾 Kamsar|-14.60|10.40|C||M|YF|
拉斯海爾 Ras Al-Khair|49.22|27.48|C|L|||
"""
PORTS = []
for line in PORTS_RAW.strip().splitlines():
    n, lo, la, t, li, ma, yf, de = line.split("|")
    PORTS.append({"name": n, "lon": float(lo), "lat": float(la), "tier": t, "listed": li == "L",
                  "malaria": {"M": "有", "m": "低/局部"}.get(ma, ""), "yf": yf == "YF", "dengue": de == "D"})

SPEED_KN = 12.5      # 散裝船平均航速（假設）
ROUTE_FACTOR = 1.15  # 大圓距離→實際航程修正

CATS = [  # key, 中文, ICD-10, 基礎權重, 嚴重度機率 [1,2,3,4]
    ("MSK","肌肉骨骼","M00–M99",19,[.45,.35,.17,.03]),
    ("INJ","外傷","S00–T98",18,[.30,.32,.25,.13]),
    ("SKN","皮膚","L00–L99",14,[.60,.32,.07,.01]),
    ("GI","腸胃／腹部","K20–K93, R10",12,[.35,.38,.20,.07]),
    ("RSP","呼吸道","J00–J99",8,[.40,.40,.16,.04]),
    ("DEN","牙科","K00–K14",7,[.20,.35,.43,.02]),
    ("CVD","心血管","I00–I99",6,[.05,.30,.35,.30]),
    ("PSY","精神／心理","F00–F99",5,[.15,.45,.30,.10]),
    ("URO","泌尿","N00–N99",4,[.15,.40,.35,.10]),
    ("INF","感染／發燒","A00–B99, R50",4,[.25,.45,.22,.08]),
    ("EYE","眼科","H00–H59",3,[.35,.40,.22,.03]),
]
SEV_LABEL = {1:"1 輕微—船上處置",2:"2 中度—需TMAS諮詢",3:"3 重度—需岸上就醫",4:"4 危急—需立即後送"}
RANKS = [("甲板幹部","Deck officer",.16),("甲板普通船員","Deck rating",.30),("輪機幹部","Engine officer",.14),
         ("輪機普通船員","Engine rating",.28),("廚務","Galley",.12)]


def hav_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))


def hours_to_care(lon, lat, tiers=("A","B"), excl_listed=False):
    best = None
    for p in PORTS:
        name, plon, plat, t = p["name"], p["lon"], p["lat"], p["tier"]
        if t not in tiers: continue
        if excl_listed and p["listed"]: continue
        nm = hav_km(lon, lat, plon, plat) / 1.852 * ROUTE_FACTOR
        h = nm / SPEED_KN
        if best is None or h < best[0]:
            best = (h, name, t)
    return best


def seg_lengths(pts):
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        lon_b = b[0]
        if abs(lon_b - a[0]) > 180:  # antimeridian
            lon_b = lon_b + 360 if lon_b < a[0] else lon_b - 360
        out.append(hav_km(a[0], a[1], lon_b, b[1]))
    return out


def interp(a, b, f):
    lon_b = b[0]
    if abs(lon_b - a[0]) > 180:
        lon_b = lon_b + 360 if lon_b < a[0] else lon_b - 360
    lon = a[0] + (lon_b - a[0]) * f
    if lon > 180: lon -= 360
    if lon < -180: lon += 360
    return lon, a[1] + (b[1] - a[1]) * f


def pick(weights):
    r, acc = random.random() * sum(weights), 0
    for i, w in enumerate(weights):
        acc += w
        if r <= acc: return i
    return len(weights) - 1

# ---------- 航段可近性（供地圖上色）----------
route_out = []
for rid, r in ROUTES.items():
    samples = []
    lens = seg_lengths(r["pts"])
    for (a, b), L in zip(zip(r["pts"][:-1], r["pts"][1:]), lens):
        n = max(2, int(L / 150))
        for k in range(n):
            lon, lat = interp(a, b, k / n)
            h, port, tier = hours_to_care(lon, lat)
            la_ = listed_area(lon, lat)
            hx = hours_to_care(lon, lat, excl_listed=True)[0] if la_ else h
            samples.append([round(lon, 3), round(lat, 3), round(h, 1), 1 if la_ else 0, round(hx, 1)])
    lon, lat = r["pts"][-1]
    h = hours_to_care(lon, lat)[0]; la_ = listed_area(lon, lat)
    samples.append([lon, lat, round(h, 1), 1 if la_ else 0, round(hours_to_care(lon, lat, excl_listed=True)[0] if la_ else h, 1)])
    route_out.append({"id": rid, "name": r["name"], "en": r["en"], "ships": r["ships"],
                      "km": round(sum(lens)), "samples": samples})

# ---------- 船隊與事件 ----------
CREW = 21
vessels = []
for rid, r in ROUTES.items():
    for i in range(r["ships"]):
        vessels.append({"vessel": f"MV-{rid}{i+1:02d}", "route": rid})

RATE = 1.75  # 每船年需紀錄之醫療事件（假設）
start, end = date(2023,1,1), date(2025,12,31)
days = (end - start).days + 1
events = []
eid = 0
for v in vessels:
    n = sum(1 for _ in range(3*100) if random.random() < RATE/100)
    r = ROUTES[v["route"]]
    lens = seg_lengths(r["pts"])
    for _ in range(n):
        eid += 1
        d = start + timedelta(days=random.randrange(days))
        ri = pick([x[2] for x in RANKS])
        rank = RANKS[ri]
        w = [c[3] for c in CATS]
        if rank[0] in ("甲板普通船員", "輪機普通船員"):
            w[1] *= 1.6; w[0] *= 1.2
        if rank[0] == "廚務":
            w[1] *= 1.3; w[2] *= 1.3
        if rank[0] in ("甲板幹部", "輪機幹部"):
            w[6] *= 1.8  # 幹部年齡較高，心血管較多（假設）
        if v["route"] == "R7": w[9] *= 3   # 西非瘧疾／黃熱病流行區（假設）
        if v["route"] == "R4": w[9] *= 2   # 加里曼丹瘧疾（假設）
        ci = pick(w)
        cat = CATS[ci]
        sev = pick(cat[4]) + 1
        in_port = random.random() < 0.15
        if in_port:
            lon, lat = r["pts"][random.choice([0, -1])]
            lon += random.uniform(-0.15, 0.15); lat += random.uniform(-0.15, 0.15)
        else:
            si = pick(lens)
            lon, lat = interp(r["pts"][si], r["pts"][si+1], random.random())
            lon += random.uniform(-0.6, 0.6); lat += random.uniform(-0.6, 0.6)
        h, near_port, tier = hours_to_care(lon, lat)
        h_x = hours_to_care(lon, lat, excl_listed=True)[0]
        la = listed_area(lon, lat)
        if in_port: h = min(h, 2.0); h_x = h
        h_eff = h_x if la else h   # 列名區域內，列名國港口視為受限，改以非列名港口計算
        # 處置
        div_h, heli, cost = 0.0, 0, 0
        if sev == 1:
            disp = "船上自行處置"
        elif sev == 2:
            disp = "TMAS遠距諮詢"
        elif sev == 3:
            disp = "靠港就醫" if (in_port or h_eff <= 72) else "偏航送醫"
        else:
            if in_port: disp = "靠港就醫"
            elif h_eff <= 10 and cat[0] in ("CVD", "INJ") and random.random() < .5:
                disp = "直升機後送"; heli = 1
            else:
                disp = "偏航送醫"
        if disp == "偏航送醫":
            div_h = round(h_eff * 2 * random.uniform(.55, .85), 1)  # 偏離原航線之額外航時（來回、部分順路）
        EUR_USD = 1.15  # 2026-11 匯率約略值
        cost = int((div_h * 2200 + heli * 25000) * EUR_USD)  # Faurby et al. 2017 基準情境（歐元）換算美元
        repat = 1 if (sev == 4 and random.random() < .7) or (sev == 3 and random.random() < .25) else 0
        events.append({
            "id": f"E{eid:04d}", "date": d.isoformat(), "year": d.year, "month": d.month,
            "vessel": v["vessel"], "route": v["route"], "rank": rank[0], "dept": rank[1],
            "cat": cat[0], "cat_zh": cat[1], "icd10": cat[2], "severity": sev,
            "at_sea": 0 if in_port else 1, "lon": round(lon, 3), "lat": round(lat, 3),
            "hours_to_care": round(h, 1), "hours_to_care_excl_listed": round(h_x, 1),
            "nearest_capable_port": near_port, "port_tier": tier, "war_listed_area": la,
            "disposition": disp, "diversion_h": div_h, "helicopter": heli,
            "repatriated": repat, "est_cost_usd": cost,
        })

events.sort(key=lambda e: e["date"])
with open("data/events.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(events[0].keys()))
    w.writeheader(); w.writerows(events)
with open("data/ports.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(PORTS[0].keys())); w.writeheader(); w.writerows(PORTS)

payload = {"routes": route_out, "ports": PORTS, "listedSea": [{"name": k, "poly": v} for k, v in LISTED_SEA.items()],
           "listedCountries": LISTED_COUNTRIES,
           "events": events, "vessels": len(vessels), "crew": CREW,
           "cats": [{"key":c[0],"zh":c[1],"icd":c[2]} for c in CATS]}
with open("data/payload.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
print(len(vessels), "vessels;", len(events), "events")
