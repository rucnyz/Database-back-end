from flask import Blueprint, request

from utils import run_sql, wrap_json_for_send

admin = Blueprint('admin', __name__)


# 1. 显示每个商家最热卖的top 3个商品。
# /api/admin/top3_product
# input:base,{""}
# output:base,{"supplier_id","rank","product_id","product_name","sum_quantity"}
@admin.route("/top3_product", methods=['POST'])
def top3_product():
# 获取已有商家数量，进行循环
    getNum = """
            SELECT COUNT(*) as cnt
           from supplier   
            """
    tmp = run_sql(getNum)
    number = int(tmp['cnt'][0])


    for i in range(1, number+1):
        spid = 'S' + i
        top3_product = """
        SELECT TOP 3 s.supplier_id, p.product_id, p.product_name, SUM(o.quantity)
        FROM supplier s , orders o , products p
        WHERE s.supplier_id=o.supplier_id AND p.product_id=o.product_id AND s.supplier='%s'
        GROUP BY s.supplier_id
        ORDER BY SUM(o.quantity) DESC
        """ % spid

        t = run_sql(top3_product)
        column = ['supplier_id', 'product_id', 'product_name',]
        d = {"detail": [dict(zip(column, t[i])) for i in range(len(t))]}



    return


# 2. 给定一个商品，显示售卖此商品价格最低的5个商家。”（商品名字模糊搜索)
# /api/admin/low5_supplier
# input:base,{"key_words"}
# output:base,{"key_words",{"product_id","product_name","supplier_id","supplier_name"{}},{},...,{}}
@admin.route("/low5_supplier", methods=['POST'])
def low5_supplier():


    return


# 3. 显示每个商家的年销售总额。
# /api/admin/annual_sales
# input:base,{"year"}
# output:base,{"year",{"supplier_id","supplier_name","annual_sales"{}},{},...,{}}
@admin.route("/annual_sales", methods=['POST'])
def annual_sales():
    return


# 4.显示每个会员购买次数最多的商品。
# /api/admin/top_product
# input:base,{""}
# output:base,{"customer_id","product_id","product_name","count"}
@admin.route("/top_product", methods=['POST'])
def top_product():
    get_top_product = """
    SELECT o.customer_id, p.product_id, p.product_name, COUNT(*)
    FROM orders o, product p
    WHERE o.product_id = p.product_id AND 
    """
    return


# 5. 显示每个省份会员的平均消费额、最大消费额和最小消费额，并按平均消费额降序排列。
# /api/admin/province_top
# input:base,{""}
# output:base,{"province","average_spending","max_spending","min_spending"}
@admin.route("/province_top", methods=['POST'])
def province_top():
    provinces = ['安徽省', '澳门特别行政区', '北京市', '福建省', '甘肃省', '广东省', '广西壮族自治区', '贵州省', '海南省',
                 '河北省', '河南省', '黑龙江省', '湖北省', '湖南省', '吉林省', '江苏省', '江西省', '辽宁省', '内蒙古自治区',
                 '宁夏回族自治区', '青海省', '山东省', '山西省', '陕西省', '上海市', '四川省', '台湾省', '天津市', '西藏自治区',
                 '香港特别行政区', '新疆维吾尔自治区', '云南省', '浙江省', '重庆市']
    province_top = []
    for i in provinces:
        get_province_top = """
        SELECT '%s' province, AVG(o.price_sum) avg, MAX(o.price_sum) max, MIN(o.price_sum) min
        FROM orders o
        WHERE o.receive_address LIKE '%s';
        """ % i
        t = run_sql(get_province_top)
        province_top.append(t)
    column = ["province", "average", "max", "min"]
    # TOTODO 降序排列
    d = {"detail": [dict(zip(column, province_top[i])) for i in range(len(province_top))]}
    return wrap_json_for_send(d, "successful")
