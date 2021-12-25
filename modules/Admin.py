from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from utils import run_sql, wrap_json_for_send

admin = Blueprint('admin', __name__)
db = SQLAlchemy()


# 管理员登录
# /api/admin/login
# input: base, {"adminName":"xxx", "password":"xxx"}
# output:base
@admin.route("/login", methods = ['POST'])
def login():
    admin_name = request.json['adminName']
    password = request.json['password']
    message = None

    login = """
    SELECT admin_id adminId
    FROM admin
    WHERE admin_name=:admin_name AND admin_password=:password
    """

    admin_info = run_sql(login, {"admin_name": admin_name,
                                 "password": password})[0]

    statuscode = "successful"
    return wrap_json_for_send(admin_info, statuscode, message = message)


# 1. 显示每个商家最热卖的top 3个商品。 # zzm  # hcy修改【lsy已测试】
# /api/admin/top3_product
# input:base,{""}
# output:base,{"supplier_id","product_id","product_name","sum_quantity"}
@admin.route("/top3_product", methods = ['POST', 'GET'])
def top3_product():
    # 获取已有商家数量，进行循环
    get_id = """
    SELECT supplier_id
    FROM supplier
    """
    tmp = run_sql(get_id)
    final_info = []
    for i in range(len(tmp)):
        splid = tmp[i]['supplier_id']
        top3_product = """
        SELECT TOP 3 supplier_name, product_id, product_name, sum_quantity
        FROM SUM_QUANTITY
        WHERE supplier_id = :supplier_id
        ORDER BY sum_quantity DESC;
        """
        tuple_tmp = run_sql(top3_product, {"supplier_id": splid})
        column = ['supplierName', 'productId', 'productName', 'sumQuantity']
        tmp_info = [dict(zip(column, tuple_tmp[i].values())) for i in range(len(tuple_tmp))]
        final_info.append(tmp_info)

    d = {"details": final_info}

    return wrap_json_for_send(d, "successful")


# 2. 给定一个商品，显示售卖此商品价格最低的5个商家。”（商品名字模糊搜索) # zzm   hcy修改【lsy已测试】
# /api/admin/low5_supplier
# input:base,{"keywords"}
# output:base,{"keywords",'details': [{"price","product_id","product_name","supplier_id","supplier_name"{}},{},...,{}]}
@admin.route("/low5_supplier", methods = ['POST'])
def low5_supplier():
    key_words = request.json['keywords']
    key_words_vague = '%' + key_words + '%'
    get_low5_supplier = """
    SELECT TOP 5 p.price, p.product_id, p.product_name, s.supplier_id, s.supplier_name
    FROM product p, supplier s
    WHERE p.supplier_id=s.supplier_id AND product_name LIKE :vague
    ORDER BY price 
    """
    t = run_sql(get_low5_supplier, {"vague": key_words_vague})
    column = ["price", "productId", "productName", "supplierId", "supplierName"]
    d = {'keywords': key_words, 'details': [dict(zip(column, t[i].values())) for i in range(len(t))]}

    return wrap_json_for_send(d, "successful")


# 3. 显示每个商家的年销售总额。 # hcy 【lsy已测试】[已添加input ID]
# /api/admin/annual_sales
# input:base,{"ID": "xxx"}
# output:base, {details:[{"year":,"suppliers": list[{"supplierId","supplierName","annualSales"}},{}]}
@admin.route("/annual_sales", methods = ['POST'])
def annual_sales():
    id = request.json['ID']
    statuscode = "successful"
    # 获取年份，进行循环
    get_years = """
    SELECT DISTINCT DatePart(yyyy, orderdate)
    from orders 
    """
    list_year = run_sql(get_years)
    list_year = [i[''] for i in list_year]
    get_annual_sales = """
    SELECT DatePart(yyyy, o.orderdate) year, s.supplier_id supplierId, s.supplier_name supplierName, round(SUM(o.price_sum),2) annualSales
    FROM supplier s, orders o
    WHERE s.supplier_id=o.supplier_id
    GROUP BY s.supplier_id, s.supplier_name, DatePart(yyyy, o.orderdate)
    ORDER BY year, annualSales DESC
    """
    t = run_sql(get_annual_sales)

    l_all = []
    for item in list_year:
        dtmp = {}
        ltmp = []
        for item_ in t:
            if item_['year'] == item:
                if id[0] == "A":
                    ltmp.append(item_)
                elif id[0] == "S":
                    if item_['supplierId'] == id:
                        ltmp.append(item_)
        dtmp['year'] = item
        dtmp['suppliers'] = ltmp
        l_all.append(dtmp)

    d = {"details": l_all}
    if id[0] != "S" and id[0] != "A":
        d = {}
        statuscode = "failed"
    return wrap_json_for_send(d, statuscode)


# 4.显示每个会员购买次数最多的商品。  # lsy【已测试】[已添加input ID][hcy 加视图]
# /api/admin/top_product
# input:base,{"ID": "xxx"}
# output:base,{"customer_id","product_id","product_name","top_num"}
@admin.route("/top_product", methods = ['POST', 'GET'])
def top_product():
    id = request.json['ID']
    statuscode = "successful"
    if id[0] == "A":
        get_top_product = """
        SELECT o_c.customer_id customerId, o_c.customer_nickname, o_c.product_id productId, product_name, top_num
        FROM SUM_QUANTITY_EACHCUST_EACHPRO o_c, (SELECT customer_id, MAX(sum_quantity) top_num
                                               FROM SUM_QUANTITY_EACHCUST_EACHPRO
                                               GROUP BY customer_id) AS tmp
        WHERE tmp.top_num=o_c.sum_quantity AND tmp.customer_id=o_c.customer_id
        ORDER BY top_num DESC
        """
        t = run_sql(get_top_product)
        column = ["customerId", "customerName", "productId", "productName", "topNum"]
        d = {"details": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    elif id[0] == "C":
        get_top_product_customer = """
        SELECT o_c.customer_id customerId, o_c.customer_nickname, o_c.product_id productId, product_name, top_num
        FROM SUM_QUANTITY_EACHCUST_EACHPRO o_c, (SELECT customer_id, MAX(sum_quantity) top_num
                                               FROM SUM_QUANTITY_EACHCUST_EACHPRO
                                               GROUP BY customer_id) AS tmp
        WHERE tmp.top_num=o_c.sum_quantity AND tmp.customer_id=o_c.customer_id AND o_c.customer_id = :id
        ORDER BY top_num DESC 
                """
        t = run_sql(get_top_product_customer, {"id": id})
        column = ["customerId", "customerName", "productId", "productName", "topNum"]
        d = {"details": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    else:
        d = {}
        statuscode = "failed"
    return wrap_json_for_send(d, statuscode)


# 5. 显示每个省份会员的平均消费额、最大消费额和最小消费额，并按平均消费额降序排列。   # lsy【已测试】
# /api/admin/province_top
# input:base,{"ID": "xxx"}
# output:base,{"province", "count", "averageSpending","maxSpending","minSpending"}
# 可以加功能：以不同方式排序
@admin.route("/province_top", methods = ['POST', 'GET'])
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
	          WHERE o.receive_address LIKE :vague) AS pvs
	    ORDER BY avg DESC, max DESC 
        """
        t = run_sql(get_province_top, {"province": i, "vague": vague})
        province_top.append(t)
    column = ["province", "count", "average", "max", "min"]
    province_top = sorted(province_top, key = lambda province_top: [x['avg'] for x in province_top], reverse = True)
    # toTODO 降序排列
    d = {"details": [dict(zip(column, province_top[i])) for i in range(len(province_top))]}
    return wrap_json_for_send(d, "successful")


# 6. 显示每个商家消费最高的会员 # hcy [后端已完成][已测试]
# /api/admin/top_customer
# input:base,{"ID": "xxx"}
# output:base,{"details":{"supplierId","supplierName","customerId","sumConsume"},{}}
@admin.route("/top_customer", methods = ['POST'])
def top_customer():
    id = request.json['ID']
    statuscode = "successful"
    if id[0] == "A":
        get_top_customer = """
        SELECT s.supplier_id, s.supplier_name, s.customer_id,s.customer_nickname, sum_consume
        FROM SUM_CONSUME_EACHSUPP_EACHCUST s, (SELECT supplier_id, supplier_name, MAX(sum_consume) max_sum_consume
                                               FROM SUM_CONSUME_EACHSUPP_EACHCUST
                                               GROUP BY supplier_id, supplier_name) AS tmp
        WHERE tmp.max_sum_consume=s.sum_consume AND tmp.supplier_id=s.supplier_id
        ORDER BY max_sum_consume DESC 
        """
        t = run_sql(get_top_customer)
        column = ["supplierId", "supplierName", "customerId", "customerName", "sumConsume"]
        d = {"details": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    elif id[0] == "S":
        get_top_customer_supp = """
                SELECT s.supplier_id, s.supplier_name, s.customer_id,s.customer_nickname, sum_consume
                FROM SUM_CONSUME_EACHSUPP_EACHCUST s, (SELECT supplier_id, supplier_name, MAX(sum_consume) max_sum_consume
                                                       FROM SUM_CONSUME_EACHSUPP_EACHCUST
                                                       GROUP BY supplier_id, supplier_name) AS tmp
                WHERE tmp.max_sum_consume=s.sum_consume AND tmp.supplier_id=s.supplier_id AND s.supplier_id=:id
                """
        t = run_sql(get_top_customer_supp, {"id": id})
        column = ["supplierId", "supplierName", "customerID", "customerName", "sumConsume"]
        d = {"details": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    else:
        d = {}
        statuscode = "failed"
    return wrap_json_for_send(d, statuscode)


# 7. 显示每个会员年消费额。 # hcy [后端已完成][已测试]
# /api/admin/annual_consume
# input:base,{"ID": "xxx"}
# output:base,{"details": [{"year": xxx, "customers": list[{"customerId","annualConsume"}]},{}]}
@admin.route("/annual_consume", methods = ['POST'])
def annual_consume():
    id = request.json['ID']
    statuscode = "successful"
    # 获取年份，进行循环
    get_years = """
    SELECT DISTINCT DatePart(yyyy, orderdate)
    from orders 
    """
    list_year = run_sql(get_years)
    list_year = [i[''] for i in list_year]
    get_annual_consume = """
    SELECT DatePart(yyyy, o.orderdate) year, c.customer_id customerId,c.customer_nickname customerName, round(SUM(o.price_sum),2) annualConsume
    FROM customer c, orders o
    WHERE c.customer_id=o.customer_id
    GROUP BY c.customer_id, DatePart(yyyy, o.orderdate), c.customer_nickname
    ORDER BY annualConsume DESC 
    """
    t = run_sql(get_annual_consume)

    l_all = []
    for item in list_year:
        dtmp = {}
        ltmp = []
        for item_ in t:
            if item_['year'] == item:
                if id[0] == "A":
                    ltmp.append(item_)
                elif id[0] == "C":
                    if item_['customerId'] == id:
                        ltmp.append(item_)
        dtmp['year'] = item
        dtmp['customers'] = ltmp
        l_all.append(dtmp)
    d = {"details": l_all}
    if id[0] != "C" and id[0] != "A":
        d = {}
        statuscode = "failed"
    return wrap_json_for_send(d, statuscode)


# 8. 给定一个商品，显示售卖此商品最多的5个商家。”（商品名字模糊搜索) #hcy [后端已完成][已测试]
# /api/admin/top5_supplier
# input:base,{"keywords"}
# output:base,{"keywords",'details': [{"productId","productName","supplierId","supplierName","sumQuantity"},{},{}]}
@admin.route("/top5_supplier", methods = ['POST'])
def top5_supplier():
    key_words = request.json['keywords']
    key_words_vague = '%' + key_words + '%'
    get_top5_supplier = """
    SELECT TOP 5 product_id, product_name, supplier_id, supplier_name, sum_quantity
    FROM SUM_QUANTITY
    WHERE product_name LIKE :vague
    ORDER BY sum_quantity DESC 
    """
    t = run_sql(get_top5_supplier, {"vague": key_words_vague})
    column = ["productId", "productName", "supplierId", "supplierName", "sumQuantity"]
    d = {'keywords': key_words, 'details': [dict(zip(column, t[i].values())) for i in range(len(t))]}

    return wrap_json_for_send(d, "successful")
