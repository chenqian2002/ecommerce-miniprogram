# 开发执行计划状态清单

来源：`ecommerce/DEVELOPMENT_PLAN.md`

> 说明：
> - ✅ = 已完成
> - ⏳ = 待完善 / 待继续
> - ⚠️ = 仍需重点确认

---

## 一、当前已完成项

### 核心能力
- ✅ 登录 / 退出登录
- ✅ 商品浏览与分类
- ✅ 加入购物车、修改数量、删除商品
- ✅ 结算下单
- ✅ 收货地址新增 / 编辑 / 删除 / 默认地址
- ✅ 订单列表 / 订单详情
- ✅ 模拟支付
- ✅ 取消订单 / 确认收货
- ✅ 我的页面与基础入口
- ✅ 页面文案与空态统一
- ✅ 项目日志与总结文档整理

### 体验能力
- ✅ 商品详情页
- ✅ 商品搜索
- ✅ 商品筛选 / 排序
- ✅ 收藏功能（本地版）
- ✅ 设置页 / 关于我们页

---

## 二、仍可继续完善项

### P1：体验增强
- ⏳ 社交分享
- ⏳ 消息通知
- ⏳ 优惠券功能

### P2：可选扩展
- ⏳ 订单评价功能
- ⏳ 真实支付对接（有资质再做）

---

## 三、目前还没做完的功能

### 1. 收藏功能升级
- 当前为本地收藏，未做后端持久化
- 建议后续支持登录用户收藏表、跨设备同步、收藏列表接口

### 2. 搜索功能统一化
- 当前前端可搜索，但主要依赖页面内过滤
- 后续可统一走后端搜索接口，并支持分页、搜索历史

### 3. 社交分享
- 商品分享
- 活动页分享
- 分享回流

### 4. 消息通知
- 订单支付成功通知
- 发货通知
- 状态变更通知

### 5. 优惠券功能
- 领券
- 用券
- 券状态展示
- 结算抵扣

### 6. 订单评价功能
- 完成订单后评价
- 星级评分
- 文本评价

### 7. 真实支付对接
- 微信支付下单
- 支付回调验签
- 幂等处理
- 支付结果同步订单状态

### 8. 后台管理能力
- 商品管理后台
- 订单管理后台
- 发货管理
- 用户管理
- 库存管理

### 9. 图片公网化与上传
- 图片上传接口
- 公网可访问图片存储
- 小程序域名配置

---

## 四、7天冲刺上线计划

### Day 1：主链路总验收
- 登录 / token 校验
- 商品列表正常加载
- 商品详情页可打开
- 搜索可用
- 分类切换正常
- 收藏页可打开
- 设置页 / 关于我们页可打开

#### Day 1 文件级清单

**1. 登录与鉴权**
- `minprogram/pages/login/login.js`
- `minprogram/utils/request.js`
- `backend/app/api/auth.py`
- `backend/app/core/security.py`

检查项：
- 登录后 token 保存正常
- 请求自动带 token
- token 失效后回到登录页
- 未登录访问受保护接口会拒绝

**2. 商品列表页**
- `minprogram/pages/products/products.js`
- `minprogram/pages/products/products.wxml`
- `minprogram/pages/products/products.wxss`
- `backend/app/api/products.py`

检查项：
- 商品列表正常加载
- 分类切换正常
- 排序正常
- 搜索正常
- 空态正常
- 进入详情页正常

**3. 商品详情页**
- `minprogram/pages/product-detail/product-detail.js`
- `minprogram/pages/product-detail/product-detail.wxml`
- `minprogram/pages/product-detail/product-detail.wxss`
- `backend/app/api/products.py`

检查项：
- `productId` 参数正常
- 详情数据展示正常
- 加入购物车可用
- 立即购买流程可走
- 收藏状态正常

**4. 搜索功能**
- `minprogram/pages/products/products.js`
- `backend/app/api/products.py`

检查项：
- 输入框可输入
- 搜索按钮可用
- 清空搜索正常
- 空结果有提示

**5. 分类 / 筛选 / 排序**
- `minprogram/pages/products/products.js`
- `minprogram/pages/products/products.wxml`
- `backend/app/api/products.py`

检查项：
- 分类筛选正常
- 销量排序正常
- 价格排序正常
- 与搜索联动正常

**6. 收藏功能**
- `minprogram/pages/favorites/favorites.js`
- `minprogram/pages/favorites/favorites.wxml`
- `minprogram/pages/favorites/favorites.wxss`
- `minprogram/pages/product-detail/product-detail.js`
- `minprogram/utils/storage.js`

检查项：
- 收藏可添加 / 取消
- 收藏页可读取
- 跳转详情正常
- 清缓存后不崩溃

**7. 设置页 / 关于我们页**
- `minprogram/pages/settings/settings.js`
- `minprogram/pages/settings/settings.wxml`
- `minprogram/pages/settings/settings.wxss`
- `minprogram/pages/about/about.js`
- `minprogram/pages/about/about.wxml`
- `minprogram/pages/about/about.wxss`

检查项：
- 缓存信息读取正常
- 清缓存正常
- 关于我们页可打开
- 返回逻辑正常

**8. 页面配置**
- `minprogram/app.json`
- `minprogram/pages/**/xxx.json`

检查项：
- 页面注册正常
- tabBar 正常
- 跳转路径正确
- 不出现“页面不存在”

**9. 接口统一性**
- `minprogram/utils/request.js`
- `minprogram/utils/config.js`
- `backend/app/main.py`
- `backend/app/api/products.py`
- `backend/app/api/auth.py`

检查项：
- 请求基地址正确
- 返回结构一致
- 错误提示统一
- 路由挂载正常

### Day 2：购物车和下单链路
- 加入购物车
- 修改数量
- 删除商品
- 购物车为空提示
- 选地址结算
- 下单成功
- 下单失败提示正常

#### Day 2 文件级清单

**1. 购物车页面**
- `minprogram/pages/cart/cart.js`
- `minprogram/pages/cart/cart.wxml`
- `minprogram/pages/cart/cart.wxss`
- `backend/app/api/cart.py`

检查项：
- 购物车列表正常加载
- 数量增减正常
- 删除商品正常
- 空购物车提示正常

**2. 结算页面**
- `minprogram/pages/checkout/checkout.js`
- `minprogram/pages/checkout/checkout.wxml`
- `minprogram/pages/checkout/checkout.wxss`
- `backend/app/api/orders.py`
- `backend/app/api/addresses.py`

检查项：
- 地址可选择
- 金额展示正确
- 提交订单正常
- 下单失败提示明确

**3. 下单接口**
- `backend/app/api/orders.py`
- `backend/app/database/models.py`

检查项：
- 地址归属校验正常
- 库存校验正常
- 订单项写入正常
- 购物车清理逻辑正常

**4. 购物车与结算联动**
- `minprogram/pages/products/products.js`
- `minprogram/pages/product-detail/product-detail.js`
- `minprogram/pages/cart/cart.js`

检查项：
- 商品页加购后能进购物车
- 结算后能进入订单页
- 数据刷新正常

### Day 3：订单状态流转
- 订单列表
- 订单详情
- 模拟支付
- 取消订单
- 确认收货
- 状态流转校验

#### Day 3 文件级清单

**1. 订单列表页**
- `minprogram/pages/orders/orders.js`
- `minprogram/pages/orders/orders.wxml`
- `minprogram/pages/orders/orders.wxss`
- `backend/app/api/orders.py`

检查项：
- 列表可加载
- 状态展示正确
- 跳转详情正常

**2. 订单详情页**
- `minprogram/pages/order-detail/order-detail.js`
- `minprogram/pages/order-detail/order-detail.wxml`
- `minprogram/pages/order-detail/order-detail.wxss`
- `backend/app/api/orders.py`

检查项：
- 订单信息正常展示
- 商品明细正常展示
- 地址信息正常展示
- 空态 / 异常态有提示

**3. 支付与状态流转**
- `backend/app/api/payments.py`
- `backend/app/api/orders.py`
- `minprogram/pages/order-detail/order-detail.js`

检查项：
- 模拟支付可用
- 支付后状态更新正确
- 已支付不能重复支付
- 取消订单正常
- 确认收货正常

### Day 4：数据稳定性和容错
- 脏购物车数据容错
- `product_id` 空值处理
- `quantity <= 0` 处理
- 商品不存在处理
- 地址不存在处理
- 库存不足处理
- 订单创建异常回滚

#### Day 4 文件级清单

**1. 下单容错**
- `backend/app/api/orders.py`
- `backend/app/database/models.py`

检查项：
- 空值不会炸
- 异常回滚正常
- 错误提示明确

**2. 购物车容错**
- `backend/app/api/cart.py`
- `minprogram/pages/cart/cart.js`

检查项：
- 脏数据不影响页面
- 无效数量可处理
- 无效商品可跳过

**3. 地址和商品容错**
- `backend/app/api/addresses.py`
- `backend/app/api/products.py`

检查项：
- 不存在地址提示正常
- 不存在商品提示正常
- 接口返回结构稳定

### Day 5：图片与资源上线准备
- 商品图片可访问
- 默认图 / 占位图准备
- 图片地址检查
- 小程序合法域名配置确认
- 上传接口或资源路径确认

#### Day 5 文件级清单

**1. 上传与资源**
- `backend/app/api/upload.py`
- `backend/app/core/config.py`
- `backend/app/main.py`

检查项：
- 上传接口可用
- 图片地址可访问
- 配置项正确加载

**2. 前端资源展示**
- `minprogram/pages/products/products.wxml`
- `minprogram/pages/product-detail/product-detail.wxml`
- `minprogram/pages/cart/cart.wxml`

检查项：
- 图片加载正常
- 占位图有效
- 图片失败不影响页面

**3. 域名与配置**
- `minprogram/utils/config.js`
- `minprogram/app.json`

检查项：
- API 域名配置正确
- 图片域名配置正确
- 路径拼接正常

### Day 6：后台 / 管理最小版
- 商品管理基础能力确认
- 订单管理基础能力确认
- 用户 / 地址数据可查
- 库存可观察
- 简单日志可追踪

#### Day 6 文件级清单

**1. 商品管理**
- `backend/app/api/products.py`
- `backend/app/database/models.py`

检查项：
- 商品增删改查正常
- 分类校验正常
- 库存字段正确

**2. 订单管理**
- `backend/app/api/orders.py`
- `backend/app/api/payments.py`

检查项：
- 订单列表可查
- 订单详情可查
- 订单状态可追踪

**3. 用户 / 地址 / 日志**
- `backend/app/api/users.py`
- `backend/app/api/addresses.py`
- `backend/backend.log`

检查项：
- 用户数据可查
- 地址数据可查
- 日志能追踪异常

### Day 7：全链路回归 + 发布准备
- 全链路回归测试
- 页面截图
- 演示说明整理
- 发布说明整理
- 已完成 / 待完善项标记
- 最终清单确认

#### Day 7 文件级清单

**1. 文档整理**
- `ecommerce/DEVELOPMENT_PLAN_STATUS.md`
- `ecommerce/7DAY_LAUNCH_PLAN.md`
- `ecommerce/PROJECT_SUMMARY.md`
- `ecommerce/PROJECT_LOG.md`

检查项：
- 状态标记清晰
- 发布说明完整
- 项目总结可读

**2. 全链路回归**
- `minprogram/pages/**`
- `backend/app/api/**`

检查项：
- 核心流程无阻塞
- 页面跳转正常
- 接口返回正常
- 最终演示顺畅

### Day 3：订单状态流转
- 订单列表
- 订单详情
- 模拟支付
- 取消订单
- 确认收货
- 状态流转校验

### Day 4：数据稳定性和容错
- 脏购物车数据容错
- `product_id` 空值处理
- `quantity <= 0` 处理
- 商品不存在处理
- 地址不存在处理
- 库存不足处理
- 订单创建异常回滚

### Day 5：图片与资源上线准备
- 商品图片可访问
- 默认图 / 占位图准备
- 图片地址检查
- 小程序合法域名配置确认
- 上传接口或资源路径确认

### Day 6：后台 / 管理最小版
- 商品管理基础能力确认
- 订单管理基础能力确认
- 用户 / 地址数据可查
- 库存可观察
- 简单日志可追踪

### Day 7：全链路回归 + 发布准备
- 全链路回归测试
- 页面截图
- 演示说明整理
- 发布说明整理
- 已完成 / 待完善项标记
- 最终清单确认

---

## 五、按正式使用标准需要重点确认的内容

- ⚠️ 支付流程是否真正闭环（当前以模拟支付为主）
- ⚠️ 图片上传是否已部署到公网
- ⚠️ 商家登录流程是否足够规范
- ⚠️ 地址 / 收藏 / 后台管理是否完整
- ⚠️ 订单、购物车、库存是否存在脏数据或并发问题
- ⚠️ 取消、支付、确认收货等状态流转是否足够严格

---

## 六、建议的下一步落地顺序

1. 先把主链路再验一遍：商品详情、搜索、收藏、设置页
2. 再补体验增强：分享、消息通知、优惠券
3. 然后补可选扩展：评价、真实支付
4. 最后做收尾整理：截图、演示说明、发布说明、最终验收

---

## 七、当前项目状态结论

项目已经具备核心交易闭环能力，属于：

- 核心功能已完成
- 体验功能大部分已完成
- 仍有少量扩展功能可继续完善
- 已进入 7 天冲刺收尾优化阶段
