# 数据库函数使用指南
## run_sql
- 函数签名： run_sql(T_sql, param, user)  
- 参数:   
    - T_sql:需要执行的sql语句
    - param：sql语句中需要替换的变量
    - user：执行语句的身份，是"sa", "customer", "supplier", "admin"中的一个
- 特别说明：变量替换时在sql语句内需要带冒号，同时dict的key是冒号之后的内容  
- 返回值： 如果有结果返回结果，没有结果返回None
- 异常： 本函数没有进行异常处理，查询如果有问题会直接导致程序崩溃，请合理try-catch
- 使用例： 以系统管理员身份根据电话查找用户
```python
run_sql("SELECT * FROM customer WHERE   customer_phonenumber=:phonenum",{"phonenum":123456789},"admin")  
```

## run_sqls
- 函数签名：run_sqls(sqlDict, user)  
- 参数：  
    - sqlDict：一个dict，key是需要执行的sql语序，value是sql语句中需要替换的变量  
    - user：执行这些语句的身份  
- 返回值：两个dict,第一个dict中包含了执行成功的语句，key是语句本身（即参数中的T_sql），value是语句的返回值。第二个dict中包含了执行失败的语句，key是语句本身，value是出错原因。  
- 特别说明：这些语句是顺序执行的，并且启用了autocommit,也就是说这些语句的修改会立刻反映到数据库中，所以这样写并不会让一组语句执行的速度变得更快。（如果有这个需要请使用run_trans）另外，这些语句之间的error是独立的，也就是一个或多个语句执行失败并不影响其他所有语句的执行，请谨慎使用。
- 使用例：
```python
run_sqls({"SELECT * FROM supplier":None,
        "SELECT * FROM customer WHERE customer_id=:id":{"id":"C000000001"}},
        "admin")
```


## run_trans
- 函数签名：run_trans(sqlDict, user)  
- 参数：
    - sqlDict：一个dict，key是需要执行的sql语序，value是sql语句中需要替换的变量  
    - user：执行这些语句的身份  
- 返回值：None
- 说明：这些语句是顺序执行的，其中一个失败剩下的都会失败，发生回滚并抛出错误
