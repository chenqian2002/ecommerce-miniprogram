# 微信订阅消息通知 - 实现指南

## 一、准备工作

### 1. 登录微信公众平台
- 地址：https://mp.weixin.qq.com
- 用小程序管理员微信扫码登录

### 2. 获取 AppID 和 AppSecret
- 左侧菜单 -> 开发管理 -> 开发设置
- 复制 AppID 和 AppSecret

### 3. 申请订阅消息模板
- 左侧菜单 -> 功能 -> 订阅消息
- 选用模板：订单发货提醒、订单支付成功通知、订单创建成功通知
- 记录模板ID

### 4. 配置后端 .env
```
WECHAT_APPID=你的AppID
WECHAT_APPSECRET=你的AppSecret
WECHAT_SUBSCRIBE_TEMPLATE_ID=订单发货提醒的模板ID
```

## 二、实现流程

### 前端流程
买家在结算页/商品详情页点击允许订阅
微信弹窗询问用户是否允许通知
用户允许后前端记录授权状态

### 后端流程
订单状态变更时（发货/支付等）
后端调用微信subscribeMessage.send接口
微信向买家推送订阅消息

## 三、前端代码示例

在结算页下单前调用：
```javascript
wx.requestSubscribeMessage({
  tmplIds: ['模板ID1', '模板ID2'],
  success(res) {
    console.log('订阅结果:', res);
  }
});
```

## 四、注意事项

1. 一次性订阅：用户每授权一次只能发一条消息
2. 长期订阅：仅对政务公共服务类小程序开放
3. 开发阶段：未配置AppID时代码会自动跳过发送
4. 测试账号：只有真实微信用户才能收到消息

## 五、上线检查

- [ ] 已获取AppID和AppSecret
- [ ] 已申请订阅消息模板
- [ ] 已在.env中配置
- [ ] 前端已添加requestSubscribeMessage
- [ ] 后端发货时能调用发送
- [ ] 真实微信用户测试收到通知