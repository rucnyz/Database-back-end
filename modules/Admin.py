from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from utils import run_sql, wrap_json_for_send

admin = Blueprint('admin', __name__)
db = SQLAlchemy()

#/api/admin/login
# input: base, {"adminName":"xxx", "password":"xxx"}
# output:base
@admin.route("/login", methods =['POST'])
def login():
    admin_name = request.json['adminName']
    password = request.json['password']
    message = None

    login = """
    SELECT admin_id
    FROM admin
    WHERE admin_name=:admin_name AND password=:password
    """

    run_sql(login,{"admin_name":admin_name,
                   "password":password})

    admin_info = {"admin_id": "A000000001"}
    statuscode = "Successful"
    return wrap_json_for_send(admin_info, statuscode, message = message)


# 1. 显示每个商家最热卖的top 3个商品。 # zzm  # hcy修改【lsy已测试】
# /api/admin/top3_product
# input:base,{""}
# output:base,{"supplier_id","product_id","product_name","sum_quantity"}
@admin.route("/top3_product", methods=['POST'])
def top3_product():
    # 获取已有商家数量，进行循环
    get_num = """
    SELECT COUNT(*) as cnt
    FROM supplier
    """
    tmp = run_sql(get_num)
    number = int(tmp[0]['cnt'])
    final_info = []
    for i in range(1, number + 1):
        spid = 'S' + str(i).zfill(9)
        top3_product = """
        SELECT TOP 3 s.supplier_id, p.product_id, p.product_name, SUM(o.quantity)
        FROM supplier s , orders o , product p
        WHERE s.supplier_id=o.supplier_id AND p.product_id=o.product_id AND s.supplier_id=:supplier_id
        GROUP BY s.supplier_id, p.product_id, p.product_name
        ORDER BY SUM(o.quantity) DESC
        """
        tuple_tmp = run_sql(top3_product, {"supplier_id": spid})
        column = ['supplier_id', 'product_id', 'product_name', 'sum_quantity']
        tmp_info = [dict(zip(column, tuple_tmp[i].values())) for i in range(len(tuple_tmp))]
        final_info.append(tmp_info)

    d = {"detail": final_info}

    return wrap_json_for_send(d, "successful")


# 2. 给定一个商品，显示售卖此商品价格最低的5个商家。”（商品名字模糊搜索) # zzm   hcy修改【lsy已测试】
# /api/admin/low5_supplier
# input:base,{"keywords"}
# output:base,{"keywords",'detail': [{"price","product_id","product_name","supplier_id","supplier_name"{}},{},...,{}]}
@admin.route("/low5_supplier", methods=['POST'])
def low5_supplier():
    key_words = request.json['keywords']
    key_words_vague = '%'+key_words+'%'
    get_low5_supplier = """
    SELECT TOP 5 p.price, p.product_id, p.product_name, s.supplier_id, s.supplier_name
    FROM product p, supplier s
    WHERE p.supplier_id=s.supplier_id AND product_name LIKE :vague
    ORDER BY price 
    """
    t = run_sql(get_low5_supplier, {"vague": key_words_vague})
    column = ["price", "product_id", "product_name", "supplier_id", "supplier_name"]
    d = {'keywords': key_words, 'detail': [dict(zip(column, t[i].values())) for i in range(len(t))]}

    return wrap_json_for_send(d, "successful")


# 3. 显示每个商家的年销售总额。 # hcy 【lsy已测试】
# /api/admin/annual_sales
# input:base,{"year"}
# output:base, {"year":,"suppliers": list[{"supplier_id","supplier_name","annual_sales"}]}
@admin.route("/annual_sales", methods=['POST'])
def annual_sales():
    # 获取年份，进行循环
    get_years = """
    SELECT DISTINCT DatePart(yyyy, orderdate)
    from orders 
    """
    list_year = run_sql(get_years)
    list_year = [i[''] for i in list_year]
    get_annual_sales = """
    SELECT DatePart(yyyy, o.orderdate) year, s.supplier_id, s.supplier_name, round(SUM(o.price_sum),2) annual_sales
    FROM supplier s, orders o
    WHERE s.supplier_id=o.supplier_id
    GROUP BY s.supplier_id, s.supplier_name, DatePart(yyyy, o.orderdate)
    """
    t = run_sql(get_annual_sales)

    l_all = []
    for item in list_year:
        dtmp = {}
        ltmp = []
        for item_ in t:
            if item_['year'] == item:
                ltmp.append(item_)
        dtmp['year'] = item
        dtmp['suppliers'] = ltmp
        l_all.append(dtmp)

    d = {"detail": l_all}
    return wrap_json_for_send(d, "successful")


# 4.显示每个会员购买次数最多的商品。  # lsy【已测试】
# /api/admin/top_product
# input:base,{""}
# output:base,{"customer_id","product_id","product_name","top_num"}
@admin.route("/top_product", methods=['POST'])
def top_product():
    get_top_product = """
    SELECT o_c.customer_id, o_c.product_id, p.product_name, MAX(pc_count) top_num
    FROM product p, 
    (SELECT customer_id, product_id, COUNT(*) pc_count
    FROM orders
    GROUP BY customer_id, product_id) o_c
    WHERE p.product_id = o_c.product_id
    GROUP BY  o_c.customer_id, o_c.product_id, p.product_name;
    """
    t = run_sql(get_top_product)
    column = ["customer_id", "product_id", "product_name", "top_num"]
    d = {"detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")


# 5. 显示每个省份会员的平均消费额、最大消费额和最小消费额，并按平均消费额降序排列。   # lsy【已测试】
# /api/admin/province_top
# input:base,{""}
# output:base,{"province", "count", "average_spending","max_spending","min_spending"}
# 可以加功能：以不同方式排序
@admin.route("/province_top", methods=['POST'])
def province_top():
    provinces = ['安徽省', '澳门特别行政区', '北京市', '福建省', '甘肃省', '广东省', '广西壮族自治区', '贵州省', '海南省',
                 '河北省', '河南省', '黑龙江省', '湖北省', '湖南省', '吉林省', '江苏省', '江西省', '辽宁省', '内蒙古自治区',
                 '宁夏回族自治区', '青海省', '山东省', '山西省', '陕西省', '上海市', '四川省', '台湾省', '天津市', '西藏自治区',
                 '香港特别行政区', '新疆维吾尔自治区', '云南省', '浙江省', '重庆市']
    province_top = []
    for i in provinces:
        vague = i + '%'
        print(vague)
        get_province_top = """
        SELECT :province province, round(ISNULL(COUNT(*),0), 0) count, round(ISNULL(AVG(price_sum),0),2) avg, round(ISNULL(MAX(price_sum),0),2) max, round(ISNULL(MIN(price_sum),0),2) min
        FROM (SELECT o.price_sum
                FROM orders o
	            WHERE o.receive_address LIKE :vague) AS pvs;
        """
        t = run_sql(get_province_top, {"province": i, "vague": vague})
        province_top.append(t)
    column = ["province", "count", "average", "max", "min"]
    province_top = sorted(province_top, key=lambda province_top: [x['avg'] for x in province_top], reverse=True)
    # toTODO 降序排列
    d = {"detail": [dict(zip(column, province_top[i])) for i in range(len(province_top))]}
    return wrap_json_for_send(d, "successful")
