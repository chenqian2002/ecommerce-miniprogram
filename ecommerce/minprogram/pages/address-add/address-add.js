// pages/address-add/address-add.js
import { get, post, put } from '../../utils/request';

Page({
  data: {
    addressId: null,
    pageTitle: '新增收货地址',
    submitText: '保存地址',
    receiver_name: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    detail: '',
    is_default: false,
    submitting: false,
    loading: false
  },

  onLoad(options) {
    const addressId = options.addressId ? parseInt(options.addressId) : null;
    if (addressId) {
      this.setData({
        addressId,
        pageTitle: '编辑收货地址',
        submitText: '保存修改',
        loading: true
      });
      this.loadAddressDetail(addressId);
    }
  },

  loadAddressDetail(addressId) {
    get('/addresses')
      .then(res => {
        const addresses = Array.isArray(res) ? res : (res.data || []);
        const address = addresses.find(item => item.id === addressId);

        if (!address) {
          wx.showToast({ title: '地址不存在', icon: 'none' });
          this.setData({ loading: false });
          return;
        }

        this.setData({
          receiver_name: address.receiver_name || '',
          phone: address.phone || '',
          province: address.province || '',
          city: address.city || '',
          district: address.district || '',
          detail: address.detail || '',
          is_default: !!address.is_default,
          loading: false
        });
      })
      .catch(error => {
        console.error('Load address detail error:', error);
        this.setData({ loading: false });
        wx.showToast({ title: '加载地址失败', icon: 'none' });
      });
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ [field]: e.detail.value });
  },

  handleDefaultChange(e) {
    this.setData({ is_default: !!e.detail.value });
  },

  validateForm() {
    const { receiver_name, phone, province, city, district, detail } = this.data;

    if (!receiver_name.trim()) return '请填写收货人';
    if (!/^1\d{10}$/.test(phone.trim())) return '请输入正确的手机号';
    if (!province.trim() || !city.trim() || !district.trim()) return '请填写完整省市区';
    if (!detail.trim()) return '请填写详细地址';
    return '';
  },

  handleSubmit() {
    const { addressId, receiver_name, phone, province, city, district, detail, is_default, submitting } = this.data;

    if (submitting) return;

    const validationMessage = this.validateForm();
    if (validationMessage) {
      wx.showToast({ title: validationMessage, icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    const payload = {
      receiver_name: receiver_name.trim(),
      phone: phone.trim(),
      province: province.trim(),
      city: city.trim(),
      district: district.trim(),
      detail: detail.trim(),
      is_default
    };

    const action = addressId ? put(`/addresses/${addressId}`, payload) : post('/addresses', payload);

    action
      .then(() => {
        wx.showToast({ title: addressId ? '修改成功' : '新增成功', icon: 'success' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1200);
      })
      .catch(error => {
        console.error('Save address error:', error);
        wx.showToast({ title: error.message || error.detail || (addressId ? '修改失败' : '新增失败'), icon: 'none' });
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  },

  goBack() {
    wx.navigateBack();
  }
});